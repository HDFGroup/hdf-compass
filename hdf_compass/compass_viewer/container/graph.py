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
Handles graph view for Container display.
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

class ContainerGraph(wx.Window):

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
        wx.Window.__init__(self, parent, **kwds)
        # Bind mouse events later.
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
        self.Bind(wx.EVT_MENU, self.on_context_open, id=ID_CONTEXT_MENU_OPEN)
        self.Bind(wx.EVT_MENU, self.on_context_openwindow,
                  id=ID_CONTEXT_MENU_OPENWINDOW)


        self.node = node
        self.limit = 20

        self.il = wx.GetApp().imagelists[16]

        self.BufferBmp = None
        self.OnSize(None)

    def OnSize(self, event):
        # Get the size of the drawing area in pixels.
        self.wi, self.he = self.GetSizeTuple()
        # Create BufferBmp and set the same size as the drawing area.
        self.BufferBmp = wx.EmptyBitmap(self.wi, self.he)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.BufferBmp)
        # Drawing job
        ret = self.DoSomeDrawing(memdc)
        if not ret:  #error
            self.BufferBmp = None
            wx.MessageBox('Error in drawing', 'CommentedDrawing', wx.OK | wx.ICON_EXCLAMATION)


    # OnPaint is executed at the app start, when resizing or when
    # the application windows becomes active. OnPaint copies the
    # buffered picture, instead of preparing (again) the drawing job.
    # This is the trick, copying is very fast.
    # Note: if you forget to define the dc in this procedure,
    # (no dc = ... code line), the application will run in
    # an infinite loop. This is a common beginner's error. (I think)
    # BeginDrawing() and EndDrawing() are for windows platforms (see doc).
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        if self.BufferBmp != None:
            dc.DrawBitmap(self.BufferBmp, 0, 0, True)
        else:
            dc.EndDrawing()


    # The function defines the drawing job. Everything is drawn on the dc.
    # In that application, the dc corresponds to the BufferBmp.
    # Three things are drawn, a square with a fixed size, and two
    # rectangles with sizes determined by the size of the dc, that
    # means the size of the drawing area. Keep in mind, the size
    # of the drawing area depends on the size of the main frame,
    # which can be resized on the fly with your mouse.
    # At this point, I will introduce a small complication, that is
    # in fact quite practical. It may happen, the drawing is not
    # working correctly. Either there is an error in the drawing job
    # or the data you want to plot can not be drawn correctly. A typical
    # example is the plotting of 'scientific data'. The data are not (or
    # may not be) scaled correctly, that leads to errors, generally integer
    # overflow errors.
    # To circumvent this, the procedure returns True, if the drawing succeed.
    # It returns False, if the drawing fails. The returned value may be used
    # later.
    def DoSomeDrawing(self, dc):
        try:

            dc.BeginDrawing()

            #~ raise OverflowError #for test

            # Clear everything
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.Clear()

            # Draw the square with a fixed size.
            dc.SetBrush(wx.Brush(wx.CYAN, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
            dc.DrawRectangle(10, 10, 200, 200)

            # Draw a transparent rectangle with a red border, proportional to
            # the dc size.
            dcwi, dche = dc.GetSizeTuple()
            dc.SetBrush(wx.Brush(wx.CYAN, wx.TRANSPARENT))
            dc.SetPen(wx.Pen(wx.RED, 1, wx.SOLID))
            dc.DrawRectangle(0, 0, dcwi, dche)

            # Draw one another rectangle, a rectangle with a size proportional
            # to the dc size.
            gap = 50
            dc.SetBrush(wx.Brush(wx.WHITE, wx.TRANSPARENT))
            dc.SetPen(wx.Pen(wx.BLACK, 1, wx.SOLID))
            dc.DrawRectangle(0 + gap, 0 + gap, dcwi - 2 * gap, dche - 2 * gap)

            # These next 2 lines will raise an overflow error.
            #~ largeval = 1e10
            #~ dc.DrawLine(dcwi // 2, dche // 2, largeval, largeval)

            dc.EndDrawing()
            return True

        except:
            return False

    @property
    def selection(self):
        """ The currently selected item, or None. """
        log.debug('selected.')
        return None

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

        wx.PostEvent(self, evt)


    # ---------------------------------------------------------
    # Context menu support

    def on_rclick(self, evt):
        """ Pop up a context menu appropriate for the item """


        node = self.node
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



    def recursive_walk(self, node, depth):
        """ Build graph from node by traversing children recursively.
        """
        # If nodes have loop among them, it will recurse forever.
        # To prevent it, use depth.
        if depth > 1:
            return

        for item in xrange(len(node)):
            if item < self.limit:
                subnode = node[item]
