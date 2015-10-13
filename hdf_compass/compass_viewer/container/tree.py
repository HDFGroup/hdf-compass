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
Handles tree view for Container display.
"""

import wx
import compass_model

from ..events import ID_COMPASS_OPEN, CompassOpenEvent
from ..events import ContainerSelectionEvent, EVT_CONTAINER_SELECTION

ID_CONTEXT_MENU_OPEN = wx.NewId()
ID_CONTEXT_MENU_OPENWINDOW = wx.NewId()

class ContainerTree(wx.TreeCtrl):

    """
    Defines the current selection (via .selection property) as well as
    handling item activation (double-click, Enter) and right-click context
    menu.
    """

    def __init__(self, parent, node, **kwds):
        wx.TreeCtrl.__init__(self, parent, **kwds)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rclick)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
        self.Bind(wx.EVT_MENU, self.on_context_open, id=ID_CONTEXT_MENU_OPEN)
        self.Bind(wx.EVT_MENU, self.on_context_openwindow,
                  id=ID_CONTEXT_MENU_OPENWINDOW)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.hint_select)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.hint_select)
        self.node = node

        self.il = wx.GetApp().imagelists[16]
        self.SetImageList(self.il)

        g = self.AddRoot(node.display_name)
        img_ind = self.il.get_index(type(node))
        self.SetItemImage(g, img_ind, wx.TreeItemIcon_Normal)
        self.SetPyData(g, {'idx':-1})
        
        for item in xrange(len(self.node)):
            if item < 20:
                subnode = self.node[item]
                i = self.AppendItem(g, subnode.display_name)
                image_index = self.il.get_index(type(subnode))
                self.SetItemImage(i, image_index, wx.TreeItemIcon_Normal)
                self.SetPyData(i, {'idx':item})

        if len(self.node) > 20:
            i = self.AppendItem(g, 'more...')
            self.SetPyData(i, {'idx':-2})

    @property
    def selection(self):
        """ The currently selected item, or None. """
        item = self.GetSelection()
        idx = self.GetPyData(item)['idx']
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

        # idx = evt.GetIndex()
        item = evt.GetItem()
        idx = self.GetPyData(item)['idx']
        if idx >= 0:
            newnode = self.node[idx]
            pos = wx.GetTopLevelParent(self).GetPosition()
            evt = CompassOpenEvent(newnode, pos=pos)
            wx.PostEvent(self, evt)
        else:
            return

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
                submenu.Append(id_, h.classkind)
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


