[![Build Status](https://travis-ci.org/boundlessgeo/qgis-milstd2525-plugin.svg?branch=master)](https://travis-ci.org/boundlessgeo/qgis-milstd2525-plugin)

# MilStd2525

Plugin that add support for MIL-STD-2525 symbology in QGIS. It provides:
 - custom renderer for rendering a layer with SIDC codes in one of its attributes
 - custom editor widget, for entering SIDC codes in the corresponding field
   with an icon preview

## Contribute

MilStd2525 is on GitHub at https://github.com/boundlessgeo/QGIS-MIL-STD-2525.
If you wish to contribute patches you can [fork the project](https://help.github.com/forking/),
make your changes, commit to your repository, and then
[issue a pull request](http://help.github.com/pull-requests/). The development
team can then review your contribution and commit it upstream as appropriate.

## Documentation

The plugin is documented [here](http://boundlessgeo.github.io/qgis-plugins-documentation/milstd2525).

## Cloning this repository

This repository uses external repositories as submodules. Therefore in order to include the external repositories during cloning you should use the *--recursive* option:

`git clone --recursive http://github.com/boundlessgeo/qgis-milstd2525-plugin.git`

Also, to update the submodules whenever there are changes in the remote repositories one should do:

`git submodule update --remote`

## Current status

Both renderer and custom widget are implemented.

The renderer raises an exception when it is deselected in the properties windows.
Work can be resumed after closing the error dialog, and it does not crash QGIS.

The error is related to the rendered object being garbage collected by QGIS,
and is likely to be a SIP issue.

## Further info

Here's some extra info to continue developing/testing this plugin.

A generator of markers from SIDC codes can be found [here](http://spatialillusions.com/unitgenerator.html)

This tool is useful for checking that markers are correctly rendered and the SDIC codes are being correctly interpreted.

---

Markers single parts, from which full markers are created, were taken from this project:

[https://github.com/Esri/joint-military-symbology-xml](https://github.com/Esri/joint-military-symbology-xml)

Additional info about the icons themselves and the coding of markers can be found there as well.
