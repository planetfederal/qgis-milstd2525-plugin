# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

from qgis.utils import *
from qgis.core import *
import os
import unittest
from milstd2525.milstd2525 import symbolForCode, getDefaultSymbol
from milstd2525.renderer import MilStd2525Renderer
import tempfile
import shutil
import time
from PyQt4.QtCore import QFileInfo
import hashlib

try:
    from qgistester.test import Test
    from qgistester.utils import layerFromName
except:
    pass

def functionalTests():
    try:
        from qgistester.test import Test
        from qgistester.utils import layerFromName
    except:
        return []


    def _openProject():
        projfile = os.path.join(os.path.dirname(__file__), "data", "project.qgs")
        iface.addProject(projfile)

    def _openLayerProperties():
        layer = layerFromName("2525")
        iface.showLayerProperties(layer)

    def _openAttributesTable():
        layer = layerFromName("2525")
        iface.showAttributeTable(layer)

    def _startEditing():
        layer = layerFromName("2525")
        layer.startEditing()

    def _stopEditing():
        layer = layerFromName("2525")
        layer.rollBack()
        iface.newProject()

    def _setRenderer():
        r = MilStd2525Renderer(40, "SDIC")
        layer = layerFromName("2525")
        layer.setRendererV2(r)
        layer.reload()
        layer.triggerRepaint()
        iface.mapCanvas().setExtent(layer.extent())

    def _changeSize():
        layer = layerFromName("2525")
        r = layer.rendererV2()
        r.size = 80
        layer.triggerRepaint()

    editWidgetTest = Test("Test code edit widget")
    editWidgetTest.addStep("Open project", _openProject)
    #editWidgetTest.addStep("Open layer properties", _openLayerProperties)
    editWidgetTest.addStep("Set the edit widget of the SDIC field to 'SDIC code editor'")
    editWidgetTest.addStep("Toggle editing", _startEditing)
    editWidgetTest.addStep("Open attributes table", _openAttributesTable)
    editWidgetTest.addStep("Edit a value in the table using the code editor widget and check that it works correctly")
    editWidgetTest.addStep("Toggle editing", _stopEditing)

    rendererTest = Test("Renderer test")
    rendererTest.addStep("Open project", _openProject)
    rendererTest.addStep("Open layer properties", _openLayerProperties)
    rendererTest.addStep("Set renderer othe editor of the layer to 'MIL-STD-2525 renderer'. Verify it renders correctly")

    sizeChangeTest = Test("Size change test")
    sizeChangeTest.addStep("Open project", _openProject)
    sizeChangeTest.addStep("Set renderer", _setRenderer)
    sizeChangeTest.addStep("Verify that the layer is rendered with MIL-STD-2525 symbology", isVerifyStep = True)
    sizeChangeTest.addStep("Change size", _changeSize)
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
        expectedFilename = os.path.join(os.path.dirname(__file__), "expected", expected + ".png")
        image = symbol.bigSymbolPreviewImage()
        renderedFilename = tempFilename("png")
        image.save(renderedFilename)
        expectedData = open(expectedFilename).read()
        expectedHash = hashlib.md5(expectedData).hexdigest()
        renderedData = open(renderedFilename).read()
        renderedHash = hashlib.md5(renderedData).hexdigest()
        self.assertTrue(expectedHash, renderedHash)

    def testDefaultSymbol(self):
        self.checkSymbolRendering(getDefaultSymbol(40),"default_40")
        self.checkSymbolRendering(getDefaultSymbol(80), "default_80")

    def testWrongCode(self):
        self.assertIsNone(symbolForCode("wrongcode", 40))

    def testRendering(self):
        self.checkSymbolRendering(symbolForCode("10164011521200001600",40), "10164011521200001600_40")
        self.checkSymbolRendering(symbolForCode("10164011521200001600",80), "10164011521200001600_80")


    def testRendererSavedToProject(self):
        projfile = os.path.join(os.path.dirname(__file__), "data", "project.qgs")
        iface.addProject(projfile)
        layer = layerFromName("2525")
        renderer = MilStd2525Renderer(50, "SDIC")
        layer.setRendererV2(renderer)
        newProjectFile = tempFilename("qgs")
        proj=QgsProject.instance()
        proj.write(QFileInfo(newProjectFile))
        iface.newProject()
        iface.addProject(newProjectFile)
        layer = layerFromName("2525")
        layerRenderer = layer.rendererV2()
        self.assertEquals("MilStd2525Renderer", layerRenderer.type())

def pluginSuite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(MilStd2525Test, 'test'))
    return suite

def unitTests():
    _tests = []
    _tests.extend(pluginSuite())
    return _tests