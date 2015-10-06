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
Implements a simple true-color image viewer.
"""

import wx
import wx.grid
from wx.lib.newevent import NewCommandEvent  # FIXME: Unused?

from ..frame import NodeFrame


class ImageFrame(NodeFrame):

    """
        Top-level frame displaying objects of type compass_model.Image.
    """

    def __init__(self, node, **kwds):
        """ Create a new array viewer, to display *node*. """
        NodeFrame.__init__(self, node, title=node.displayname, size=(800, 400), **kwds)
        self.node = node

        p = ImagePanel(self, node)
        self.view = p


class ImagePanel(wx.Panel):

    """
    Panel inside the image viewer pane which displays the image.
    """

    def __init__(self, parent, node):
        """ Display a truecolor, pixel-interlaced (not pixel-planar) image
        """
        wx.Panel.__init__(self, parent)
        b = wx.BitmapFromBuffer(node.width, node.height, node.data)
        b.CopyFromBuffer(node.data)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sb = wx.StaticBitmap(self, wx.ID_ANY, b)
        sizer.AddStretchSpacer()
        sizer.Add(sb, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.AddStretchSpacer()
        sizer2.Add(sizer, 1)
        sizer2.AddStretchSpacer()

        self.SetSizer(sizer2)
