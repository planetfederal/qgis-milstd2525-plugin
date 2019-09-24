# -*- coding: utf-8 -*-

"""
***************************************************************************
    milstd2525symbology.py
    ---------------------
    Date                 : December 2015
    Copyright            : (C) 2015-2016, 2018 Boundless, 2019 Planet Inc.
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import range

__author__ = 'Planet Federal'
__date__ = 'September 2019'
__copyright__ = '(C) 2015-2016, 2018 Boundless, ' \
                '2019 Planet Inc, https://planet.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import fnmatch

from qgis.core import  Qgis
from qgis.core import QgsMarkerSymbol
from qgis.core import QgsSvgMarkerSymbolLayer


def symbolForCode(code, size):
    try:
        symbol = QgsMarkerSymbol()
        for i in range(symbol.symbolLayerCount()):
            symbol.takeSymbolLayer(0)

        echelonCode = code[3] + code[8:10]
        echelonLayer = getSymbolLayer('Echelon', echelonCode, size)
        if echelonLayer is not None:
            symbol.insertSymbolLayer(0, echelonLayer)
        #print 'echelon: %s %s' % (echelonCode, str(echelonLayer is not None))

        amplifierCode = code[3] + code[8:10]
        amplifierLayer = getSymbolLayer('Amplifier', amplifierCode, size)
        if amplifierLayer is not None:
            symbol.insertSymbolLayer(0, amplifierLayer)
        #print 'amplifier: %s %s' % (amplifierCode, str(amplifierLayer is not None))

        hqtffdCode = code[3:6] + code[7]
        hqtffdLayer = getSymbolLayer('HQTFFD', hqtffdCode, size)
        if hqtffdLayer is not None:
            symbol.insertSymbolLayer(0, hqtffdLayer)
        #print 'hqtffd: %s %s' % (hqtffdCode, str(hqtffdLayer is not None))

        ocaCode = code[2:7] + '2'
        ocaLayer = getSymbolLayer('OCA', ocaCode, size)
        if ocaLayer is not None:
            symbol.insertSymbolLayer(0, ocaLayer)
        #print 'oca: %s %s' % (ocaCode, str(ocaLayer is not None))

        mainCode = code[4:6] + code[10:16]
        mainLayer = getSymbolLayer('Appendices', mainCode, size)
        if mainLayer is not None:
            symbol.insertSymbolLayer(0, mainLayer)
        #print 'main: %s %s' % (mainCode, str(mainLayer is not None))

        modifier1Code = code[4:6] + code[16:18] + '1'
        modifier1Layer = getSymbolLayer('Appendices', modifier1Code, size)
        if modifier1Layer is not None:
            symbol.insertSymbolLayer(0, modifier1Layer)

        modifier2Code = code[4:6] + code[18:20] + '2'
        modifier2Layer = getSymbolLayer('Appendices', modifier2Code, size)
        if modifier2Layer is not None:
            symbol.insertSymbolLayer(0, modifier2Layer)

        frameCode = '%s_%s_%s' % (code[2], code[3:6], code[0])
        frameLayer = getSymbolLayer('Frames', frameCode, size)
        if frameLayer is not None:
            symbol.insertSymbolLayer(0, frameLayer)
        #print 'frame: %s %s' % (frameCode, str(frameLayer is not None))

        if symbol.symbolLayerCount() == 0:
            symbol = None
    except Exception as e:
        symbol = None

    return symbol


def getSymbolLayer(folder, svg, size):
    svg = svg + '.svg'
    root = os.path.join(os.path.dirname(__file__), 'svg', folder)
    filepath = None
    for base, dirs, files in os.walk(root):
        matching = fnmatch.filter(files, svg)
        if matching:
            filepath = os.path.join(base, matching[0])
            break
    if filepath is not None:
        symbolLayer = QgsSvgMarkerSymbolLayer(filepath)
        symbolLayer.setSizeUnit(3)
        symbolLayer.setSize(size)
        return symbolLayer
    else:
        return None


def getDefaultSymbol(size):
    symbol = QgsMarkerSymbol()
    symbolLayer = QgsSvgMarkerSymbolLayer(
        os.path.join(os.path.dirname(__file__), 'svg', 'question.svg'))
    symbolLayer.setSizeUnit(3)
    symbolLayer.setSize(size)
    symbol.insertSymbolLayer(0, symbolLayer)
    return symbol
