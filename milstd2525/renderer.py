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

__author__ = 'Victor Olaya'
__date__ = 'December 2015'
__copyright__ = '(C) 2015-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from PyQt4 import uic

from qgis.core import QgsFeatureRendererV2, QgsRendererV2AbstractMetadata, QgsMarkerSymbolV2, QgsSymbolV2, QGis
from qgis.gui import QgsRendererV2Widget, QgsFieldProxyModel

from milstd2525 import symbolForCode, getDefaultSymbol


pluginPath = os.path.dirname(__file__)

WIDGET, BASE = uic.loadUiType(
    os.path.join(pluginPath, 'ui', 'milstd2525rendererwidgetbase.ui'))


class MilStd2525Renderer(QgsFeatureRendererV2):
    def __init__(self, size=40, field=''):
        QgsFeatureRendererV2.__init__(self, 'MilStd2525Renderer')
        self.field = field
        self.size = size
        self._defaultSymbol = getDefaultSymbol(size)
        self._symbol = QgsMarkerSymbolV2()
        self.cached = {}
        self.started = set()

    def symbolForFeature(self, feature):
        idx = feature.fieldNameIndex(self.field)
        if idx != -1:
            code = feature.attributes()[idx]
            if code in self.cached and code in self.started:
                return self.cached[code]
            ret = symbolForCode(code, self.size, self._symbol)
            if ret is None:
                self.cached[code] = self._defaultSymbol
                return self._defaultSymbol
            else:
                self.cached[code] = self._symbol.clone()
                return self._symbol

        else:
            return self._defaultSymbol

    def startRender(self, context, fields):
        print self.cached
        for k,v in self.cached.iteritems():
            v.startRender(context)
            self.started.add(k)
        self._symbol.startRender(context)
        self._defaultSymbol.startRender(context)

    def stopRender(self, context):
        for s in self.cached.values():
            s.stopRender(context)
        self._symbol.stopRender(context)
        self._defaultSymbol.stopRender(context)

    def usedAttributes(self):
        return [self.field]

    def symbols(self, context):
        return [self._symbol, self._defaultSymbol]

    def clone(self):
        r = MilStd2525Renderer(self.size, self.field)
        r.cached = self.cached
        r.started = self.started
        return r

    def dump(self):
        return 'MILSTD2525'

    def save(self, doc):
        elem = doc.createElement('renderer-v2')
        elem.setAttribute('type', 'MILSTD2525')
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
