from builtins import str
# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

import os
import sys
import unittest
import tempfile
import shutil
import time
import hashlib

from qgis.PyQt.QtCore import QFileInfo
from qgis.core import QgsProject, Qgis
from qgis.utils import iface

from milstd2525.milstd2525symbology import symbolForCode, getDefaultSymbol
from milstd2525.renderer import MilStd2525Renderer

try:
    from qgistester.test import Test
except:
    pass


def _layerFromName(name):
    layers = list(QgsProject.instance().mapLayers().values())
    for layer in layers:
        if layer.name() == name:
            return layer


def functionalTests():
    try:
        from qgistester.test import Test
    except:
        return []

    def _openProject():
        projfile = os.path.join(os.path.dirname(__file__), "data", "project.qgs")
        iface.addProject(projfile)

    def _openLayerProperties():
        layer = _layerFromName("2525")
        iface.showLayerProperties(layer)

    def _openAttributesTable():
        layer = _layerFromName("2525")
        iface.showAttributeTable(layer)

    def _startEditing():
        layer = _layerFromName("2525")
        layer.startEditing()

    def _stopEditing():
        layer = _layerFromName("2525")
        layer.rollBack()
        iface.newProject()

    def _setRenderer():
        r = MilStd2525Renderer(40, "SDIC")
        layer = _layerFromName("2525")
        layer.setRenderer(r)
        layer.reload()
        layer.triggerRepaint()
        iface.mapCanvas().setExtent(layer.extent())

    def _changeSize():
        layer = _layerFromName("2525")
        r = layer.renderer()
        r.size = 80
        layer.triggerRepaint()
        iface.mapCanvas().setExtent(layer.extent())

    editWidgetTest = Test("Test code edit widget")
    editWidgetTest.addStep("Open project", _openProject)
    #editWidgetTest.addStep("Open layer properties", _openLayerProperties)
    editWidgetTest.addStep("Open layer properties, go to the 'Fields' tab  and set the edit widget of the SDIC field to 'SDIC code editor'", _openLayerProperties)
    editWidgetTest.addStep("Toggle editing", _startEditing)
    #editWidgetTest.addStep("Open attributes table", _openAttributesTable)
    editWidgetTest.addStep("Select layer in the layers tree and open its attribute table")
    editWidgetTest.addStep("Edit a value in the table using the code editor widget and check that it works correctly")
    editWidgetTest.addStep("Toggle editing", _stopEditing)

    rendererTest = Test("Renderer test")
    rendererTest.addStep("Open project", _openProject)
    rendererTest.addStep("Open layer properties. Go to the 'Style' tab and set renderer of the layer "
                         "to 'MIL-STD-2525' renderer. Close dialog by pressing 'OK' button", _openLayerProperties)
    rendererTest.addStep("Verify that layer rendered correctly.")

    sizeChangeTest = Test("Size change test")
    sizeChangeTest.addStep("Open project", _openProject)
    #sizeChangeTest.addStep("Set renderer", _setRenderer)
    sizeChangeTest.addStep("Open layer properties. Go to the 'Style' tab and set renderer of the layer "
                         "to 'MIL-STD-2525' renderer. Close dialog by pressing 'OK' button", _openLayerProperties)
    sizeChangeTest.addStep("Verify that the layer is rendered with MIL-STD-2525 symbology", isVerifyStep=True)
    #sizeChangeTest.addStep("Change size", _changeSize)
    sizeChangeTest.addStep("Open layer properties. Go to the 'Style' tab and set symbol size to 80. "
                           "Close dialog by pressing 'OK' button", _openLayerProperties)
    sizeChangeTest.addStep("Verify that the size of symbols has changed")

    return [editWidgetTest, rendererTest, sizeChangeTest]


_tempFolder = None
def tempFolder():
    global _tempFolder
    if _tempFolder is None:
        _tempFolder = tempfile.mkdtemp()
    return _tempFolder

def deleteTempFolder():
    global _tempFolder
    if _tempFolder is not None:
        shutil.rmtree(_tempFolder, True)
        _tempFolder = None

def tempFilename(ext):
    path = tempFolder()
    ext = "" if ext is None else ext
    filename = path + os.sep + str(time.time()) + "." + ext
    return filename


class MilStd2525Test(unittest.TestCase):

    def tearDown(self):
        deleteTempFolder()

    def checkSymbolRendering(self,symbol, expected):
        """Check symbols rendering"""
        expectedFilename = os.path.join(os.path.dirname(__file__), "expected", expected + ".png")
        image = symbol.bigSymbolPreviewImage()
        renderedFilename = tempFilename("png")
        image.save(renderedFilename)
        expectedData = open(expectedFilename, "rb").read()
        expectedHash = hashlib.md5(expectedData).hexdigest()
        renderedData = open(renderedFilename, "rb").read()
        renderedHash = hashlib.md5(renderedData).hexdigest()
        self.assertTrue(expectedHash, renderedHash)

    def testDefaultSymbol(self):
        """Check that default symbol is correct"""
        self.checkSymbolRendering(getDefaultSymbol(40), "default_40")
        self.checkSymbolRendering(getDefaultSymbol(80), "default_80")

    def testWrongCode(self):
        """Check wrong SIDC code handling"""
        self.assertIsNone(symbolForCode("wrongcode", 40))

    def testRendering(self):
        """Test code rendering"""
        self.checkSymbolRendering(symbolForCode("10164011521200001600",40), "10164011521200001600_40")
        self.checkSymbolRendering(symbolForCode("10164011521200001600",80), "10164011521200001600_80")

    def testRendererSavedToProject(self):
        """Test that renderer correctly saved in the project"""
        projfile = os.path.join(os.path.dirname(__file__), "data", "project.qgs")
        iface.addProject(projfile)
        layer = _layerFromName("2525")
        renderer = MilStd2525Renderer(50, "SDIC")
        layer.setRenderer(renderer)
        newProjectFile = tempFilename("qgs")
        proj = QgsProject.instance()
        proj.write(newProjectFile)
        iface.newProject()
        iface.addProject(newProjectFile)
        layer = _layerFromName("2525")
        layerRenderer = layer.renderer()
        self.assertEquals("MilStd2525Renderer", layerRenderer.type())


def pluginSuite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(MilStd2525Test, 'test'))
    return suite


def unitTests():
    _tests = []
    _tests.extend(pluginSuite())
    return _tests


def run_tests():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(pluginSuite())
