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
Defines the left-hand side information panel used to display context info.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import wx

import logging
log = logging.getLogger(__name__)

from hdf_compass import compass_model
from .imagesupport import png_to_bitmap
from . import platform

# Info panel width
PANEL_WIDTH = 200

# Size of the main title font
FONTSIZE = 16 if platform.WINDOWS else 18


class InfoPanel(wx.Panel):
    """
    Panel displaying general information about the selected object.

    Designed to be displayed vertically; sets its own width (PANEL_WIDTH).
    """

    def __init__(self, parent):
        """ Constructor.  *parent* should be the containing frame.
        """
        wx.Panel.__init__(self, parent, size=(PANEL_WIDTH, 10), style=wx.BORDER_NONE)

        font = wx.Font(FONTSIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        # Sidebar title text
        self.nametext = wx.StaticText(self, style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE, size=(PANEL_WIDTH - 40, 30))
        self.nametext.SetFont(font)

        # Sidebar icon (see display method)
        self.staticbitmap = None

        # Descriptive text below the icon
        self.proptext = wx.StaticText(self, style=wx.ALIGN_LEFT)

        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.nametext, 0, wx.LEFT | wx.TOP | wx.RIGHT, border=20)
        sizer.Add(self.proptext, 0, wx.LEFT | wx.RIGHT, border=20)
        sizer.AddStretchSpacer(1)
        self.SetSizer(sizer)

        self.SetBackgroundColour(wx.Colour(255, 255, 255))

    def display(self, node):
        """ Update displayed information on the node.

        See the get* methods for specifics on what's displayed.
        """

        self.nametext.SetLabel(node.display_name)
        self.proptext.SetLabel(describe(node))

        if self.staticbitmap is not None:
            self.sizer.Remove(self.staticbitmap)
            self.staticbitmap.Destroy()

        # We load the PNG icon directly from the appropriate Node class
        png = type(node).icons[64]()
        b = png_to_bitmap(png)

        self.staticbitmap = wx.StaticBitmap(self, wx.ID_ANY, b)
        self.sizer.Insert(1, self.staticbitmap, 0, wx.ALL, border=20)
        self.sizer.Layout()
        self.Layout()


def describe(node):
    """ Return a (possibly multi-line) text description of a node.
    """
    desc = "%s\n\n" % type(node).class_kind

    if isinstance(node, compass_model.Array):
        desc += "Shape\n%s\n\nType\n%s" % \
                (node.shape, dtypetext(node.dtype))

    elif isinstance(node, compass_model.Container):
        desc += "%d items\n" % len(node)

    return desc


def dtypetext(dt):
    """ String description appropriate for a NumPy dtype """
    if dt.names is not None:
        return "Compound (%d fields)" % len(dt.names)
    if dt.kind == 'f':
        return "%d-byte floating point" % dt.itemsize
    if dt.kind == 'u':
        return "%d-byte unsigned integer" % dt.itemsize
    if dt.kind == 'i':
        return "%d-byte signed integer" % dt.itemsize
    if dt.kind == 'S':
        return "ASCII String (%d characters)" % dt.itemsize
    return "Unknown"
