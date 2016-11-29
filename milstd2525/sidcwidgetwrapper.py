# -*- coding: utf-8 -*-

"""
***************************************************************************
    sidcwidgetwrapper.py
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

import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout

from qgis.core import NULL
from qgis.gui import QgsEditorWidgetWrapper, QgsEditorConfigWidget, QgsEditorWidgetFactory

from milstd2525.sidcdialog import SIDCDialog
from milstd2525.milstd2525symbology import symbolForCode


pluginPath = os.path.dirname(__file__)

CONFIG_WIDGET, CONFIG_BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525configwidgetbase.ui'))


class SIDCWidgetWrapper(QgsEditorWidgetWrapper):
    def __init__(self, vl, fieldIdx, editor, parent):
        self.widget = None
        super(SIDCWidgetWrapper, self).__init__(vl, fieldIdx, editor, parent)

    def value( self ):
        if self.widget.edit.text() == 'NULL':
            return NULL
        else:
            return self.widget.edit.text()

    def setValue(self, value):
        if value == NULL:
            self.widget.edit.setText('NULL')
        else:
            self.widget.edit.setText(value)

    def createWidget(self, parent):
        self.widget = QWidget(parent)
        self.widget.edit = QLineEdit()
        self.widget.button = QPushButton()
        self.widget.button.setText("...")
        def showDialog():
            dialog = SIDCDialog(self.widget.edit.text())
            dialog.exec_()
            if dialog.newCode is not None:
                self.widget.edit.setText(dialog.newCode)
        self.widget.button.clicked.connect(showDialog)
        self.widget.hbox = QHBoxLayout()
        self.widget.hbox.setMargin(0)
        self.widget.hbox.setSpacing(0)
        self.widget.hbox.addWidget(self.widget.edit)
        self.widget.hbox.addWidget(self.widget.button)
        self.widget.setLayout(self.widget.hbox)
        return self.widget

    def initWidget(self, editor):
        self.widget = editor

    def valid(self):
        return True


class SIDCWidgetWrapperConfig(QgsEditorConfigWidget, CONFIG_WIDGET):
    def __init__(self, layer, idx, parent):
        super(SIDCWidgetWrapperConfig, self).__init__(layer, idx, parent)
        self.setupUi(self)

    def config( self ):
        return {}

    def setConfig( self, config ):
        pass


class SIDCWidgetWrapperFactory(QgsEditorWidgetFactory):
    def __init__(self):
        QgsEditorWidgetFactory.__init__(self, 'SIDC code editor')

    def create(self, layer, fieldIdx, editor, parent):
        self.wrapper =  SIDCWidgetWrapper(layer, fieldIdx, editor, parent)
        return self.wrapper

    def configWidget(self, layer, idx, parent ):
        self._configWidget = SIDCWidgetWrapperConfig(layer, idx, parent)
        return self._configWidget
