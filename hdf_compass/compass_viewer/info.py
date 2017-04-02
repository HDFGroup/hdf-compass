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
import wx

import logging
logger = logging.getLogger(__name__)

from hdf_compass import compass_model
from hdf_compass.utils import is_win


# Info panel width
PANEL_WIDTH = 200

# Size of the main title font
FONTSIZE = 16 if is_win else 18


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
        self.name_text = wx.StaticText(self, style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE, size=(PANEL_WIDTH - 40, 30))
        self.name_text.SetFont(font)

        # Sidebar icon (see display method)
        self.static_bitmap = None

        # Descriptive text below the icon
        self.prop_text = wx.StaticText(self, style=wx.ALIGN_LEFT)

        self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.name_text, 0, wx.LEFT | wx.TOP | wx.RIGHT, border=20)
        sizer.Add(self.prop_text, 0, wx.LEFT | wx.RIGHT, border=20)
        sizer.AddStretchSpacer(1)
        self.SetSizer(sizer)

        self.SetBackgroundColour(wx.Colour(255, 255, 255))

    def display(self, node):
        """ Update displayed information on the node.

        See the get* methods for specifics on what's displayed.
        """

        self.name_text.SetLabel(node.display_name)
        self.prop_text.SetLabel(describe(node))

        if self.static_bitmap is not None:
            self.sizer.Detach(self.static_bitmap)
            self.static_bitmap.Destroy()

        # We load the PNG icon directly from the appropriate Node class
        png = wx.Bitmap(type(node).icons[64], wx.BITMAP_TYPE_ANY)
        self.static_bitmap = wx.StaticBitmap(self, wx.ID_ANY, png)
        self.sizer.Insert(1, self.static_bitmap, 0, wx.ALL, border=20)
        self.sizer.Layout()
        self.Layout()


def describe(node):
    """ Return a (possibly multi-line) text description of a node. """
    desc = "%s\n\n" % type(node).class_kind

    if isinstance(node, compass_model.Array):
        desc += "Shape\n%s\n\nType\n%s\n" % \
                (node.shape, dtype_text(node.dtype))

    elif isinstance(node, compass_model.Container):
        desc += "%d items\n" % len(node)
    
    if not isinstance(node, compass_model.KeyValue):    
        # see if there is a key-value handler for this node
        handlers = node.store.gethandlers(node.key)
        for h in handlers:
            
            kv_node = h(node.store, node.key)
            if isinstance(kv_node, compass_model.KeyValue):
                num_keys = len(kv_node.keys)
                if num_keys > 0:
                    desc += "\n%d %s\n" % (len(kv_node.keys), type(kv_node).class_kind)

    return desc


def dtype_text(dt):
    """ String description appropriate for a NumPy dtype """

    logger.debug("dtype kind: %s, size: %d" % (dt.kind, dt.itemsize))

    if dt.names is not None:
        logger.debug("dtype names: %s" % ",".join(n for n in dt.names))
        return "Compound (%d fields)" % len(dt.names)
    if dt.kind == 'f':
        return "%d-byte floating point" % dt.itemsize
    if dt.kind == 'u':
        return "%d-byte unsigned integer" % dt.itemsize
    if dt.kind == 'i':
        return "%d-byte signed integer" % dt.itemsize
    if dt.kind == 'S':
        return "ASCII String (%d characters)" % dt.itemsize
    if dt.kind == 'U':
        return "Unicode String (%d characters)" % dt.itemsize
    return "Unknown"
