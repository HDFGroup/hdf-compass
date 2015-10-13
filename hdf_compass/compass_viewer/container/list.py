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
Handles list and icon view for Container display.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import wx

import logging
log = logging.getLogger(__name__)

from hdf_compass import compass_model
from ..events import CompassOpenEvent
from ..events import ContainerSelectionEvent

ID_CONTEXT_MENU_OPEN = wx.NewId()
ID_CONTEXT_MENU_OPENWINDOW = wx.NewId()


class ContainerList(wx.ListCtrl):
    """
    Base class for list and icons views, both of which use wx.ListCtrl.
    
    Defines the current selection (via .selection property) as well as
    handling item activation (double-click, Enter) and right-click context
    menu.
    """

    def __init__(self, parent, node, **kwds):
        wx.ListCtrl.__init__(self, parent, **kwds)

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_rclick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate)
        self.Bind(wx.EVT_MENU, self.on_context_open, id=ID_CONTEXT_MENU_OPEN)
        self.Bind(wx.EVT_MENU, self.on_context_openwindow, id=ID_CONTEXT_MENU_OPENWINDOW)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.hint_select)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.hint_select)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.hint_select)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.hint_select)

    @property
    def selection(self):
        """ The currently selected item, or None. """
        idx = self.GetFirstSelected()
        if idx < 0:
            return None
        return self.node[idx]

    def hint_select(self, evt):
        """ Fire off a ContainerSelectionEvent """
        wx.PostEvent(self, ContainerSelectionEvent(self.GetId()))
        evt.Skip()

    def on_activate(self, evt):
        """ Emit a CompassOpenEvent when an item is double-clicked.
        """

        # wxPython Mac incorrectly treats a rapid left-right click as activate
        ms = wx.GetMouseState()
        if ms.RightIsDown():
            return

        idx = evt.GetIndex()
        newnode = self.node[idx]
        pos = wx.GetTopLevelParent(self).GetPosition()
        evt = CompassOpenEvent(newnode, pos=pos)
        wx.PostEvent(self, evt)

    # ---------------------------------------------------------
    # Context menu support

    def on_rclick(self, evt):
        """ Pop up a context menu appropriate for the item """

        # Click didn't land on an item
        idx = evt.GetIndex()
        if idx < 0:
            return

        # The node which was right-clicked in the view.
        node = self.node[idx]
        self._menu_node = node

        # Determine a list of handlers which can understand this object.
        # We exclude the default handler, "Unknown", as it can't do anything.
        handlers = [x for x in node.store.gethandlers(node.key) if x != compass_model.Unknown]

        # This will map menu IDs -> Node subclass handlers
        self._menu_handlers = {}

        menu = wx.Menu()
        menu.Append(ID_CONTEXT_MENU_OPEN, "Open")
        menu.Append(ID_CONTEXT_MENU_OPENWINDOW, "Open in New Window")

        if len(handlers) > 0:

            # Populate the "Open As" submenu, and record what
            # menu IDs map to what Node subclasses
            submenu = wx.Menu()
            for h in handlers:
                id_ = wx.NewId()
                self._menu_handlers[id_] = h
                submenu.Append(id_, h.class_kind)
                self.Bind(wx.EVT_MENU, self.on_context_openas, id=id_)
            menu.AppendSubMenu(submenu, "Open As")

        else:
            # No handlers were available, so gray out the "Open" entries
            id1 = wx.NewId()
            menu.Append(id1, "Open As")
            menu.Enable(ID_CONTEXT_MENU_OPEN, 0)
            menu.Enable(ID_CONTEXT_MENU_OPENWINDOW, 0)
            menu.Enable(id1, 0)

        self.PopupMenu(menu)

        del self._menu_node
        del self._menu_handlers

        menu.Destroy()

    def on_context_open(self, evt):
        """ Called in response to a plain "Open" in the context menu.

        Posts an event requesting that the node be opened as-is.
        """
        pos = wx.GetTopLevelParent(self).GetPosition()
        wx.PostEvent(self, CompassOpenEvent(self._menu_node, pos=pos))

    def on_context_openwindow(self, evt):
        """ Called in response to a plain "Open in New Window" in the context
        menu.
        
        Posts an event directly to the app object.
        """
        pos = wx.GetTopLevelParent(self).GetPosition()
        wx.PostEvent(wx.GetApp(), CompassOpenEvent(self._menu_node, pos=pos))

    def on_context_openas(self, evt):
        """ Called in response to one of the "Open As" context menu items.
        """
        # The "Open As" submenu ID
        id_ = evt.GetId()

        # Node which was right-clicked in the view
        node_being_opened = self._menu_node

        # The requested Node subclass to instantiate
        h = self._menu_handlers[id_]

        # Brand new Node instance of the requested type
        node_new = h(node_being_opened.store, node_being_opened.key)

        # Send off a request for it to be opened in the appropriate viewer
        pos = wx.GetTopLevelParent(self).GetPosition()
        wx.PostEvent(self, CompassOpenEvent(node_new, pos=pos))

        # End context menu support
        # -------------------------------------------------------------------


class ContainerIconList(ContainerList):
    """
    Icon view of nodes in a Container.
    """

    def __init__(self, parent, node):
        """ New icon list view
        """
        ContainerList.__init__(self, parent, node, style=wx.LC_ICON | wx.LC_AUTOARRANGE | wx.BORDER_NONE | 0x400)
        self.node = node

        self.il = wx.GetApp().imagelists[64]
        self.SetImageList(self.il, wx.IMAGE_LIST_NORMAL)

        for item in xrange(len(self.node)):
            subnode = self.node[item]
            image_index = self.il.get_index(type(subnode))
            self.InsertImageStringItem(item, subnode.display_name, image_index)


class ContainerReportList(ContainerList):
    """
    List view of the container's contents.

    Uses a wxPython virtual list, allowing millions of items in a container
    without any slowdowns.
    """

    def __init__(self, parent, node):
        """ Create a new list view.

        parent: wxPython parent object
        node:   Container instance to be displayed
        """

        ContainerList.__init__(self, parent, node,
                               style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_SINGLE_SEL | wx.BORDER_NONE)

        self.node = node

        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Kind")
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 200)

        self.il = wx.GetApp().imagelists[16]
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.SetItemCount(len(node))
        self.Refresh()

    def OnGetItemText(self, item, col):
        """ Callback method to support virtual list ctrl """
        if col == 0:
            return self.node[item].display_name
        elif col == 1:
            return type(self.node[item]).class_kind
        return ""

    def OnGetItemImage(self, item):
        """ Callback method to support virtual list ctrl """
        subnode = self.node[item]
        return self.il.get_index(type(subnode))
