# -*- coding: utf-8 -*-

from qgis.core import QgsRendererV2Registry
from qgis.gui import QgsEditorWidgetRegistry

from renderer import MilStd2525RendererMetadata
from sidcwidgetwrapper import SIDCWidgetWrapperFactory
#from sidcdialog import SIDCWidgetWrapperFactory

class MilStd2525Plugin:
    def __init__(self, iface):
        self.iface = iface

        self._rendererMetadata = MilStd2525RendererMetadata()
        self._widgetWrapperFactory = SIDCWidgetWrapperFactory()

        QgsRendererV2Registry.instance().addRenderer(self._rendererMetadata)
        QgsEditorWidgetRegistry.instance().registerWidget('SDIC code editor', self._widgetWrapperFactory)

    def unload(self):
        QgsRendererV2Registry.instance().removeRenderer('MilStd2525Renderer')

    def initGui(self):
        pass
