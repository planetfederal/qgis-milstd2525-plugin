# -*- coding: utf-8 -*-

"""
***************************************************************************
    renderer.py
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
from __future__ import absolute_import

__author__ = 'Victor Olaya'
__date__ = 'December 2015'
__copyright__ = '(C) 2015-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt import uic

try:
    from qgis.core import  QGis
except ImportError:
    from qgis.core import  Qgis as QGis

if QGis.QGIS_VERSION_INT < 29900:
    from qgis.core import QgsFeatureRendererV2, QgsRendererV2AbstractMetadata, QgsMarkerSymbolV2, QgsSymbolV2, QGis
    from qgis.gui import QgsRendererV2Widget, QgsFieldProxyModel
else:
    from qgis.core import QgsFeatureRenderer as QgsFeatureRendererV2
    from qgis.core import QgsRendererAbstractMetadata as QgsRendererV2AbstractMetadata
    from qgis.core import QgsMarkerSymbol as QgsMarkerSymbolV2
    from qgis.core import QgsSymbol as QgsSymbolV2
    from qgis.gui import QgsRendererWidget as QgsRendererV2Widget

from qgis.gui import QgsFieldProxyModel

from milstd2525.milstd2525symbology import symbolForCode, getDefaultSymbol


pluginPath = os.path.dirname(__file__)

WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525rendererwidgetbase.ui'))


class MilStd2525Renderer(QgsFeatureRendererV2):
    def __init__(self, size=40, field=''):
        QgsFeatureRendererV2.__init__(self, 'MilStd2525Renderer')
        self.field = field
        self.size = size
        self._defaultSymbol = getDefaultSymbol(size)
        self.cached = {}

    def symbolForFeature(self, feature, context):
        idx = feature.fieldNameIndex(self.field)
        if idx != -1:
            code = feature.attributes()[idx]
            if code not in self.cached:
                symbol = symbolForCode(code, self.size)
                if symbol is None:
                    self._defaultSymbol.setSize(self.size)
                    self.cached[code] = self._defaultSymbol
                else:
                    self.cached[code] = symbol.clone()
                    self.cached[code].startRender(self.context)
            self.cached[code].setSize(self.size)
            return self.cached[code]
        else:
            return self._defaultSymbol

    def startRender(self, context, fields):
        self.context = context
        for k,v in self.cached.items():
            v.startRender(context)
        self._defaultSymbol.startRender(context)

    def stopRender(self, context):
        for s in list(self.cached.values()):
            s.stopRender(context)
        self._defaultSymbol.stopRender(context)

    def usedAttributes(self):
        return [self.field]

    def symbols(self, context):
        return list(self.cached.values())

    def clone(self):
        r = MilStd2525Renderer(self.size, self.field)
        r.cached = self.cached
        return r

    def save(self, doc):
        elem = doc.createElement('renderer-v2')
        elem.setAttribute('type', 'MilStd2525Renderer')
        elem.setAttribute('size', self.size)
        elem.setAttribute('field', self.field)
        return elem


class MilStd2525RendererWidget(QgsRendererV2Widget, WIDGET):
    def __init__(self, layer, style, renderer):
        super(MilStd2525RendererWidget, self).__init__(layer, style)
        self.setupUi(self)

        if renderer is None or renderer.type() != 'MilStd2525Renderer':
            fields = [f.name() for f in layer.dataProvider().fields()]
            self.r = MilStd2525Renderer(field = fields[0])
        else:
            self.r = renderer.clone()

        self.cmbField.setLayer(layer)
        self.cmbField.setFilters(QgsFieldProxyModel.String)

        self.spnSize.setValue(self.r.size)

        self.cmbField.fieldChanged.connect(self.fieldChanged)
        self.spnSize.valueChanged[float].connect(self.sizeChanged)

    def sizeChanged(self, value):
        self.r.size = value

    def fieldChanged(self):
        self.r.field = self.cmbField.currentText()

    def renderer(self):
        return self.r


class MilStd2525RendererMetadata(QgsRendererV2AbstractMetadata):
    def __init__(self):
        QgsRendererV2AbstractMetadata.__init__(
            self, 'MilStd2525Renderer', 'MIL-STD-2525 renderer')

    def createRenderer(self, element):
        return MilStd2525Renderer(int(element.attribute('size')), element.attribute('field'))

    def createRendererWidget(self, layer, style, renderer):
        return MilStd2525RendererWidget(layer, style, renderer)
