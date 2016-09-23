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

__author__ = 'Victor Olaya'
__date__ = 'December 2015'
__copyright__ = '(C) 2015-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4 import QtGui, QtCore
from qgis.core import QgsRendererV2Registry, QgsApplication
from qgis.gui import QgsEditorWidgetRegistry

from renderer import MilStd2525RendererMetadata
from sidcwidgetwrapper import SIDCWidgetWrapperFactory

import webbrowser

class MilStd2525Plugin:
    def __init__(self, iface):
        self.iface = iface
        try:
            from .tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, 'MIL-STD-2525')
        except:
            pass

        self._rendererMetadata = MilStd2525RendererMetadata()
        self._widgetWrapperFactory = SIDCWidgetWrapperFactory()

        QgsRendererV2Registry.instance().addRenderer(self._rendererMetadata)
        QgsEditorWidgetRegistry.instance().registerWidget('SIDC code editor', self._widgetWrapperFactory)

    def initGui(self):
        helpIcon = QgsApplication.getThemeIcon('/mActionHelpAPI.png')
        self.helpAction = QtGui.QAction(helpIcon, "MIL-STD-2525 Help", self.iface.mainWindow())
        self.helpAction.setObjectName("milstd2525Help")
        self.helpAction.triggered.connect(lambda: webbrowser.open_new("file://" + os.path.join(os.path.dirname(__file__), "docs", "html", "index.html")))
        self.iface.addPluginToMenu("MIL-STD-2525", self.helpAction)        

    def unload(self):
        QgsRendererV2Registry.instance().removeRenderer('MilStd2525Renderer')

        try:
            from milstd2525.tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, 'MIL-STD-2525')
        except:
            pass
