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

import numpy as np
import wx

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

from ..frame import BaseFrame


class PlotFrame(BaseFrame):

    """
    Base class for Matplotlib plot windows.

    Override draw_figure() to plot your figure on the provided axes.
    """

    def __init__(self, data):
        """ Create a new Matplotlib plotting window for a 1D line plot
        """

        BaseFrame.__init__(self, id=wx.ID_ANY, title="Line plot", size=(800,400))
        
        self.data = data

        self.panel = wx.Panel(self)
        
        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.axes = self.fig.add_subplot(111)
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

    def __init__(self, data, names=None):
        self.names = names
        PlotFrame.__init__(self, data)


    def draw_figure(self):

        lines = [self.axes.plot(d)[0] for d in self.data]
        if self.names is not None:
            for n in self.names:
                self.axes.legend(tuple(lines), tuple(self.names))
        

class ContourPlotFrame(PlotFrame):

    def draw_figure(self):
        import pylab
        xx = np.arange(self.data.shape[1])
        yy = np.arange(self.data.shape[0])
        out = self.axes.contourf(xx, yy, self.data, 25)
        pylab.colorbar(out)
