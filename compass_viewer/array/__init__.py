# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Implements a viewer frame for compass_model.Array.
"""

import wx
import wx.grid
from wx.lib.newevent import NewCommandEvent

from .. import imagesupport

from ..frame import NodeFrame
from .plot import LinePlotFrame, ContourPlotFrame

# Indicates that the slicing selection may have changed.
# These events are emitted by the SlicerPanel.
ArraySlicedEvent, EVT_ARRAY_SLICED = NewCommandEvent()

# Menu and button IDs
ID_VIS_MENU_PLOT = wx.NewId()


class ArrayFrame(NodeFrame):

    """
    Top-level frame displaying objects of type compass_model.Array.

    From top to bottom, has:

    1. Toolbar (see ArrayFrame.init_toolbar)
    2. SlicerPanel, with controls for changing what's displayed.
    3. An ArrayGrid, which displays the data in a spreadsheet-like view.
    """

    def __init__(self, node, **kwds):
        """ Create a new array viewer, to display *node*. """
        NodeFrame.__init__(self, node, title=node.displayname, **kwds)

        self.node = node

        # The Slicer is the panel with indexing controls
        self.slicer = SlicerPanel(self, node.shape, node.dtype.fields is not None)
        self.grid = ArrayGrid(self, node, self.slicer)

        vis_menu = wx.Menu()
        vis_menu.Append(ID_VIS_MENU_PLOT, "Plot Data\tCtrl-D")
        self.add_menu(vis_menu, "Visualize")

        self.init_toolbar()

        gridsizer = wx.BoxSizer(wx.VERTICAL)
        gridsizer.Add(self.slicer, 0, wx.EXPAND)
        gridsizer.Add(self.grid, 1, wx.EXPAND)

        self.view = gridsizer

        self.Bind(EVT_ARRAY_SLICED, self.on_sliced)
        self.Bind(wx.EVT_MENU, self.on_plot, id=ID_VIS_MENU_PLOT)

        # Workaround for wxPython bug (see SlicerPanel.enable_spinctrls)
        ID_WORKAROUND_TIMER = wx.NewId()
        self.Bind(wx.EVT_TIMER, self.on_workaround_timer, id=ID_WORKAROUND_TIMER)
        self.timer = wx.Timer(self, ID_WORKAROUND_TIMER)
        self.timer.Start(100)


    def on_workaround_timer(self, evt):
        """ See slicer.enable_spinctrls docs """
        self.timer.Destroy()
        self.slicer.enable_spinctrls()


    def init_toolbar(self):
        """ Set up the toolbar at the top of the window. """
        tsize = (24,24)
        plot_bmp = imagesupport.getbitmap('viz_plot_24')

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT|wx.TB_TEXT)

        self.toolbar.SetToolBitmapSize(tsize)
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddLabelTool(ID_VIS_MENU_PLOT, "Plot Data", plot_bmp, shortHelp="Plot data in a popup window", longHelp="Long help for 'New'")
        self.toolbar.Realize()


    def on_sliced(self, evt):
        """ User has chosen to display a different part of the dataset. """
        self.grid.Refresh()


    def on_plot(self, evt):
        """ User has chosen to plot the current selection """
        cols = self.grid.GetSelectedCols()
        rows = self.grid.GetSelectedRows()

        # Scalar data can't be line-plotted.
        if len(self.node.shape) == 0:
            return

        # Columns in the view are selected
        if len(cols) != 0:

            # The data is compound
            if self.node.dtype.names is not None:
                names = [self.grid.GetColLabelValue(x) for x in cols]
                data = self.node[self.slicer.indices]  # -> 1D compound array
                data = [data[n] for n in names]
                f = LinePlotFrame(data, names)
                f.Show()

            # Plot multiple columns independently
            else:
                if len(self.node.shape) == 1:
                    data = [self.node[self.slicer.indices]]
                else:
                    data = [self.node[self.slicer.indices+(c,)] for c in cols]

                names = ["Col %d"%c for c in cols] if len(data) > 1 else None

                f = LinePlotFrame(data, names)
                f.Show()


        # Rows in view are selected
        elif len(rows) != 0:
        
            data = [self.node[self.slicer.indices+(slice(None,None,None),r)] for r in rows]
            names = ["Row %d"%r for r in rows] if len(data) > 1 else None

            f = LinePlotFrame(data, names)
            f.Show()


        # No row or column selection.  Plot everything
        else:

            data = self.node[self.slicer.indices]

            # The data is compound
            if self.node.dtype.names is not None:
                names = [self.grid.GetColLabelValue(x) for x in xrange(self.grid.GetNumberCols())]
                data = [data[n] for n in names]
                f = LinePlotFrame(data, names)
                f.Show()

            # Plot 1D
            elif len(self.node.shape) == 1:
                f = LinePlotFrame([data])
                f.Show()

            # Plot 2D
            else:
                f = ContourPlotFrame(data)
                f.Show()


class SlicerPanel(wx.Panel):

    """
    Holds controls for data access.

    Consult the "indices" property, which returns a tuple of indices that
    prefix the array.  This will be RANK-2 elements long, unless hasfields
    is true, in which case it will be RANK-1 elements long.
    """

    @property
    def indices(self):
        """ A tuple of integer indices appropriate for slicing.

        Will be RANK-2 elements long, RANK-1 if compound data is in use
        (hasfields == True).
        """
        return tuple([x.GetValue() for x in self.spincontrols])


    def __init__(self, parent, shape, hasfields):
        """ Create a new slicer panel.

        parent:     The wxPython parent window
        shape:      Shape of the data to visualize
        hasfields:  If True, the data is compound and the grid can only
                    display one axis.  So, we should display an extra spinbox.
        """
        wx.Panel.__init__(self, parent)

        self.shape = shape
        self.hasfields = hasfields
        self.spincontrols = []

        # Rank of the underlying array
        rank = len(shape)

        # Rank displayable in the grid.  If fields are present, they occupy
        # the columns, so the data displayed is actually 1-D.
        visible_rank = 1 if hasfields else 2

        sizer = wx.BoxSizer(wx.HORIZONTAL)  # Will arrange the SpinCtrls

        if rank > visible_rank:
            infotext = wx.StaticText(self, wx.ID_ANY, "Array Indexing: ")
            sizer.Add(infotext, 0, flag=wx.EXPAND|wx.ALL, border=10)

            for idx in xrange(rank-visible_rank):
                sc = wx.SpinCtrl(self, max=shape[idx]-1, value="0", min=0)
                sizer.Add(sc, 0, flag=wx.EXPAND|wx.ALL, border=10)
                sc.Disable()
                self.spincontrols.append(sc)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_SPINCTRL, self.on_spin)


    def enable_spinctrls(self):
        """ Unlock the spin controls.

        Because of a bug in wxPython on Mac, by default the first spin control
        has bizarre contents (and control focus) when the panel starts up.
        Call this after a short delay (e.g. 100 ms) to enable indexing.
        """
        for sc in self.spincontrols:
            sc.Enable()


    def on_spin(self, evt):
        """ Spinbox value changed; notify parent to refresh the grid. """
        wx.PostEvent(self, ArraySlicedEvent(self.GetId()))



class ArrayGrid(wx.grid.Grid):

    """
    Grid class to display the Array.
    
    Cell contents and appearance are handled by the table model in ArrayTable.
    """

    def __init__(self, parent, node, slicer):
        wx.grid.Grid.__init__(self, parent)
        table = ArrayTable(node, slicer)
        self.SetTable(table, True)

        # Column selection is always allowed
        selmode = wx.grid.Grid.wxGridSelectColumns

        # Row selection is forbidden for compound types, and for
        # scalar/1-D datasets
        if node.dtype.names is None and len(node.shape) > 1:
            selmode |= wx.grid.Grid.wxGridSelectRows

        self.SetSelectionMode(selmode)



class ArrayTable(wx.grid.PyGridTableBase):

    """
    "Table" class which provides data and metadata for the grid to display.

    The methods defined here define the contents of the table, as well as
    the number of rows, columns and their values.
    """

    def __init__(self, node, slicer):
        """ Create a new Table instance for use with a grid control.

        node:     An compass_model.Array implementation instance.
        slicer:   An instance of SlicerPanel, so we can see what indices the
                  user has requested.
        """
        wx.grid.PyGridTableBase.__init__(self)

        self.node = node
        self.slicer = slicer

        self.rank = len(node.shape)
        self.names = node.dtype.names


    def GetNumberRows(self):
        """ Callback for number of rows displayed by the grid control """
        if self.rank == 0:
            return 1
        return self.node.shape[-1]


    def GetNumberCols(self):
        """ Callback for number of columns displayed by the grid control.

        Note that if compound data is in use, columns display the field names.
        """
        if self.names is not None:
            return len(self.names)
        if self.rank < 2:
            return 1
        return self.node.shape[-2]


    def GetValue(self, row, col):
        """ Callback which provides data to the Grid.

        row, col:   Integers giving row and column position (0-based).
        """
        # Scalar case
        if self.rank == 0:  
            data = self.node[()]
            if self.names is None:
                return data
            return data[col]

        # 1D case
        if self.rank == 1:
            data = self.node[row]
            if self.names is None:
                return data
            return data[self.names[col]]

        # ND case.  Watch out for compound mode!
        if self.names is None:
            args = self.slicer.indices + (col,row)
        else:
            args = self.slicer.indices + (row,)

        data = self.node[args]
        if self.names is None:
            return data
        return data[self.names[col]]


    def GetRowLabelValue(self, row):
        """ Callback for row labels.

        Row number is used unless the data is scalar.
        """
        if self.rank == 0:
            return "Value"
        return str(row)


    def GetColLabelValue(self, col):
        """ Callback for column labels.

        Column number is used, except for scalar or 1D data, or if we're
        displaying field names in the columns.
        """
        if self.names is not None:
            return self.names[col]
        if self.rank == 0 or self.rank == 1:
            return "Value"
        return str(col)
