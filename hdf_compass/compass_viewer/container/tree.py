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
__author__ = 'Hyo-Kyung Lee <hyoklee@hdfgroup.org>'

import platform
import wx
from hdf_compass import compass_model

from ..events import ID_COMPASS_OPEN, CompassOpenEvent
from ..events import ContainerSelectionEvent, EVT_CONTAINER_SELECTION


import logging
log = logging.getLogger(__name__)

ID_CONTEXT_MENU_OPEN = wx.NewId()
ID_CONTEXT_MENU_OPENWINDOW = wx.NewId()

class ContainerTree(wx.TreeCtrl):

    """
    Defines the current selection (via .selection property) as well as
    handling item activation (double-click, Enter) and right-click context
    menu.
    """

    def __init__(self, parent, node, **kwds):
        """
        Initialize tree view window.
        :param parent: NodeFrame's view window
        :param node: container instance to dispaly
        :param kwds: other optional arguments
        :return:
        """
        wx.TreeCtrl.__init__(self, parent, **kwds)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rclick)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
        self.Bind(wx.EVT_MENU, self.on_context_open, id=ID_CONTEXT_MENU_OPEN)
        self.Bind(wx.EVT_MENU, self.on_context_openwindow,
                  id=ID_CONTEXT_MENU_OPENWINDOW)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.hint_select)
        self.Bind(wx.EVT_SCROLLWIN, self.on_bottom)
        self.node = node
        self.limit = 20

        self.il = wx.GetApp().imagelists[16]
        self.SetImageList(self.il)

        self.root = self.AddRoot(node.display_name)
        img_ind = self.il.get_index(type(node))
        self.SetItemImage(self.root, img_ind, wx.TreeItemIcon_Normal)
        self.SetPyData(self.root, {'idx':-1, 'node':node})
        self.SelectItem(self.root, True)


    @property
    def selection(self):
        """ The currently selected item, or None. """
        log.debug('selected.')
        grp = self.GetSelection()
        node = self.GetPyData(grp)['node']
        # Add children if they don't exist.
        if (isinstance(node, compass_model.Container) and
            self.GetChildrenCount(grp) == 0):
            for item in xrange(len(node)):
                if item < self.limit:
                    subnode = node[item]
                    i = self.AppendItem(grp, subnode.display_name)
                    image_index = self.il.get_index(type(subnode))

                    self.SetItemImage(i, image_index, wx.TreeItemIcon_Normal)
                    self.SetPyData(i, {'idx':item, 'node':subnode})
            self.Expand(grp)
        return node

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
        
        item = evt.GetItem()
        newnode = self.GetPyData(item)['node']


        if newnode:
            pos = wx.GetTopLevelParent(self).GetPosition()
            evt = CompassOpenEvent(newnode, pos=pos)
            wx.PostEvent(self, evt)


    # ---------------------------------------------------------
    # Context menu support

    def on_rclick(self, evt):
        """ Pop up a context menu appropriate for the item """

        item = evt.GetItem()
        node = self.GetPyData(item)['node']
        if node is None:
            return
        print node
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
        
    def on_bottom(self, evt):
        """ Handle window scroll down event.
            This works only for Windows and Mac.
            Mac fires this event several times in succession.
            Windows fires only once.
        """
        if (evt.Orientation == wx.SB_VERTICAL and
            (evt.GetEventType() == wx.wxEVT_SCROLLWIN_PAGEDOWN
                or evt.GetEventType() == wx.wxEVT_SCROLLWIN_LINEDOWN)):
            log.debug("got scroll down event.")
            # Show more items automatically.
            item = self.GetLastChild(self.root)
            start = self.GetPyData(item)['idx']

            for x in xrange(len(self.node)):
                if start < x <= start + self.limit:
                    subnode = self.node[x]
                    i = self.AppendItem(self.root, subnode.display_name)
                    image_index = self.il.get_index(type(subnode))
                    self.SetItemImage(i, image_index, wx.TreeItemIcon_Normal)
                    self.SetPyData(i, {'idx':x, 'node':subnode})
                    self.ScrollTo(i)


    def recursive_walk(self, node, depth):
        """ Build tree from node by traversing children recursively.
        """
        # If nodes have loop among them, it will recurse forever.
        # To prevent it, use depth.
        if depth > 1:
            return
        g = self.GetSelection()
        for item in xrange(len(node)):
            if item < self.limit:
                subnode = node[item]
                i = self.AppendItem(g, subnode.display_name)
                image_index = self.il.get_index(type(subnode))

                self.SetItemImage(i, image_index, wx.TreeItemIcon_Normal)
                self.SetPyData(i, {'idx':item, 'node':subnode})
