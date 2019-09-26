# -*- coding: utf-8 -*-
"""
***************************************************************************
    pavement.py
    ---------------------
    Date          : September 2019
    Copyright     : (C) 2016 Boundless, 2019 Planet Inc, https://planet.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Planet Federal'
__date__ = 'September 2019'
__copyright__ = '(C) 2019 Planet Inc, https://planet.com'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
import sys
import fnmatch
# import shutil
import zipfile
import subprocess
# import requests
import json
from collections import defaultdict

# this pulls in the sphinx target
# noinspection PyPackageRequirements
from paver.easy import *
# noinspection PyPackageRequirements
# from paver.doctools import html


options(
    plugin=Bunch(
        name='milstd2525',
        source_dir=path('milstd2525'),
        package_dir=path('.'),
        ext_libs=path('milstd2525/extlibs'),
        ext_src=path('milstd2525/ext-src'),
        tests=['test', 'tests'],
        excludes=[
            '*.pyc',
            '.git',
            '*.pro',
            '.DS_Store',
        ],
        # skip certain files inadvertently found by exclude pattern globbing
        skip_exclude=[]
    ),

    sphinx=Bunch(
        docroot=path('docs'),
        sourcedir=path('docs/source'),
        builddir=path('docs/build')
    )

)


# noinspection PyUnusedLocal
@task
@cmdopts([
    ('clean', 'c', 'clean out dependencies first'),
])
def setup():
    # noinspection PyBroadException
    clean = getattr(options, 'clean', False)
    ext_libs = options.plugin.ext_libs
    ext_src = options.plugin.ext_src
    if clean:
        ext_libs.rmtree()
    ext_libs.makedirs()
    runtime, test = read_requirements()
    os.environ['PYTHONPATH'] = ext_libs.abspath()
    for req in runtime + test:
        # sh('python3 -m pip install -U --install-option="--prefix=" '
        #    '-t %(ext_libs)s %(dep)s' % {
        #     'ext_libs': ext_libs.abspath(),
        #     'dep': req
        # }, env=os.environ)
        try:
            ret = subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--upgrade',
                 '--no-deps', '-t', f'{ext_libs.abspath()}', req])
        except subprocess.CalledProcessError:
            error(f"Error installing {req} with pip.")
            sys.exit(1)


# noinspection PyShadowingNames
@task
def install(options):
    """install plugin to qgis"""
    if options.sphinx.docroot.exists():
        builddocs(options)
    plugin_name = options.plugin.name
    src = path(__file__).dirname() / plugin_name
    if os.name == 'nt':
        default_profile_plugins = \
            "~/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins"
    elif sys.platform == 'darwin':
        default_profile_plugins = \
            "~/Library/Application Support/QGIS/QGIS3" \
            "/profiles/default/python/plugins"
    else:
        default_profile_plugins = \
            "~/.local/share/QGIS/QGIS3/profiles/default/python/plugins"

    dst_plugins = path(default_profile_plugins).expanduser()
    if not dst_plugins.exists():
        os.makedirs(dst_plugins, exist_ok=True)
    dst = dst_plugins / plugin_name
    src = src.abspath()
    dst = dst.abspath()
    if not hasattr(os, 'symlink'):
        dst.rmtree()
        src.copytree(dst)
    elif not dst.exists():
        src.symlink(dst)
        if options.sphinx.docroot.exists():
            # Symlink the docs build folder to the parent
            docs = path('..') / '..' / "docs" / 'build' / 'html'
            docs_dest = path(__file__).dirname() / plugin_name / "docs"
            docs_link = docs_dest / 'html'
            if not docs_dest.exists():
                docs_dest.mkdir()
            if not docs_link.islink():
                docs.symlink(docs_link)


def read_requirements():
    """Return a list of runtime and list of test requirements"""
    lines = open('requirements.txt').readlines()
    lines = [l for l in [l.strip() for l in lines] if l]
    divider = '# test requirements'

    try:
        idx = lines.index(divider)
    except ValueError:
        raise BuildFailure(
            'Expected to find "%s" in requirements.txt' % divider)

    not_comments = lambda s, e: [l for l in lines[s:e] if l[0] != '#']
    return not_comments(0, idx), not_comments(idx + 1, None)


# noinspection PyShadowingNames
@task
@cmdopts([
    ('tests', 't', 'Package tests with plugin'),
])
def package(options):
    """Create plugin package"""
    if options.sphinx.docroot.exists():
        builddocs(options)
    package_file = options.plugin.package_dir / \
        ('%s.zip' % options.plugin.name)
    if os.path.exists(package_file):
        os.remove(package_file)
    with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if not hasattr(options.package, 'tests'):
            options.plugin.excludes.extend(options.plugin.tests)
        _make_zip(zf, options)
    return package_file


# noinspection PyShadowingNames
def _make_zip(zipfile, options):
    excludes = set(options.plugin.excludes)
    skips = options.plugin.skip_exclude

    src_dir = options.plugin.source_dir
    # noinspection PyShadowingNames
    exclude = lambda p: any([fnmatch.fnmatch(p, e) for e in excludes])

    # noinspection PyShadowingNames
    def filter_excludes(root, items):
        if not items:
            return []
        # to prevent descending into dirs, modify the list in place
        for item in list(items):  # copy list or iteration values change
            itempath = path(os.path.relpath(root)) / item
            if exclude(item) and item not in skips:
                debug('Excluding %s' % itempath)
                items.remove(item)
        return items

    for root, dirs, files in os.walk(src_dir):
        for f in filter_excludes(root, files):
            relpath = os.path.relpath(root)
            zipfile.write(path(root) / f, path(relpath) / f)
        filter_excludes(root, dirs)

    for root, dirs, files in os.walk(options.sphinx.builddir):
        for f in files:
            relpath = os.path.join(
                options.plugin.name, "docs",
                os.path.relpath(root, options.sphinx.builddir))
            zipfile.write(path(root) / f, path(relpath) / f)


# noinspection PyShadowingNames
def create_settings_docs(options):
    settings_file = path(options.plugin.name) / "settings.json"
    doc_file = options.sphinx.sourcedir / "settingsconf.rst"
    # noinspection PyBroadException
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except:
        return
    grouped = defaultdict(list)
    for setting in settings:
        grouped[setting["group"]].append(setting)
    with open(doc_file, "w") as f:
        f.write(".. _plugin_settings:\n\n"
                "Plugin settings\n===============\n\n"
                "The plugin can be adjusted using the following settings, "
                "to be found in its settings dialog (|path_to_settings|).\n")
        for groupName, group in grouped.items():
            section_marks = "-" * len(groupName)
            f.write("\n%s\n%s\n\n"
                    ".. list-table::\n"
                    "   :header-rows: 1\n"
                    "   :stub-columns: 1\n"
                    "   :widths: 20 80\n"
                    "   :class: non-responsive\n\n"
                    "   * - Option\n"
                    "     - Description\n"
                    % (groupName, section_marks))
            for setting in group:
                f.write("   * - %s\n"
                        "     - %s\n"
                        % (setting["label"], setting["description"]))


# noinspection PyShadowingNames
@task
@cmdopts([
    ('clean', 'c', 'clean out built artifacts first'),
    ('sphinx_theme=', 's', 'Sphinx theme to use in documentation'),
])
def builddocs(options):
    # noinspection PyBroadException
    try:
        # May fail if not in a git repo
        sh("git submodule init")
        sh("git submodule update")
    except:
        pass
    create_settings_docs(options)
    if getattr(options, 'clean', False):
        options.sphinx.builddir.rmtree()
    if getattr(options, 'sphinx_theme', False):
        # overrides default theme by the one provided in command line
        set_theme = "-D html_theme='{}'".format(options.sphinx_theme)
    else:
        # Uses default theme defined in conf.py
        set_theme = ""
    sh("sphinx-build -a {} {} {}/html".format(set_theme,
                                              options.sphinx.sourcedir,
                                              options.sphinx.builddir))


@task
def install_devtools():
    """Install development tools"""
    # noinspection PyBroadException
    try:
        # noinspection PyPackageRequirements
        import pip
    except:
        error('FATAL: Unable to import pip, please install it first!')
        sys.exit(1)

    pip.main(['install', '-r', 'requirements-dev.txt'])


# noinspection PyPackageRequirements
@task
@consume_args
def pep8(args):
    """Check code for PEP8 violations"""
    # noinspection PyBroadException
    try:
        import pep8
    except:
        error('pep8 not found! Run "paver install_devtools".')
        sys.exit(1)

    # Errors to ignore
    ignore = ['E203', 'E121', 'E122', 'E123', 'E124', 'E125', 'E126', 'E127',
              'E128', 'E402']
    styleguide = pep8.StyleGuide(ignore=ignore,
                                 exclude=['*/extlibs/*', '*/ext-src/*'],
                                 repeat=True, max_line_length=79,
                                 parse_argv=args)
    styleguide.input_dir(options.plugin.source_dir)
    info('===== PEP8 SUMMARY =====')
    styleguide.options.report.print_statistics()


# noinspection PyPackageRequirements
@task
@consume_args
def autopep8(args):
    """Format code according to PEP8"""
    # noinspection PyBroadException
    try:
        import autopep8
    except:
        error('autopep8 not found! Run "paver install_devtools".')
        sys.exit(1)

    if any(x not in args for x in ['-i', '--in-place']):
        args.append('-i')

    args.append('--ignore=E261,E265,E402,E501')
    args.insert(0, 'dummy')

    cmd_args = autopep8.parse_args(args)

    excludes = ('ext-lib', 'ext-src')
    for p in options.plugin.source_dir.walk():
        if any(exclude in p for exclude in excludes):
            continue

        if p.fnmatch('*.py'):
            autopep8.fix_file(p, options=cmd_args)


# noinspection PyPackageRequirements
@task
@consume_args
def pylint(args):
    """Check code for errors and coding standard violations"""
    # noinspection PyBroadException
    try:
        from pylint import lint
    except:
        error('pylint not found! Run "paver install_devtools".')
        sys.exit(1)

    if 'rcfile' not in args:
        rcfile = options.plugin.source_dir / 'tests' / 'pylintrc'
        if rcfile.exists():
            args.append('--rcfile={0}'.format(rcfile))

    args.append(options.plugin.source_dir)
    lint.Run(args)
