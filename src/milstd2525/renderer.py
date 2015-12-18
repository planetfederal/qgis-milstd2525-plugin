import os
# -*- coding: utf-8 -*-

from PyQt4 import uic

from qgis.core import QgsFeatureRendererV2, QgsRendererV2AbstractMetadata
from qgis.gui import QgsRendererV2Widget, QgsFieldProxyModel

from milstd2525 import symbolForCode, getDefaultSymbol


pluginPath = os.path.dirname(__file__)

WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525rendererwidgetbase.ui'))


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

    def clone(self):
        return MilStd2525Renderer(self.size, self.field, self.fields)

    def dump(self):
        return 'MILSTD2525'


class MilStd2525RendererWidget(QgsRendererV2Widget, WIDGET):
    def __init__(self, layer, style, renderer):
        super(MilStd2525RendererWidget, self).__init__(layer, style)
        self.setupUi(self)

        if renderer is None or renderer.type() != 'MilStd2525Renderer':
            fields = [f.name() for f in layer.dataProvider().fields()]
            self.r = MilStd2525Renderer(field = fields[0], fields = fields)
        else:
            self.r = renderer

        self.cmbField.setLayer(layer)
        self.cmbField.setFilters(QgsFieldProxyModel.String)

        self.spnSize.setValue(self.r.size)

        self.cmbField.fieldChanged.connect(self.fieldChanged)
        self.spnSize.valueChanged[float].connect(self.sizeChanged)

    def sizeChanged(self, value):
        self.r.size = value

    def fieldChanged(self):
        self.r.field = self.combo.currentText()

    def renderer(self):
        return self.r


class MilStd2525RendererMetadata(QgsRendererV2AbstractMetadata):
    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(
            self, 'MilStd2525Renderer', 'MIL-STD-2525 renderer')

    def createRenderer(self, element):
        return MilStd2525Renderer()

    def createRendererWidget(self, layer, style, renderer):
        return MilStd2525RendererWidget(layer, style, renderer)
