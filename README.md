## MilStd2525

Plugin that add support for MIL-STD-2525 symbology in QGIS. It provides:
 - custom renderer for rendering a layer with SIDC codes in one of its attributes
 - custom editor widget, for entering SIDC codes in the corresponding field
   with an icon preview

# Contribute

MilStd2525 is on GitHub at https://github.com/boundlessgeo/QGIS-MIL-STD-2525.
If you wish to contribute patches you can [fork the project](https://help.github.com/forking/),
make your changes, commit to your repository, and then
[issue a pull request](http://help.github.com/pull-requests/). The development
team can then review your contribution and commit it upstream as appropriate.

# Documentation

The plugin is documented [here](http://boundlessgeo.github.io/qgis-plugins-documentation/milstd2525).

Cloning this repository
=======================

This repository uses external repositories as submodules. Therefore in order to include the external repositories during cloning you should use the *--recursive* option:

`git clone --recursive http://github.com/boundlessgeo/qgis-milstd2525-plugin.git`

Also, to update the submodules whenever there are changes in the remote repositories one should do:

`git submodule update --remote`
