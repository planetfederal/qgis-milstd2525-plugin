# -*- coding: utf-8 -*-

import os

from PyQt4.QtGui import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout

from qgis.core import NULL
from qgis.gui import QgsEditorWidgetWrapper, QgsEditorConfigWidget, QgsEditorWidgetFactory

from sidcdialog import SIDCDialog
from milstd2525 import symbolForCode

class SIDCWidgetWrapper(QgsEditorWidgetWrapper):

    def __init__(self, vl, fieldIdx, editor, parent):
        self.widget = None
        super(SIDCWidgetWrapper, self).__init__(vl, fieldIdx, editor, parent)

    def value( self ):
        if self.widget.edit.text() == u"NULL":
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
        self.widget.hbox.addWidget(self.widget.edit)
        self.widget.hbox.addWidget(self.widget.button)
        self.widget.setLayout(self.widget.hbox)
        return self.widget

    def initWidget(self, editor):
        self.widget = editor

    def valid(self):
        return True



class SIDCWidgetWrapperConfig(QgsEditorConfigWidget):
    def __init__(self, layer, idx, parent):
        QgsEditorConfigWidget.__init__(self, layer, idx, parent)
        self.setLayout(QHBoxLayout())
        label = QLabel("This edit widget allows entering SDIC codes and get a preview of the corresponding icon")
        self.layout().addWidget(label)

    def config( self ):
        return {}

    def setConfig( self, config ):
        pass


class SIDCWidgetWrapperFactory(QgsEditorWidgetFactory):
    def __init__(self):
        QgsEditorWidgetFactory.__init__(self, "SDIC code editor")

    def create(self, layer, fieldIdx, editor, parent):
        self.wrapper =  SIDCWidgetWrapper(layer, fieldIdx, editor, parent)
        return self.wrapper

    def configWidget(self, layer, idx, parent ):
        self._configWidget = SIDCWidgetWrapperConfig(layer, idx, parent)
        return self._configWidget
