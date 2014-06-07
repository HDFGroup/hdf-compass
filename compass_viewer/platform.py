# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
    Module for platform- and version-specific feature detection.
"""

import sys

MAC = sys.platform == 'darwin'
WINDOWS = sys.platform == 'win32'
LINUX = sys.platform == 'linux2'

if not any((MAC, WINDOWS, LINUX)):
    raise ValueError('Unknown platform "%s"' % sys.platform)

VERSION = "0.4a"