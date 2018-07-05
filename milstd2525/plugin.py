# -*- coding: utf-8 -*-

"""
***************************************************************************
    plugin.py
    ---------------------
    Date                 : December 2015
    Copyright            : (C) 2015-2016 Boundless, http://boundlessgeo.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import object

__author__ = 'Victor Olaya'
__date__ = 'December 2015'
__copyright__ = '(C) 2015-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import webbrowser

from qgis.PyQt.QtWidgets import QAction

from qgis.core import  Qgis
from qgis.core import QgsApplication

from qgis.gui import QgsGui

from milstd2525.renderer import MilStd2525RendererMetadata
from milstd2525.sidcwidgetwrapper import SIDCWidgetWrapperFactory

from qgiscommons2.gui import (addAboutMenu,
                             removeAboutMenu,
                             addHelpMenu,
                             removeHelpMenu)

class MilStd2525Plugin(object):
    def __init__(self, iface):
        self.iface = iface
        try:
            from milstd2525.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, 'MIL-STD-2525')
        except:
            pass

        self._rendererMetadata = MilStd2525RendererMetadata()
        self._widgetWrapperFactory = SIDCWidgetWrapperFactory()

        QgsApplication.rendererRegistry().addRenderer(self._rendererMetadata)
        QgsGui.instance().editorWidgetRegistry().registerWidget('SIDC code editor', self._widgetWrapperFactory)

    def initGui(self):
        addHelpMenu("MIL-STD-2525", self.iface.addPluginToMenu)
        addAboutMenu("MIL-STD-2525", self.iface.addPluginToMenu)

        try:
            from lessons import addLessonsFolder, addGroup
            folder = os.path.join(os.path.dirname(__file__), "_lessons")
            addLessonsFolder(folder, "milstd2525")
        except:
            pass


    def unload(self):
        QgsRendererRegistry.instance().removeRenderer('MilStd2525Renderer')

        removeHelpMenu("MIL-STD-2525")
        removeAboutMenu("MIL-STD-2525")

        try:
            from milstd2525.tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, 'MIL-STD-2525')
        except:
            pass

        try:
            from lessons import removeLessonsFolder
            folder = os.path.join(pluginPath, '_lessons')
            removeLessonsFolder(folder)
        except:
            pass


