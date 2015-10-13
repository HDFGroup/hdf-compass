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
from __future__ import absolute_import, division, print_function, unicode_literals

# Must be at the top, to ensure we're the first to call matplotlib.use.
import matplotlib
matplotlib.use('WXAgg')

import wx

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from hdf_compass import compass_model
from hdf_compass import utils

from .events import ID_COMPASS_OPEN
from . import container, array, keyvalue, image, frame, text

__version__ = utils.__version__


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

    def get_index(self, node_class):
        """ Retrieve an index appropriate for the given Node subclass. """

        if node_class not in self._indices:
            png = wx.Bitmap(node_class.icons[self._size], wx.BITMAP_TYPE_ANY)
            idx = self.Add(png)
            self._indices[node_class] = idx

        return self._indices[node_class]


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
        new_pos =(int(pos[0])+40, int(pos[1])+40)
    else:
        new_pos = None

    log.debug("Top-level open called for %s" % node)

    if isinstance(node, compass_model.Container):
        f = container.ContainerFrame(node, pos=new_pos)
        f.Show()

    elif isinstance(node, compass_model.Array):
        f = array.ArrayFrame(node, pos=new_pos)
        f.Show()

    elif isinstance(node, compass_model.Xml):
        f = text.XmlFrame(node, pos=new_pos)
        f.Show()

    elif isinstance(node, compass_model.Text):
        f = text.TextFrame(node, pos=new_pos)
        f.Show()

    elif isinstance(node, compass_model.KeyValue):
        f = keyvalue.KeyValueFrame(node, pos=new_pos)
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
    stores = [x for x in compass_model.get_stores() if x.can_handle(url)]

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
        log.info("Filesystem plugin not loaded")

    try:
        from hdf_compass import array_model
    except ImportError:
        log.info("Array plugin not loaded")

    try:
        from hdf_compass import hdf5_model
    except ImportError:
        log.info("HDF plugin not loaded")

    try:
        from hdf_compass import bag_model
    except ImportError:
        log.info("BAG plugin not loaded")

    try:
        from hdf_compass import asc_model
    except ImportError:
        log.info("Ascii grid plugin not loaded")

    try:
        from hdf_compass import opendap_model
    except ImportError:
        log.info("Opendap plugin not loaded")


def run():
    """ Run HDFCompass.  Handles all command-line arguments, etc.
    """

<<<<<<< HEAD:compass_viewer/__init__.py
    # These are imported to register their classes with
    # compass_model.  We don't use them directly.
    import filesystem_model
    import array_model
    import hdf5_model
    import asc_model
    # todo - disabling opendap module for now due to installer issues
    import opendap_model

=======
>>>>>>> develop:hdf_compass/compass_viewer/__init__.py
    import sys
    import os.path as op

    app = CompassApp(False)

    load_plugins()

    urls = sys.argv[1:]
    
    for url in urls:
        if "://" not in url:
            # assumed to be file path
            if utils.is_win:
                url = 'file:///' + op.abspath(url)
            else:
                url = 'file://' + op.abspath(url)
        if not open_store(url):
            log.warning('Failed to open "%s"; no handlers' % url)

    f = frame.InitFrame()
    
    if utils.is_darwin:
        wx.MenuBar.MacSetCommonMenuBar(f.GetMenuBar())
    else:
        f.Show()
        
    app.MainLoop()
