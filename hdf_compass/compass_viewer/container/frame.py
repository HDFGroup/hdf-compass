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
Implements a viewer for compass_model.Container instances.

This frame is a simple browser view with back/forward/up controls.

Currently list and icon views are supported.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import wx
import os

import logging
log = logging.getLogger(__name__)

from hdf_compass import compass_model
from ..frame import NodeFrame
from ..events import ID_COMPASS_OPEN
from ..events import EVT_CONTAINER_SELECTION
from .list import ContainerReportList, ContainerIconList
from .tree import ContainerTree
from .graph import ContainerGraph

ID_GO_MENU_BACK = wx.NewId()
ID_GO_MENU_NEXT = wx.NewId()
ID_GO_MENU_UP = wx.NewId()
ID_GO_MENU_TOP = wx.NewId()

ID_VIEW_MENU_LIST = wx.NewId()
ID_VIEW_MENU_ICON = wx.NewId()
ID_VIEW_MENU_TREE = wx.NewId()
ID_VIEW_MENU_GRAPH = wx.NewId()


class ContainerFrame(NodeFrame):
    """
    A frame to display a Container class, and browse its contents.
    """

    def __init__(self, node, pos=None):
        """ Create a new frame.

        node:   Container instance to display.
        pos:    Screen position at which to display the window.
        """
        NodeFrame.__init__(self, node, size=(800, 400), title=node.display_title, pos=pos)

        view_menu = wx.Menu()
        view_menu.Append(ID_VIEW_MENU_GRAPH, "Graph view")                
        view_menu.Append(ID_VIEW_MENU_TREE, "Tree view")        
        view_menu.Append(ID_VIEW_MENU_LIST, "List view")
        view_menu.Append(ID_VIEW_MENU_ICON, "Icon view")
        self.add_menu(view_menu, "View")
        self.view_menu = view_menu

        go_menu = wx.Menu()
        go_menu.Append(ID_GO_MENU_BACK, "Back")
        go_menu.Append(ID_GO_MENU_NEXT, "Next")
        go_menu.Append(ID_GO_MENU_UP, "Up")
        go_menu.Append(ID_GO_MENU_TOP, "Top")
        self.add_menu(go_menu, "Go")
        self.go_menu = go_menu

        self.acc_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CMD, wx.WXK_LEFT, ID_GO_MENU_BACK),
            (wx.ACCEL_CMD, wx.WXK_RIGHT, ID_GO_MENU_NEXT),
            (wx.ACCEL_CMD, wx.WXK_UP, ID_GO_MENU_UP),
            (wx.ACCEL_CMD | wx.ACCEL_SHIFT, wx.WXK_UP, ID_GO_MENU_TOP),
        ])
        self.SetAcceleratorTable(self.acc_tbl)

        self.Bind(wx.EVT_MENU, self.on_open, id=ID_COMPASS_OPEN)
        self.Bind(EVT_CONTAINER_SELECTION, lambda evt: self.update_info())

        self.Bind(wx.EVT_MENU, lambda evt: self.go_back(), id=ID_GO_MENU_BACK)
        self.Bind(wx.EVT_MENU, lambda evt: self.go_next(), id=ID_GO_MENU_NEXT)
        self.Bind(wx.EVT_MENU, lambda evt: self.go_up(), id=ID_GO_MENU_UP)
        self.Bind(wx.EVT_MENU, lambda evt: self.go_top(), id=ID_GO_MENU_TOP)
        self.Bind(wx.EVT_MENU, lambda evt: self.list_view(), id=ID_VIEW_MENU_LIST)
        self.Bind(wx.EVT_MENU, lambda evt: self.icon_view(), id=ID_VIEW_MENU_ICON)
        self.Bind(wx.EVT_MENU, lambda evt: self.tree_view(), id=ID_VIEW_MENU_TREE)
        self.Bind(wx.EVT_MENU, lambda evt: self.graph_view(), id=ID_VIEW_MENU_GRAPH)

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        tsize = (24, 24)
        back_bmp = wx.Bitmap(os.path.join(self.icon_folder, "go_back_24.png"), wx.BITMAP_TYPE_ANY)
        next_bmp = wx.Bitmap(os.path.join(self.icon_folder, "go_next_24.png"), wx.BITMAP_TYPE_ANY)
        up_bmp = wx.Bitmap(os.path.join(self.icon_folder, "go_up_24.png"), wx.BITMAP_TYPE_ANY)
        top_bmp = wx.Bitmap(os.path.join(self.icon_folder, "go_top_24.png"), wx.BITMAP_TYPE_ANY)
        icon_bmp = wx.Bitmap(os.path.join(self.icon_folder, "view_icon_24.png"), wx.BITMAP_TYPE_ANY)
        list_bmp = wx.Bitmap(os.path.join(self.icon_folder, "view_list_24.png"), wx.BITMAP_TYPE_ANY)
        tree_bmp = wx.Bitmap(os.path.join(self.icon_folder, "view_tree_24.png"), wx.BITMAP_TYPE_ANY)
        
        self.toolbar.SetToolBitmapSize(tsize)
        self.toolbar.AddLabelTool(ID_GO_MENU_BACK, "Back", back_bmp, shortHelp="New", longHelp="Long help for 'New'")
        self.toolbar.AddLabelTool(ID_GO_MENU_NEXT, "Next", next_bmp, shortHelp="New", longHelp="Long help for 'New'")
        self.toolbar.AddSeparator()        
        self.toolbar.AddLabelTool(ID_GO_MENU_UP, "Up", up_bmp, shortHelp="New", longHelp="Long help for 'New'")
        self.toolbar.AddLabelTool(ID_GO_MENU_TOP, "Top", top_bmp, shortHelp="New", longHelp="Long help for 'New'")        
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddLabelTool(ID_VIEW_MENU_TREE, "Tree View", tree_bmp, shortHelp="Tree", longHelp="View in Tree")                
        self.toolbar.AddLabelTool(ID_VIEW_MENU_LIST, "List View", list_bmp, shortHelp="New",
                                  longHelp="View in List")
        self.toolbar.AddLabelTool(ID_VIEW_MENU_ICON, "Icon View", icon_bmp, shortHelp="New",
                                  longHelp="View in Icons")

        self.toolbar.Realize()
        # self.view = ContainerGraph(self, node)
        self.view = ContainerTree(self, node)
        # self.view = ContainerReportList(self, node)

        self.history = [node]
        self.history_ptr = 0
        self.update_view()

    def list_view(self):
        """ Switch to list view """
        if not isinstance(self.view, ContainerReportList):
            self.view = ContainerReportList(self, self.history[self.history_ptr])

    def icon_view(self):
        """ Switch to icon view """
        if not isinstance(self.view, ContainerIconList):
            self.view = ContainerIconList(self, self.history[self.history_ptr])

    def tree_view(self):
         """ Switch to tree view """
         if not isinstance(self.view, ContainerTree):
             self.view = ContainerTree(self, self.history[self.history_ptr])
             self.update_view()

    def graph_view(self):
         """ Switch to graph view """
         if not isinstance(self.view, ContainerTree):
             self.view = ContainerGraph(self, self.history[self.history_ptr])
             self.update_view()
            
    # --- Begin history support functions -------------------------------------

    @property
    def node(self):
        return self.history[self.history_ptr]

    def go_back(self):
        """ Go to the previously displayed item """
        if self.history_ptr > 0:
            self.history_ptr -= 1
        self.update_view()

    def go_next(self):
        """ Go to the next displayed item """
        if self.history_ptr < (len(self.history) - 1):
            self.history_ptr += 1
        self.update_view()

    def go_up(self):
        """ Go to the enclosing container """
        node = self.history[self.history_ptr]
        parent = node.store.get_parent(node.key)
        if parent.key != node.key:  # at the root item
            self.go(parent)

    def go_top(self):
        """ Go to the root node """
        node = self.history[self.history_ptr]
        parent = node.store.root
        if parent.key != node.key:  # at the root item
            self.go(parent)

    def go(self, newnode):
        """ Go to a particular node.

        Adds the node to the history.
        """
        del self.history[self.history_ptr + 1:]
        self.history.append(newnode)
        self.history_ptr += 1
        self.update_view()

    # --- End history support functions ---------------------------------------

    def update_view(self):
        """ Refresh the entire contents of the frame according to self.node. """
        self.SetTitle(self.node.display_title)
        self.view = type(self.view)(self, self.node)
        self.update_info()

        can_go_back = self.history_ptr > 0
        can_go_next = self.history_ptr < (len(self.history) - 1)
        can_go_up = self.node.store.get_parent(self.node.key) is not None
        can_go_top = self.node.key != self.node.store.root.key
        self.go_menu.Enable(ID_GO_MENU_BACK, can_go_back)
        self.go_menu.Enable(ID_GO_MENU_NEXT, can_go_next)
        self.go_menu.Enable(ID_GO_MENU_UP, can_go_up)
        self.go_menu.Enable(ID_GO_MENU_TOP, can_go_top)
        self.toolbar.EnableTool(ID_GO_MENU_BACK, can_go_back)
        self.toolbar.EnableTool(ID_GO_MENU_NEXT, can_go_next)
        self.toolbar.EnableTool(ID_GO_MENU_UP, can_go_up)
        self.toolbar.EnableTool(ID_GO_MENU_TOP, can_go_top)

        icon_view_allowed = len(self.node) <= 1000
        self.view_menu.Enable(ID_VIEW_MENU_ICON, icon_view_allowed)
        self.toolbar.EnableTool(ID_VIEW_MENU_ICON, icon_view_allowed)

    def update_info(self):
        """ Refresh the left-hand side information panel, according to the
        current selection in the view.
        """
        node = self.view.selection
        if node is None:
            node = self.node  # Nothing selected; show this node's info
        self.info.display(node)

    def on_open(self, evt):
        """ Trap Container open events, so we can browse instead of launching
        new windows.
        """
        new_node = evt.node
        log.debug("Got request to open node: %s" % new_node.key)
        if isinstance(new_node, compass_model.Container):
            self.go(new_node)
        else:
            evt.Skip()
