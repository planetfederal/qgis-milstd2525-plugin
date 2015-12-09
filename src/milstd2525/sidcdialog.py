from PyQt4 import QtGui, uic
import os
from milstd2525 import symbolForCode
from qgis.gui import *
from qgis.core import NULL

class SIDCWidgetWrapper(QgsEditorWidgetWrapper):
    def value( self ):
        if self.edit.text() == u"NULL":
            return NULL
        else:
            return self.edit.text()

    def setValue(self, value):
        if value == NULL:
            self.edit.setText('NULL')
        else:
            self.edit.setText(value)

    def createWidget(self, parent):
        widget = QtGui.QWidget()
        self.edit = QtGui.QLineEdit()
        button = QtGui.QPushButton()
        button.setText("...")
        def showDialog():
            dialog = SIDCDialog(self.edit.text())
            dialog.exec_()
            if dialog.newCode is not None:
                self.edit.setText(dialog.newCode)
        button.clicked.connect(showDialog)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.edit)
        hbox.addWidget(button)
        widget.setLayout(hbox)
        return widget

    def initWidget(self, editor):
        self.edit = editor


class SIDCWidgetWrapperConfig(QgsEditorConfigWidget):
    def __init__(self, layer, idx, parent):
        QgsEditorConfigWidget.__init__(self, layer, idx, parent)
        self.setLayout(QtGui.QHBoxLayout())
        label = QtGui.QLabel("This edit widget allows entering SDIC codes and get a preview of the corresponding icon")
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

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'sidcdialog.ui'))

class SIDCDialog(BASE, WIDGET):

    def __init__(self, code = ""):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.txtCode.textChanged.connect(self.textChanged)
        if code:
            self.txtCode.setText(code)
        self.newCode = None

    def textChanged(self):
        text = self.txtCode.text()
        symbol = symbolForCode(text, 100)
        if symbol:
            image = symbol.bigSymbolPreviewImage()
            self.labelImg.setPixmap(QtGui.QPixmap.fromImage(image))
        else:
            self.labelImg.setPixmap(QtGui.QPixmap())

    def accept(self):
        self.newCode = self.txtCode.text()
        self.close()


