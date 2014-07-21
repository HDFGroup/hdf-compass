# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Defines wx.Frame subclasses which are the foundation of the various windows
displayed by HDFCompass.

Much of the common functionality (e.g. "Open File..." menu item) is implemented
here.
"""

import wx
from wx.lib.pubsub import pub

from . import imagesupport
from .info import InfoPanel
from . import platform

ID_OPEN_RESOURCE = wx.NewId()
ID_CLOSE_FILE = wx.NewId()


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

    def __init__(self, **kwds):
        """ Constructor; any keywords are passed on to wx.Frame.
        """

        wx.Frame.__init__(self, None, **kwds)
        menubar = wx.MenuBar()

        # File menu
        fm = wx.Menu()

        fm.Append(wx.ID_OPEN, "&Open...\tCtrl-O")
        fm.Append(ID_OPEN_RESOURCE, "Open &Resource...\tCtrl-R")

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

    
    def on_exit(self, evt):
        """ Called on "exit" event from the menu """
        wx.GetApp().Exit()
        
        
    def on_about(self, evt):
        """ Display an "About" dialog """
        info = wx.AboutDialogInfo()
        info.Name = "HDFCompass"
        if platform.MAC:
            info.Version = "release"
        else:
            info.Version = platform.VERSION
        info.Copyright = "(c) 2013-2014 Heliosphere Research LLC"
        wx.AboutBox(info)
    

    def on_file_open(self, evt):
        """ Request to open a file via the Open entry in the File menu """
        import compass_model
        
        def make_filter_string(dct):
            """ Make a wxPython dialog filter string segment from dict """
            filter_string = []
            for key, value in dct.iteritems():
                s = "{name} ({pattern_c})|{pattern_sc}".format(
                    name=key, 
                    pattern_c=",".join(value),
                    pattern_sc=";".join(value) )
                filter_string.append(s)
            return "|".join(filter_string)
            
        # The wxPython wildcard string is a bunch of filter strings pasted together
        wc_string = [s.file_extensions for s in compass_model.getstores() if len(s.file_extensions) != 0]
        wc_string = "|".join([make_filter_string(x) for x in wc_string])
        
        from . import open_store
        dlg = wx.FileDialog(self, "Open Local File", wildcard=wc_string)#, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        url = 'file://'+path
        if not open_store(url):
            dlg = wx.MessageDialog(self, 'The following file could not be opened:\n\n%s' % path,
                               'No handler for file', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        
    def on_window_close(self, evt):
        """ Close Window file event, or cmd-W """
        self.Destroy()
        
        
    def on_resource_open(self, evt):
        """ Request to open a URL via the File menu """
        from . import open_store
        dlg = wx.TextEntryDialog(self, 'Enter resource URL:')

        if dlg.ShowModal() != wx.ID_OK or dlg.GetValue() == "":
            dlg.Destroy()
            return

        url = dlg.GetValue()
        dlg.Destroy()

        if not open_store(url):
            dlg = wx.MessageDialog(self, 'The following URL could not be opened:\n\n%s' % url,
                               'No handler for URL', wx.OK | wx.ICON_INFORMATION)
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

        data = imagesupport.getbitmap('logo')
        bmp = wx.StaticBitmap(self, wx.ID_ANY, data)

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

