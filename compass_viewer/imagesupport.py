# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Small module to handle common image operations.

Images themselves come from the auto-generated "images.py" module.
"""

import wx
import cStringIO
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