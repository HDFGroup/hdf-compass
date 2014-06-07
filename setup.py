# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Setup script for HDFCompass on Mac OS X.  

Usage:
    python setup.py py2app

The output is HDFCompass.app, in the dist/ folder.

PyInstaller, for Windows and Linux distribution, does not use setup.py.
"""

from setuptools import setup

APP = ['HDFCompass.py']
DATA_FILES = []
PLIST = {   "CFBundleDocumentTypes": [ { "CFBundleTypeExtensions": ["hdf5","h5"],
                                      "CFBundleTypeName": "HDF5 Data File",
                                      "CFBundleTypeRole": "Viewer"} ],
            "CFBundleIdentifer": "org.alfven.hdfcompass",
            "CFBundleDisplayName": "HDFCompass",
            "CFBundleVersion": "0.4.0" }

OPTIONS = { 'argv_emulation': True,
            'excludes': ['scipy'],
            'matplotlib_backends': ['wxagg'],
            'iconfile': 'compass.icns',
            'plist': PLIST }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
