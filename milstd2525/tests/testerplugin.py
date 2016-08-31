# Tests for the QGIS Tester plugin. To know more see
# https://github.com/boundlessgeo/qgis-tester-plugin

from qgis.utils import *
from qgis.core import *
import os


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

    editWidgetTest = Test("Test code edit widget")
    editWidgetTest.addStep("Open project", _openProject)
    #editWidgetTest.addStep("Open layer properties", _openLayerProperties)
    editWidgetTest.addStep("Set the editor of the SDIC field to 'SDIC code editor")
    editWidgetTest.addStep("Toggle editing", _startEditing)
    editWidgetTest.addStep("Open attributes table", _openAttributesTable)
    editWidgetTest.addStep("Edit a value in the table using the code editor widget and check that it works correctly")
    editWidgetTest.addStep("Toggle editing", _stopEditing)

    renderedTest = Test("Renderer test")
    renderedTest.addStep("Open project", _openProject)
    renderedTest.addStep("Open layer properties", _openLayerProperties)
    renderedTest.addStep("Set renderer othe editor of the layer to 'MIL-STD-2525 renderer'. Verify it renders correctly")


    return [editWidgetTest, rendererTest]


def unitTests():
    _tests = []
    #add unit tests with _tests.extend(test_suite)
    return _tests