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

""" A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject

Run `python setup.py --help-commands` for available options
"""

from __future__ import absolute_import, division, print_function  # unicode_literals

import os
import sys
# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# ---------------------------------------------------------------------------
#                             Some helper stuff
# ---------------------------------------------------------------------------

if 'bdist_wininst' in sys.argv:
    if len(sys.argv) > 2 and ('sdist' in sys.argv or 'bdist_rpm' in sys.argv):
        print("Error: bdist_wininst must be run alone. Exiting.")
        sys.exit(1)

here = os.path.abspath(os.path.dirname(__file__))


def txt_read(*paths):
    """ Build a file path from *paths* and return the textual contents """
    with open(os.path.join(here, *paths), encoding='utf-8') as f:
        return f.read()

# ---------------------------------------------------------------------------
#                      Populate dictionary with settings
# ---------------------------------------------------------------------------

# Create a dict with the basic information that is passed to setup after keys are added.
setup_args = dict()

setup_args['name'] = 'hdf_compass'
# The adopted versioning scheme follow PEP40
setup_args['version'] = '0.6.0.dev1'
setup_args['url'] = 'https://github.com/HDFGroup/hdf-compass/'
setup_args['license'] = 'BSD-like license'
setup_args['author'] = 'HDFGroup'
setup_args['author_email'] = 'help@hdfgroup.org'

#
# descriptive stuff
#

description = 'An experimental viewer program for HDF5 and related formats.'
setup_args['description'] = description
if 'bdist_wininst' in sys.argv:
    setup_args['long_description'] = description
else:
    setup_args['long_description'] = txt_read('README.rst')

setup_args['classifiers'] = \
    [  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Office/Business :: Office Suites',
        'Topic :: Utilities'
    ]
setup_args['keywords'] = "data hdf bag ascii grid opendap"

#
# code stuff
#

# requirements
setup_args['setup_requires'] =\
    [
        "setuptools",
        "wheel",
    ]
setup_args['install_requires'] =\
    [
        "numpy",
        "matplotlib",
        "h5py",
        "wxPython",
        "hydroffice.bag",
        "pydap",
        "requests"
    ]
# hdf_compass namespace, packages and other files
setup_args['namespace_packages'] = ['hdf_compass']
setup_args['packages'] = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*.test*",
                                                ])
setup_args['package_data'] =\
    {
        '': ['icons/*.png', 'icons/*.ico', 'icons/*.icns', 'icons/*.txt'],
    }
setup_args['data_files'] = []
setup_args['entry_points'] =\
    {
        'gui_scripts': ['HDFCompass = hdf_compass.compass_viewer.viewer:run'],
    }

# ---------------------------------------------------------------------------
#                            Do the actual setup now
# ---------------------------------------------------------------------------

setup(**setup_args)