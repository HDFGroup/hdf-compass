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
Implements a viewer for key-value stores (instances of compass_model.KeyValue).

Keys are strings, values are any data type HDFCompass can understand.
Presently this means all NumPy types, plus Python str/unicode.
"""

import wx
import compass_model

from ..frame import NodeFrame


class KeyValueFrame(NodeFrame):

    """
    A frame to display a list of key/value pairs, their types and shapes.
    """

    def __init__(self, node, pos=None):
        """ Create a new frame.

        node:   Container instance to display.
        """
        title = 'Attributes of "%s"' % node.displayname
        NodeFrame.__init__(self, node, size=(800, 400), title=title, pos=pos)

        self.list = KeyValueList(self, node)
        self.view = self.list


class KeyValueList(wx.ListCtrl):

    """
    A simple list view of key/value attributes
    """

    def __init__(self, parent, node):
        """ Create a new attribute list view.

        parent: wxPython parent object
        node:   compass_model.KeyValue instance
        """

        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_NONE|wx.LC_HRULES)

        self.node = node

        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Value")
        self.InsertColumn(2, "Type")
        self.InsertColumn(3, "Shape")

        names = node.keys
        values = [self.node[n] for n in names]

        def itemtext(item, col):
            name = names[item]
            data = values[item]
            text = ""
            if col == 0:
                text = name
            elif col == 1:
                text = str(data)
            elif col == 2:
                if hasattr(data, 'dtype'):
                    text = str(data.dtype)
                else:
                    text = str(type(data))
            elif col == 3:
                if hasattr(data, 'shape'):
                    text =  str(data.shape)
                else:
                    text = "()"
            return text

        for n in names:
            row = self.InsertStringItem(9999, n)
            for col in xrange(1,4):
                self.SetStringItem(row, col, itemtext(row, col))

        self.SetColumnWidth(0, 200)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, wx.LIST_AUTOSIZE)



        