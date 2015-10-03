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
Small module to handle common image operations.

Images themselves come from the auto-generated "images.py" module.
"""

import cStringIO

import wx

from . import images


def getbitmap(name):
    """ Return a wx.Bitmap of the given icon """
    png = getattr(images, name)()
    return png_to_bitmap(png)


def png_to_bitmap(png):
    """ Convert a string with raw PNG data to a wx.Bitmap """
    stream = cStringIO.StringIO(png)
    img = wx.ImageFromStream(stream, wx.BITMAP_TYPE_PNG)
    return img.ConvertToBitmap()
