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
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
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

        self.axes = self.fig.add_subplot(111, projection=ccrs.PlateCarree())
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


class ContourPlotFrame(PlotFrame):
    def __init__(self, data, extent, names=None, title="Contour Map"):
        self.geo_extent = extent
        log.debug("Extent: %f, %f, %f, %f" % self.geo_extent)
        # need to be set before calling the parent (need for plotting)
        self.colormap = "jet"
        self.cb = None  # matplotlib color-bar
        self.surf = None
        self.xx = None
        self.yy = None

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
        self.surf = self.data[::row_stride, ::col_stride]
        self.xx = np.linspace(self.geo_extent[0], self.geo_extent[1], self.surf.shape[1])
        self.yy = np.linspace(self.geo_extent[2], self.geo_extent[3], self.surf.shape[0])
        img = self.axes.contourf(self.xx, self.yy, self.surf, 25, cmap=plt.cm.get_cmap(self.colormap),
                                 transform=ccrs.PlateCarree())
        self.axes.coastlines(resolution='50m', color='gray', linewidth=1)
        # add gridlines with labels only on the left and on the bottom
        grl = self.axes.gridlines(crs=ccrs.PlateCarree(), color='gray', draw_labels=True)
        grl.xformatter = LONGITUDE_FORMATTER
        grl.yformatter = LATITUDE_FORMATTER
        grl.xlabel_style = {'size': 8}
        grl.ylabel_style = {'size': 8}
        grl.ylabels_right = False
        grl.xlabels_top = False

        if self.cb:
            self.cb.on_mappable_changed(img)
        else:
            self.cb = plt.colorbar(img, ax=self.axes)
        self.cb.ax.tick_params(labelsize=8)

    def change_cursor(self, event):
        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

    @staticmethod
    def _find_nearest(arr, value):
        """ Helper function to find the nearest value in an array """
        return (np.abs(arr - value)).argmin()

    def update_status_bar(self, event):
        msg = str()
        if event.inaxes:
            x, y = event.xdata, event.ydata
            id_y, id_x = self._find_nearest(self.yy, y), self._find_nearest(self.xx, x)
            # log.debug("id: %f %f" % (id_y, id_x))
            z = self.surf[id_y, id_x]
            msg = "x= %f, y= %f, z= %f" % (x, y, z)
        self.status_bar.SetStatusText(msg, 1)
