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
import matplotlib.pyplot as plt
plt.rcdefaults()
import networkx as nx
import numpy as np

import matplotlib
matplotlib.use('WXAgg')

import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from hdf_compass import compass_model

from ..events import ID_COMPASS_OPEN, CompassOpenEvent
from ..events import ContainerSelectionEvent, EVT_CONTAINER_SELECTION


import logging
log = logging.getLogger(__name__)

ID_CONTEXT_MENU_OPEN = wx.NewId()
ID_CONTEXT_MENU_OPENWINDOW = wx.NewId()

# class ContainerGraph(wx.Panel):
class ContainerGraph(wx.HVScrolledWindow):
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
        # wx.Window.__init__(self, parent, size=(600,400), **kwds)
        # wx.Panel.__init__(self, parent, **kwds)
        wx.HVScrolledWindow.__init__(self, parent, **kwds)
        # self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
        self.Bind(wx.EVT_MENU, self.on_context_open, id=ID_CONTEXT_MENU_OPEN)
        self.Bind(wx.EVT_MENU, self.on_context_openwindow,
                  id=ID_CONTEXT_MENU_OPENWINDOW)


        self.node = node
        self.limit = 20

        self.il = wx.GetApp().imagelists[16]
        # self.init_generic_dc()
        self.init_matplotlib()

    def init_generic_dc(self):
        # Bind mouse events later.
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.BufferBmp = None
        self.OnSize(None)

    def init_matplotlib(self):
        # self.data = data

        # self.panel = wx.Panel(self)

        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        # self.canvas = FigCanvas(self.panel, -1, self.fig)
        self.canvas = FigCanvas(self, -1, self.fig)
        self.axes = self.fig.add_subplot(111)
        # self.toolbar = NavigationToolbar(self.canvas)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        # self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.canvas, 1, wx.EXPAND)
        # self.vbox.Add(self.toolbar, 0, wx.EXPAND)

        # self.panel.SetSizer(self.vbox)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.draw_figure()

    def label(self, xy, text):
        y = xy[1] - 0.15  # shift y-value for label so that it's below the artist
        self.axes.text(xy[0], y, text, ha="center", family='sans-serif', size=14)

    def draw_figure(self):
        # create 3x3 grid to plot the artists
        G = nx.DiGraph()
        node = self.node
        G.add_node(node.display_name)
        # Containers
        c_labels = []
        c_graphs = []
        c_nodes = []

        # Dsets
        d_labels = []
        d_graphs = []
        d_nodes = []

        # Separate container type by shape.
        for item in xrange(len(node)):
            if item < self.limit:
                subnode = node[item]
                print type(subnode)
                G.add_node(item)
                e = (node.display_name, item)
                G.add_edge(*e)
                if type(subnode) == type(node):
                    c_nodes.append(item)
                    c_graphs.append(e)
                    c_labels.append(subnode.display_name)
                else:
                    d_nodes.append(item)
                    d_graphs.append(e)
                    d_labels.append(subnode.display_name)

        edge_labels = dict(zip(c_graphs, c_labels))

        pos = nx.spring_layout(G)
        if len(c_nodes) > 0:
            nx.draw_networkx_nodes(G, pos, nodelist=c_nodes,
                                   ax=self.axes, node_shape='o')
            nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=self.axes)

        if len(d_nodes) > 0:
            nx.draw_networkx_nodes(G, pos, nodelist=d_nodes,
                                   ax=self.axes, node_shape='s')


        self.axes.axis('equal')
        self.axes.axis('off')
        self.canvas.draw()

    def draw_figure_generic(self):
        grid = np.mgrid[0.2:0.8:3j, 0.2:0.8:3j].reshape(2, -1).T

        patches = []

        # add a circle
        # circle = mpatches.Circle(grid[0], 0.1, ec="none")
        # patches.append(circle)
        # self.label(grid[0], "Circle")

        # add a rectangle
        # rect = mpatches.Rectangle(grid[1] - [0.025, 0.05], 0.05, 0.1, ec="none")
        # patches.append(rect)
        circle = mpatches.Circle(grid[1], 0.05, ec="none")
        patches.append(circle)

        self.label(grid[1], self.node[0].display_name)

        # add a wedge
        # wedge = mpatches.Wedge(grid[2], 0.1, 30, 270, ec="none")
        # patches.append(wedge)
        # self.label(grid[2], "Wedge")

        # add a Polygon
        # polygon = mpatches.RegularPolygon(grid[3], 5, 0.1)
        # patches.append(polygon)
        circle = mpatches.Circle(grid[3], 0.05, ec="none")
        patches.append(circle)
        self.label(grid[3], self.node.display_name)

        # add an ellipse
        # ellipse = mpatches.Ellipse(grid[4], 0.2, 0.1)
        #patches.append(ellipse)
        # self.label(grid[4], "Ellipse")

        # add an arrow
        # arrow = mpatches.Arrow(grid[5, 0] - 0.05, grid[5, 1] - 0.05, 0.1, 0.1, width=0.1)
        # patches.append(arrow)
        # self.label(grid[5], "Arrow")

        # add a path patch
        # Path = mpath.Path
        # path_data = [
        # (Path.MOVETO, [0.018, -0.11]),
        # (Path.CURVE4, [-0.031, -0.051]),
        # (Path.CURVE4, [-0.115,  0.073]),
        # (Path.CURVE4, [-0.03 ,  0.073]),
        # (Path.LINETO, [-0.011,  0.039]),
        # (Path.CURVE4, [0.043,  0.121]),
        # (Path.CURVE4, [0.075, -0.005]),
        # (Path.CURVE4, [0.035, -0.027]),
        # (Path.CLOSEPOLY, [0.018, -0.11])
        # ]
        # codes, verts = zip(*path_data)
        # path = mpath.Path(verts + grid[6], codes)
        # patch = mpatches.PathPatch(path)
        # patches.append(patch)
        # self.label(grid[6], "PathPatch")

        # add a fancy box
        # fancybox = mpatches.FancyBboxPatch(
        #    grid[7] - [0.025, 0.05], 0.05, 0.1,
        #    boxstyle=mpatches.BoxStyle("Round", pad=0.02))
        # patches.append(fancybox)

        circle = mpatches.Circle(grid[7], 0.05, ec="none")
        patches.append(circle)
        self.label(grid[7], self.node[1].display_name)

        # add a line
        # x, y = np.array([[-0.06, 0.0, 0.1], [0.05, -0.05, 0.05]])
        # line = mlines.Line2D(x + grid[8, 0], y + grid[8, 1], lw=5., alpha=0.3)
        # self.label(grid[8], "Line2D")

        colors = np.linspace(0, 1, len(patches))

        collection = PatchCollection(patches, cmap=plt.cm.hsv, alpha=0.3)
        collection.set_array(np.array(colors))
        self.axes.add_collection(collection)
        # self.axes.add_line(line)

        # plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.axes.axis('equal')
        self.axes.axis('off')
        self.canvas.draw()

        # plt.show()

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
