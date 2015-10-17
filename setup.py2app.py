##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of the HDF Compass Viewer. The full HDF Compass          #
# copyright notice, including terms governing use, modification, and         #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

"""
Setup script for HDFCompass on Mac OS X.  

Usage:
    python setup.py py2app

The output is HDFCompass.app, in the dist/ folder.

After running setup.py2app.py and verifying the install image, run:
    appdmg spec.json HDFCompass.dmg
To create dmg install file.  The appdmg utility can be installed from npm: 
    npm install -g appdmg


PyInstaller, for Windows and Linux distribution, does not use setup.py2app.py.
"""

from setuptools import setup
from glob import glob
import os
	

APP = ['HDFCompass.py']
compass_viewer_folder = os.path.join('hdf_compass', 'compass_viewer', 'icons')
compass_model_folder = os.path.join('hdf_compass', 'compass_model', 'icons')
DATA_FILES = [
	(compass_viewer_folder, glob(os.path.join(compass_viewer_folder, '*.png'))),
	(compass_model_folder, glob(os.path.join(compass_model_folder, '*.png'))),
]
PLIST = {   "CFBundleDocumentTypes": [ { "CFBundleTypeExtensions": ["hdf5","h5"],
                                      "CFBundleTypeName": "HDF5 Data File",
                                      "CFBundleTypeRole": "Viewer"} ],
            "CFBundleIdentifer": "org.hdfgroup.compass",
            "CFBundleDisplayName": "HDFCompass",
            "CFBundleVersion": "0.5.0" }

# ARGV emulation interacts badly with wxPython on Mac... it "eats" events
# when the program starts up and causes windows not to be displayed.
OPTIONS = { 'argv_emulation': False,
            'excludes': ['scipy', 'PyQt4', 'mpi4py'],
            'includes': ['h5py', 'matplotlib'],
            'matplotlib_backends': ['wxagg',],
            'iconfile': 'HDFCompass.icns',
            'packages': ['h5py', 'matplotlib'],
            'plist': PLIST }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
