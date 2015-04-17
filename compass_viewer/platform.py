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
    Module for platform- and version-specific feature detection.
"""

import sys

MAC = sys.platform == 'darwin'
WINDOWS = sys.platform == 'win32'
LINUX = sys.platform == 'linux2'

if not any((MAC, WINDOWS, LINUX)):
    raise ValueError('Unknown platform "%s"' % sys.platform)

VERSION = "0.5"