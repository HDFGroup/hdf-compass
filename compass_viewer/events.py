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
Defines a small number of custom events, which are useful for the GUI.
"""

import wx
from wx.lib.newevent import NewCommandEvent

ID_COMPASS_OPEN = wx.NewId()


class CompassOpenEvent(wx.PyCommandEvent):

    """
    Event posted when a request has been made to "open" a object in
    the container.  The source should always be ID_COMPASS_OPEN.

    The type of event is EVT_MENU, because wxPython doesn't like it if we
    use anything else.  When binding handlers, make sure to explicitly
    specify the source ID (or check it in the callback) to avoid catching
    these events by mistake.
    """
    
    def __init__(self, newnode, **kwds):
        """ Request that *newnode* be displayed by the GUI """
        wx.PyCommandEvent.__init__(self, wx.EVT_MENU.typeId, ID_COMPASS_OPEN)
        self.node = newnode
        self.kwds = kwds


# Hints that the selected item in the view may have changed.
# Interested parties should inspect the view to figure out the new selection.
ContainerSelectionEvent, EVT_CONTAINER_SELECTION = NewCommandEvent()
