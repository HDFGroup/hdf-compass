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
Main module for HDFCompass.

Defines the App class, along with supporting infrastructure.
"""

# Must be at the top, to ensure we're the first to call matplotlib.use.
import matplotlib
matplotlib.use('WXAgg')

import wx

from hdf_compass import compass_model

from .imagesupport import png_to_bitmap
from . import platform
from .events import ID_COMPASS_OPEN
from . import container, array, keyvalue, image, frame

__version__ = platform.VERSION


class CompassImageList(wx.ImageList):

    """
    A specialized type of image list, to support icons from Node subclasses.

    Instances of this class hold only square icons, of the size specified
    when created.  The appropriate icon index for a particular Node subclass is
    retrieved using get_index(nodeclass).

    Image addition and indexing is completely bootstrapped; there's no need
    to manually add or register Node classes with this class.  Just call
    get_index and the object will figure it out.
    """

    def __init__(self, size):
        """ Create a new list holding square icons of the given size. """
        wx.ImageList.__init__(self, size, size)
        self._indices = {}
        self._size = size

    def get_index(self, nodeclass):
        """ Retrieve an index appropriate for the given Node subclass. """

        if nodeclass not in self._indices:
            png = nodeclass.icons[self._size]()
            idx = self.Add(png_to_bitmap(png))
            self._indices[nodeclass] = idx

        return self._indices[nodeclass]


class CompassApp(wx.App):

    """
    The main application object for HDFCompass.

    This mainly handles ID_COMPASS_OPEN events, which are requests to launch
    a new window viewing a particular node.  Also contains a dict of
    CompassImageLists, indexed by image width.
    """

    def __init__(self, redirect):
        """ Constructor.  If *redirect*, show a windows with console output.
        """
        wx.App.__init__(self, redirect)

        self.imagelists = {}
        for size in (16, 24, 32, 48, 64):
            self.imagelists[size] = CompassImageList(size)

        self.Bind(wx.EVT_MENU, self.on_compass_open, id=ID_COMPASS_OPEN)

        self.SetAppName("HDFCompass")


    def on_compass_open(self, evt):
        """ A request has been made to open a node from somewhere in the GUI
        """
        open_node(evt.node, evt.kwds.get('pos'))


    def MacOpenFile(self, filename):
        """ A file has been dropped onto the app icon """
        url = 'file://'+filename
        open_store(url)


def open_node(node, pos=None):
    """ Open a viewer frame appropriate for the given Node instance.
    
    node:   Node instance to open
    pos:    2-tuple with current window position (used to avoid overlap).
    """
    
    if pos is not None:
        # The thing we get from GetPosition isn't really a tuple, so
        # you have to manually cast entries to int or it silently fails.
        newpos =(int(pos[0])+40, int(pos[1])+40)
    else:
        newpos = None

    print "Top-level open called for ", node

    if isinstance(node, compass_model.Container):
        f = container.ContainerFrame(node, pos=newpos)
        f.Show()
    elif isinstance(node, compass_model.Array):
        f = array.ArrayFrame(node, pos=newpos)
        f.Show()
    elif isinstance(node, compass_model.KeyValue):
        f = keyvalue.KeyValueFrame(node, pos=newpos)
        f.Show()
    elif isinstance(node, compass_model.Image):
        f = image.ImageFrame(node, pos=pos)
        f.Show()
    else:
        pass

        
def open_store(url):
    """ Open the url using the first matching registered Store class.

    Returns True if the url was successfully opened, False otherwise.
    """
    stores = [x for x in compass_model.getstores() if x.canhandle(url)]

    if len(stores) > 0:
        instance = stores[0](url)
        open_node(instance.root)
        return True

    return False


def load_plugins():
    """ Helper function that attempts to load all the plugins """

    from hdf_compass import compass_model

    try:
        from hdf_compass import filesystem_model
    except ImportError:
        print("Filesystem plugin not loaded")

    try:
        from hdf_compass import array_model
    except ImportError:
        print("Array plugin not loaded")

    try:
        from hdf_compass import hdf5_model
    except ImportError:
        print("HDF plugin not loaded")

    # Coming soon!
    # try:
    #     from hdf_compass import bag_model
    # except ImportError:
    #     print("BAG plugin not loaded")

    try:
        from hdf_compass import asc_model
    except ImportError:
        print("Ascii grid plugin not loaded")

    try:
        from hdf_compass import opendap_model
    except ImportError:
        print("Opendap plugin not loaded")


def run():
    """ Run HDFCompass.  Handles all command-line arguments, etc.
    """

    import sys
    import os.path as op

    app = CompassApp(False)

    load_plugins()

    urls = sys.argv[1:]
    
    for url in urls:
        if "://" not in url:
            # assumed to be file path
            if sys.platform == 'win32':
                url = 'file:///' + op.abspath(url)
            else:
                url = 'file://' + op.abspath(url)
        if not open_store(url):
            print 'Failed to open "%s"; no handlers'%url

    f = frame.InitFrame()
    
    if platform.MAC:
        wx.MenuBar.MacSetCommonMenuBar(f.GetMenuBar())
    else:
        f.Show()
        
    app.MainLoop()
