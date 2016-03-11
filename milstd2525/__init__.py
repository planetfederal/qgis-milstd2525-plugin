# -*- coding: utf-8 -*-

def classFactory(iface):
    from plugin import MilStd2525Plugin
    return MilStd2525Plugin(iface)
