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
Defines wx.Frame subclasses which are the foundation of the various windows
displayed by HDFCompass.

Much of the common functionality (e.g. "Open File..." menu item) is implemented
here.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
from datetime import date
import wx
from wx.lib.pubsub import pub

import logging
log = logging.getLogger(__name__)

from .info import InfoPanel

ID_OPEN_RESOURCE = wx.NewId()
ID_CLOSE_FILE = wx.NewId()

MAX_RECENT_FILES = 8

from hdf_compass import compass_model
from hdf_compass.utils import __version__, is_darwin, url2path, path2url
from .events import CompassOpenEvent


class BaseFrame(wx.Frame):

    """
    Base class for all frames used in HDF Compass.

    Implements common menus including File and Help, and handles their
    events.

    When implementing a new viewer window, you should instead inherit from
    BaseFrame (below), which adds a left-hand side information panel, and
    participates in the reference counting that automatically shows the
    initial window when all other frames are closed.
    """

    icon_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons'))

    def __init__(self, **kwds):
        """ Constructor; any keywords are passed on to wx.Frame.
        """

        wx.Frame.__init__(self, None, **kwds) 
        
        # Frame icon
        ib = wx.IconBundle()
        icon_32 = wx.EmptyIcon()
        icon_32.CopyFromBitmap(wx.Bitmap(os.path.join(self.icon_folder, "compass_32.png"), wx.BITMAP_TYPE_ANY))
        ib.AddIcon(icon_32)
        icon_48 = wx.EmptyIcon()
        icon_48.CopyFromBitmap(wx.Bitmap(os.path.join(self.icon_folder, "compass_48.png"), wx.BITMAP_TYPE_ANY))
        ib.AddIcon(icon_48)
        self.SetIcons(ib)

        # This is needed to display the app icon on the taskbar on Windows 7
        if os.name == 'nt':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('HDFCompass')
        self.urlhistory = wx.FileHistory(MAX_RECENT_FILES)
        self.config = wx.Config("HDFCompass", style=wx.CONFIG_USE_LOCAL_FILE)
        self.urlhistory.Load(self.config) 
        menubar = wx.MenuBar()

        # File menu
        fm = wx.Menu()
        
        # Open Recent Menu
        recent = wx.Menu()
        self.urlhistory.UseMenu(recent)
        self.urlhistory.AddFilesToMenu()

        fm.Append(wx.ID_OPEN, "&Open...\tCtrl-O")
        fm.Append(ID_OPEN_RESOURCE, "Open &Resource...\tCtrl-R")
        fm.AppendMenu(wx.ID_ANY, "O&pen Recent", recent)

        fm.AppendSeparator()
 
        fm.Append(wx.ID_CLOSE, "&Close Window\tCtrl-W")
        fm.Append(ID_CLOSE_FILE, "Close &File\tShift-Ctrl-W")
        fm.Enable(ID_CLOSE_FILE, False)
        fm.Append(wx.ID_EXIT,"E&xit"," Terminate the program")   
        
        menubar.Append(fm, "&File")

        # Help menu; note that on the Mac, the About entry is automatically
        # moved to the main application menu by wxPython.
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About HDFCompass"," Information about this program")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_window_close, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.on_file_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_resource_open, id=ID_OPEN_RESOURCE)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU_RANGE, self.on_url_history, id=wx.ID_FILE1, id2=wx.ID_FILE9)

    def on_exit(self, evt):
        """ Called on "exit" event from the menu """
        wx.GetApp().Exit()

    def on_about(self, evt):
        """ Display an "About" dialog """
        info = wx.AboutDialogInfo()
        info.Name = "HDFCompass"
        info.Version = __version__
        info.Copyright = "(c) 2014-%d The HDF Group" % date.today().year
        icon_48 = wx.EmptyIcon()
        icon_48.CopyFromBitmap(wx.Bitmap(os.path.join(self.icon_folder, "compass_48.png"), wx.BITMAP_TYPE_ANY))
        info.SetIcon(icon_48)
        wx.AboutBox(info)

    def on_file_open(self, evt):
        """ Request to open a file via the Open entry in the File menu """

        def make_filter_string():
            """ Make a wxPython dialog filter string segment from dict """
            filter_string = []
            hdf_filter_string = []  # put HDF filters in the front
            for store in compass_model.get_stores():
                if len(store.file_extensions) == 0:
                    continue
                for key in store.file_extensions:
                    s = "{name} ({pattern_c})|{pattern_sc}".format(
                        name=key, 
                        pattern_c=",".join(store.file_extensions[key]),
                        pattern_sc=";".join(store.file_extensions[key]) )
                    if s.startswith("HDF"):
                        hdf_filter_string.append(s)
                    else:
                        filter_string.append(s)
            filter_string = hdf_filter_string + filter_string
            filter_string.append('All Files (*.*)|*.*')
            pipe = "|"
            return pipe.join(filter_string)
            
        # The wxPython wildcard string is a bunch of filter strings pasted together
        # wc_string = [s.file_extensions for s in compass_model.get_stores() if len(s.file_extensions) != 0]
        # print "jlr -- wc_string: " , wc_string
        # wc_string.append({"All Files": ["*"]})
        # wc_string = "|".join([make_filter_string(x) for x in wc_string])
        #wc_string.append("|")
        #wc_string.append(make_filter_string(wc_string))
        wc_string = make_filter_string()
        
        dlg = wx.FileDialog(self, "Open Local File", wildcard=wc_string, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()

        url = path2url(path)
        self.open_url(url)
    
    def on_url_history(self, evt):
        """ Opens url from history """
        fileNum = evt.GetId() - wx.ID_FILE1
        url = self.urlhistory.GetHistoryFile(fileNum)
        self.open_url(url, fileNum)
            
    def on_window_close(self, evt):
        """ Close Window file event, or cmd-W """
        self.Destroy()

    def on_resource_open(self, evt):
        """ Request to open a URL via the File menu """
        dlg = wx.TextEntryDialog(self, 'Enter resource URL:')

        if dlg.ShowModal() != wx.ID_OK or dlg.GetValue() == "":
            dlg.Destroy()
            return

        url = dlg.GetValue()
        url = url.strip()  # remove any new lines
        dlg.Destroy()
        self.open_url(url)

    def open_url(self, url, fileNum=-1):
        """ Opens url and saves it to history """
        from . import can_open_store, open_store
        if can_open_store(url):
            self.urlhistory.AddFileToHistory(url) # add url to top of list
            self.urlhistory.Save(self.config)
            self.config.Flush()
            open_store(url)
        else:
            if fileNum >= 0 and fileNum < MAX_RECENT_FILES:
                self.urlhistory.RemoveFileFromHistory(fileNum)
                self.urlhistory.Save(self.config)
                self.config.Flush()
            dlg = wx.MessageDialog(self, 'The following url could not be opened:\n\n%s' % url,
                                   'No handler for url', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def add_menu(self, menu, title):
        """ Add a menu at the appropriate place in the menubar """
        mb = self.GetMenuBar()
        mb.Insert(1, menu, title)


class InitFrame(BaseFrame):

    """
    Frame displayed when the application starts up.

    This includes the menu bar provided by TopFrame.  On the Mac, although it
    still exists (to prevent the application from exiting), the frame
    is typically not shown.
    """

    def __init__(self):
        
        style = wx.DEFAULT_FRAME_STYLE & (~wx.RESIZE_BORDER) & (~wx.MAXIMIZE_BOX)
        title = "HDFCompass"
        BaseFrame.__init__(self, size=(552,247), title=title, style=style)

        data = wx.Bitmap(os.path.join(self.icon_folder, "logo.png"), wx.BITMAP_TYPE_ANY)
        bmp = wx.StaticBitmap(self, wx.ID_ANY, data)

        # The init frame isn't visible on Mac, so there shouldn't be an
        # option to close it.  "Quit" does the same thing.
        if is_darwin:
            mb = self.GetMenuBar()
            mu = mb.GetMenu(0)
            mu.Enable(wx.ID_CLOSE, False)
        self.Center()
            
            
class NodeFrame(BaseFrame):

    """
    Base class for any frame which displays a Node instance.

    Provides a "Close file" menu item and manages open data stores.

    Has three attributes of note:

    .node:  Settable Node instance to display
    .info:  Read-only InfoPanel instance (left-hand sidebar)
    .view:  Settable wx.Panel instance for the right-hand view.

    In order to coordinate file-close events across multiple frames,
    a reference-counting system is used.  When a new frame that uses a store
    is created, that store's reference count (in cls._stores) is incremented.
    When the frame is closed, the store's count is decremented.  

    When the reference count reaches 0 or the "Close File" is selected from the
    menu, the store is closed and a pubsub notification is sent out to all
    other frames.  They check to see if their .node.store's are valid, and
    if not, close themselves.
    """

    # --- Store reference-counting methods ------------------------------------

    _stores = {}

    @classmethod
    def _incref(cls, store):
        """ Record that a client is using the specified store. """
        try:
            cls._stores[store] = cls._stores[store] + 1
        except KeyError:
            cls._stores[store] = 1

    @classmethod
    def _decref(cls, store):
        """ Record that a client is finished using the specified store. """
        try:
            val = cls._stores[store]
            if val == 1:
                cls._close(store)
                del cls._stores[store]
            else:
                cls._stores[store] = val-1
        except KeyError:
            pass

    @classmethod
    def _close(cls, store):
        """ Manually close the store, and broadcast a pubsub notification.
        """
        cls._stores.pop(store, None)
        store.close()
        pub.sendMessage('store.close')

    # --- End store reference-counting ----------------------------------------

    @property
    def info(self):
        """ The InfoPanel object used for the left-hand sidebar.
        """
        return self.__info

    @property
    def node(self):
        """ Node instance displayed by the frame. """
        return self.__node

    @node.setter
    def node(self, newnode):
        self.__node = newnode

    @property
    def view(self):
        """ Right-hand view """
        return self.__view

    @view.setter
    def view(self, window):
        if self.__view is None:
            self.__sizer.Add(window, 1, wx.EXPAND)
        else:
            self.__sizer.Remove(self.__view)
            self.__view.Destroy()
            self.__sizer.Add(window, 1, wx.EXPAND)
        self.__view = window
        self.Layout()

    def __init__(self, node, **kwds):
        """ Constructor.  Keywords are passed on to wx.Frame.

        node:   The compass_model.Node instance to display.
        """

        BaseFrame.__init__(self, **kwds)

        # Enable the "Close File" menu entry
        fm = self.GetMenuBar().GetMenu(0)
        fm.Enable(ID_CLOSE_FILE, True)

        # Create the "window" menu to hold "Reopen As" items.
        wm = wx.Menu()

        # Determine a list of handlers which can understand this object.
        # We exclude the default handler, "Unknown", as it can't do anything.
        # See also container/list.py.
        handlers = [x for x in node.store.gethandlers(node.key) if x != compass_model.Unknown]

        # This will map menu IDs -> Node subclass handlers
        self._menu_handlers = {}

        # Note there's guaranteed to be at least one entry: the class
        # being used for the current frame!
        for h in handlers:
            id_ = wx.NewId()
            self._menu_handlers[id_] = h
            wm.Append(id_, "Reopen as " + h.class_kind)
            self.Bind(wx.EVT_MENU, self.on_menu_reopen, id=id_)
            
        self.GetMenuBar().Insert(1, wm, "&Window")
        
        self.__node = node
        self.__view = None
        self.__info = InfoPanel(self)

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer.Add(self.__info, 0, wx.EXPAND)
        self.SetSizer(self.__sizer)

        self.info.display(node)

        self.Bind(wx.EVT_CLOSE, self.on_close_evt)
        self.Bind(wx.EVT_MENU, self.on_menu_closefile, id=ID_CLOSE_FILE)

        self._incref(node.store)
        pub.subscribe(self.on_notification_closefile, 'store.close')

    def on_notification_closefile(self):
        """ Pubsub notification that a file (any file) has been closed """
        if not self.node.store.valid:
            self.Destroy()

    def on_close_evt(self, evt):
        """ Window is about to be closed """
        self._decref(self.node.store)
        evt.Skip()

    def on_menu_closefile(self, evt):
        """ "Close File" menu item activated.

        Note we rely on the pubsub message (above) to actually close the frame.
        """
        self._close(self.node.store)

    def on_menu_reopen(self, evt):
        """ Called when one of the "Reopen As" menu items is clicked """
        
        # The "Reopen As" submenu ID
        id_ = evt.GetId()               

        # Present node
        node_being_opened = self.node

        # The requested Node subclass to instantiate.
        h = self._menu_handlers[id_]

        log.debug('opening: %s %s' % (node_being_opened.store, node_being_opened.key))
        # Brand new Node instance of the requested type
        node_new = h(node_being_opened.store, node_being_opened.key)

        # Send off a request for it to be opened in the appropriate viewer
        # Post it directly to the App, or Container will intercept it!
        pos = wx.GetTopLevelParent(self).GetPosition()
        wx.PostEvent(wx.GetApp(), CompassOpenEvent(node_new, pos=pos))
