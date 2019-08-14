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
Matplotlib window with toolbar.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import wx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar

import logging
log = logging.getLogger(__name__)

from ..frame import BaseFrame

ID_VIEW_CMAP_JET = wx.NewId()  # default
ID_VIEW_CMAP_BONE = wx.NewId()
ID_VIEW_CMAP_GIST_EARTH = wx.NewId()
ID_VIEW_CMAP_OCEAN = wx.NewId()
ID_VIEW_CMAP_RAINBOW = wx.NewId()
ID_VIEW_CMAP_RDYLGN = wx.NewId()
ID_VIEW_CMAP_WINTER = wx.NewId()


class PlotFrame(BaseFrame):
    """ Base class for Matplotlib plot windows.

    Override draw_figure() to plot your figure on the provided axes.
    """

    def __init__(self, data, title="a title"):
        """ Create a new Matplotlib plotting window for a 1D line plot """

        log.debug(self.__class__.__name__)
        BaseFrame.__init__(self, id=wx.ID_ANY, title=title, size=(800, 400))

        self.data = data

        self.panel = wx.Panel(self)

        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel('')
        self.axes.set_ylabel('')

        self.toolbar = NavigationToolbar(self.canvas)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        self.draw_figure()

    def draw_figure(self):
        raise NotImplementedError


class LinePlotFrame(PlotFrame):
    def __init__(self, data, names=None, title="Line Plot"):
        self.names = names
        PlotFrame.__init__(self, data, title)

    def draw_figure(self):
        lines = [self.axes.plot(d)[0] for d in self.data]
        if self.names is not None:
            for n in self.names:
                self.axes.legend(tuple(lines), tuple(self.names))

class LineXYPlotFrame(PlotFrame):
    def __init__(self, data, names=None, title="Line XY Plot"):
        self.names = names
        PlotFrame.__init__(self, data, title)

    def draw_figure(self):
        self.axes.set_xlabel(self.names[0])
        if len(self.data)==2:
            # a simple X-Y plot using 2 columns
            self.axes.set_ylabel(self.names[1])

        lines = [self.axes.plot(self.data[0], d)[0] for d in self.data[1::]]
        if self.names is not None:
            for n in self.names:
                self.axes.legend(tuple(lines), tuple(self.names[1::]))

class ContourPlotFrame(PlotFrame):
    def __init__(self, data, names=None, title="Contour Plot"):
        # need to be set before calling the parent (need for plotting)
        self.colormap = "jet"
        self.cb = None  # matplotlib color-bar

        PlotFrame.__init__(self, data, title)

        self.cmap_menu = wx.Menu()
        self.cmap_menu.Append(ID_VIEW_CMAP_JET, "Jet", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_BONE, "Bone", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_GIST_EARTH, "Gist Earth", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_OCEAN, "Ocean", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_RAINBOW, "Rainbow", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_RDYLGN, "Red-Yellow-Green", kind=wx.ITEM_RADIO)
        self.cmap_menu.Append(ID_VIEW_CMAP_WINTER, "Winter", kind=wx.ITEM_RADIO)
        self.add_menu(self.cmap_menu, "Colormap")

        self.Bind(wx.EVT_MENU, self.on_cmap_jet, id=ID_VIEW_CMAP_JET)
        self.Bind(wx.EVT_MENU, self.on_cmap_bone, id=ID_VIEW_CMAP_BONE)
        self.Bind(wx.EVT_MENU, self.on_cmap_gist_earth, id=ID_VIEW_CMAP_GIST_EARTH)
        self.Bind(wx.EVT_MENU, self.on_cmap_ocean, id=ID_VIEW_CMAP_OCEAN)
        self.Bind(wx.EVT_MENU, self.on_cmap_rainbow, id=ID_VIEW_CMAP_RAINBOW)
        self.Bind(wx.EVT_MENU, self.on_cmap_rdylgn, id=ID_VIEW_CMAP_RDYLGN)
        self.Bind(wx.EVT_MENU, self.on_cmap_winter, id=ID_VIEW_CMAP_WINTER)

        self.status_bar = wx.StatusBar(self, -1)
        self.status_bar.SetFieldsCount(2)
        self.SetStatusBar(self.status_bar)

        self.canvas.mpl_connect('motion_notify_event', self.update_status_bar)
        self.canvas.Bind(wx.EVT_ENTER_WINDOW, self.change_cursor)

    def on_cmap_jet(self, evt):
        log.debug("cmap: jet")
        self.colormap = "jet"
        self._refresh_plot()

    def on_cmap_bone(self, evt):
        log.debug("cmap: bone")
        self.colormap = "bone"
        self._refresh_plot()

    def on_cmap_gist_earth(self, evt):
        log.debug("cmap: gist_earth")
        self.colormap = "gist_earth"
        self._refresh_plot()

    def on_cmap_ocean(self, evt):
        log.debug("cmap: ocean")
        self.colormap = "ocean"
        self._refresh_plot()

    def on_cmap_rainbow(self, evt):
        log.debug("cmap: rainbow")
        self.colormap = "rainbow"
        self._refresh_plot()

    def on_cmap_rdylgn(self, evt):
        log.debug("cmap: RdYlGn")
        self.colormap = "RdYlGn"
        self._refresh_plot()

    def on_cmap_winter(self, evt):
        log.debug("cmap: winter")
        self.colormap = "winter"
        self._refresh_plot()

    def _refresh_plot(self):
        self.draw_figure()
        self.canvas.draw()

    def draw_figure(self):
        max_elements = 500  # don't attempt plot more than 500x500 elements
        rows = self.data.shape[0]
        cols = self.data.shape[1]
        row_stride = rows // max_elements + 1
        col_stride = cols // max_elements + 1
        data = self.data[::row_stride, ::col_stride]
        xx = np.arange(0, self.data.shape[1], col_stride)
        yy = np.arange(0, self.data.shape[0], row_stride)
        img = self.axes.contourf(xx, yy, data, 25, cmap=plt.cm.get_cmap(self.colormap))
        self.axes.set_aspect('equal')
        if self.cb:
            self.cb.on_mappable_changed(img)
        else:
            self.cb = plt.colorbar(img, ax=self.axes)
        self.cb.ax.tick_params(labelsize=8)

    def change_cursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

    def update_status_bar(self, event):
        msg = str()
        if event.inaxes:
            x, y = int(event.xdata), int(event.ydata)
            z = self.data[y, x]
            msg = "x= %d, y= %d, z= %f" % (x, y, z)
        self.status_bar.SetStatusText(msg, 1)
