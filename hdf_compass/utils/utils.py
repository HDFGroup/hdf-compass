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
Implementation of utils and helper functions
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import logging
log = logging.getLogger(__name__)

is_darwin = sys.platform == 'darwin'
is_win = sys.platform == 'win32'
is_linux = sys.platform == 'linux2'


def url2path(url):
    """Helper function that returns the file path from an url, dealing with Windows peculiarities"""
    if is_win:
        return url.replace('file:///', '')
    else:
        return url.replace('file://', '')


def path2url(path):
    """Helper function that returns the url from a file path, dealing with Windows peculiarities"""
    if is_win:
        return 'file:///' + path
    else:
        return 'file://' + path
