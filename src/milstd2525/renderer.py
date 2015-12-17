from PyQt4.QtGui import QComboBox, QLabel, QHBoxLayout, QSpinBox, QVBoxLayout

from qgis.core import QgsFeatureRendererV2, QgsRendererV2AbstractMetadata
from qgis.gui import QgsRendererV2Widget

from milstd2525 import symbolForCode, getDefaultSymbol


class MilStd2525Renderer(QgsFeatureRendererV2):
    def __init__(self, size=40, field='', fields=[]):
        QgsFeatureRendererV2.__init__(self, 'MilStd2525Renderer')
        self.field = field
        self.fields = fields
        self.size = size
        self.cachedSymbols = {}

    def symbolForFeature(self, feature):
        idx = feature.fieldNameIndex(self.field)
        if idx != -1:
            code = feature.attributes()[idx]
            if code in self.cachedSymbols:
                return self.cachedSymbols[code]
            symbol = symbolForCode(code, self.size) or getDefaultSymbol(self.size)
            self.cachedSymbols[code] = symbol
            return symbol
        else:
            return getDefaultSymbol(self.size)

    def startRender(self, context, vlayer):
        for s in self.cachedSymbols.values():
            s.startRender(context)

    def stopRender(self, context):
        for s in self.cachedSymbols.values():
            s.stopRender(context)

    def usedAttributes(self):
        return self.fields

    def symbols2(self, context):
        return self.cachedSymbols.values()

    def dump(self):
        return "MILSTD2525"

    def clone(self):
        return MilStd2525Renderer(self.size, self.field, self.fields)

    def dump(self):
        return 'MILSTD2525'


class MilStd2525RendererWidget(QgsRendererV2Widget):
    def __init__(self, layer, style, renderer):
        QgsRendererV2Widget.__init__(self, layer, style)

        if renderer is None or renderer.type() != 'MilStd2525Renderer':
            fields = [f.name() for f in layer.dataProvider().fields()]
            self.r = MilStd2525Renderer(field = fields[0], fields = fields)
        else:
            self.r = renderer
        self.combo = QtGui.QComboBox()
        for f in layer.dataProvider().fields():
            self.combo.addItem(f.name(), f.name())
        idx =  max(0, layer.dataProvider().fieldNameIndex(self.r.field))
        self.combo.setCurrentIndex(idx)
        self.combo.currentIndexChanged.connect(self.fieldChanged)
        self.labelField = QtGui.QLabel('SIDC code field')
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.labelField)
        self.hbox.addWidget(self.combo)
        self.spinSize = QtGui.QSpinBox()
        self.spinSize.setValue(self.r.size)
        self.spinSize.valueChanged.connect(self.sizeChanged)
        self.labelSize = QtGui.QLabel('Size (pixels)')
        self.hbox2 = QtGui.QHBoxLayout()
        self.hbox2.addWidget(self.labelSize)
        self.hbox2.addWidget(self.spinSize)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.hbox2)
        self.setLayout(self.vbox)

    def sizeChanged(self, value):
        self.r.size = value

    def fieldChanged(self):
        self.r.field = self.combo.currentText()

    def renderer(self):
        return self.r


class MilStd2525RendererMetadata(QgsRendererV2AbstractMetadata):
    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(self, 'MilStd2525Renderer', 'MIL-STD-2525 renderer')

    def createRenderer(self, element):
        return MilStd2525Renderer()

    def createRendererWidget(self, layer, style, renderer):
        return MilStd2525RendererWidget(layer, style, renderer)
