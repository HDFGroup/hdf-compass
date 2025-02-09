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
#                                                                            #
# author: gmasetti@ccom.unh.edu                                              #
##############################################################################

"""
Implements a viewer frame for compass_model.Array.
"""

import os
import logging

import wx

logger = logging.getLogger(__name__)

from hdf_compass.compass_viewer.text.text_ctrl import TextViewerFrame, XmlStc
from hdf_compass.compass_viewer.frame import NodeFrame


# Menu and button IDs
ID_FIND_TEXT_MENU = wx.NewId()
ID_SAVE_TEXT_MENU = wx.NewId()
ID_VALIDATE_XML_MENU = wx.NewId()
ID_FIND_XML_MENU = wx.NewId()
ID_SAVE_XML_MENU = wx.NewId()


class TextFrame(NodeFrame):
    icon_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'icons'))

    """
    Top-level frame displaying objects of type compass_model.Text.

    From top to bottom, has:

    1. Toolbar (see TextFrame.init_toolbar)
    2. A TextCtrl, which displays the text.
    """

    def __init__(self, node, pos=None):
        """ Create a new array viewer, to display *node*. """
        super(TextFrame, self).__init__(node, size=(800, 400), title=node.display_name, pos=pos)
        logger.debug("init")

        self.node = node

        self.txt = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt.SetValue(node.text)
        self.find_data = None
        self.start = 0
        self.last_search = None

        find_menu = wx.Menu()
        find_menu.Append(ID_FIND_TEXT_MENU, "Find Text\tCtrl-F")
        self.add_menu(find_menu, "Find")
        save_menu = wx.Menu()
        save_menu.Append(ID_SAVE_TEXT_MENU, "Save Text\tCtrl-T")
        self.add_menu(save_menu, "Save")

        self.toolbar = None
        self.init_toolbar()

        gridsizer = wx.BoxSizer(wx.VERTICAL)
        gridsizer.Add(self.txt, 1, wx.EXPAND)

        self.view = gridsizer

        self.Bind(wx.EVT_MENU, self.on_find_dialog, id=ID_FIND_TEXT_MENU)
        self.Bind(wx.EVT_MENU, self.on_save, id=ID_SAVE_TEXT_MENU)
        self.Bind(wx.EVT_FIND, self.on_find)
        self.Bind(wx.EVT_FIND_NEXT, self.on_find)
        self.Bind(wx.EVT_FIND_CLOSE, self.on_close_find)

    def init_toolbar(self):
        """ Set up the toolbar at the top of the window. """
        t_size = (24, 24)
        find_bmp = wx.Bitmap(os.path.join(self.icon_folder, "find_24.png"), wx.BITMAP_TYPE_ANY)
        save_bmp = wx.Bitmap(os.path.join(self.icon_folder, "save_24.png"), wx.BITMAP_TYPE_ANY)

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        self.toolbar.SetToolBitmapSize(t_size)
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddTool(ID_FIND_TEXT_MENU, "  Find  ", find_bmp)
        self.toolbar.AddTool(ID_SAVE_TEXT_MENU, "  Save  ", save_bmp)
        self.toolbar.Realize()

    def on_save(self, evt):
        """ User has chosen to save the current Text """
        logger.debug("saving: %s" % self.node.key)

        save_file_dialog = wx.FileDialog(self, "Save XML file", "", "text.txt",
                                         "Text files (*.txt)|*.txt", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_file_dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        with open(save_file_dialog.GetPath(), 'w') as fod:
            fod.write(self.node.text)

    def on_find_dialog(self, evt):
        # self.txt = self.txt.GetValue()
        self.find_data = wx.FindReplaceData()   # initializes and holds search parameters
        self.find_data.SetFlags(wx.FR_DOWN)
        dlg = wx.FindReplaceDialog(self.txt, self.find_data, 'Find')
        dlg.Show()

    def on_find(self, evt):
        flags = evt.GetFlags()
        down = flags & wx.FR_DOWN > 0
        whole = flags & wx.FR_WHOLEWORD > 0
        case = flags & wx.FR_MATCHCASE > 0
        logger.debug("Down search: %s, whole words: %s, case sensitive: %s > %s" % (down, whole, case, flags))

        end_of_words = [" ", "\n", ",", ";", ".", "-"]

        find_string = evt.GetFindString()
        if find_string != self.last_search:
            self.last_search = find_string
            self.start = 0
        len_str = len(find_string)

        txt = self.txt.GetValue()
        if not case:
            find_string = find_string.lower()
            txt = txt.lower()

        if down:
            if whole:
                while True:
                    pos = txt.find(find_string, self.start)
                    if pos == -1:
                        break
                    logger.debug("%s: %s, %s" % (txt[pos - 1: pos + len_str], txt[pos - 1],  txt[pos + len_str + 1]))
                    if txt[pos - 1] in end_of_words and txt[pos + len_str] in end_of_words:
                        logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
                        break
                    self.start = pos + 1
            else:
                pos = txt.find(find_string, self.start)
                logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
        else:
            if whole:
                while True:
                    pos = txt.rfind(find_string, 0, self.start)
                    if pos == -1:
                        break
                    if txt[pos - 1] in end_of_words and txt[pos + len_str + 1] in end_of_words:
                        logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
                        break
                    self.start = pos - 1
            else:
                pos = txt.rfind(find_string, 0, self.start)
                logger.debug("%s from %s up > pos: %s" % (find_string, self.start, pos))
        if pos == -1:
            dlg = wx.MessageDialog(self, 'No match for %s' % find_string, 'Text Search',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.start = 0
            return

        lines = len(txt[:pos].splitlines()) - 1
        logger.debug("lines: %d" % lines)
        end = pos + len_str

        self.txt.SetSelection(pos + lines, end + lines)
        self.txt.SetFocus()
        self.start = pos + 1

    def on_close_find(self, evt):
        evt.GetDialog().Destroy()
        self.start = 0


class XmlFrame(NodeFrame):
    icon_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'icons'))

    """
    Top-level frame displaying objects of type compass_model.Text.

    From top to bottom, has:

    1. Toolbar (see ArrayFrame.init_toolbar)
    2. A TextCtrl, which displays the text.
    """

    def __init__(self, node, pos=None):
        """ Create a new array viewer, to display *node*. """
        super(XmlFrame, self).__init__(node, size=(800, 400), title=node.display_name, pos=pos)
        logger.debug("init")

        self.node = node

        self.xml = XmlStc(self, xml_string=self.node.text)
        self.find_data = None
        self.start = 0
        self.last_search = None

        find_menu = wx.Menu()
        find_menu.Append(ID_FIND_XML_MENU, "Find Text\tCtrl-F")
        self.add_menu(find_menu, "Find")

        self.text_viewer = None

        save_menu = wx.Menu()
        save_menu.Append(ID_SAVE_XML_MENU, "Save xml\tCtrl-X")
        self.add_menu(save_menu, "Save")

        if self.node.has_validation():
            val_menu = wx.Menu()
            val_menu.Append(ID_VALIDATE_XML_MENU, "Validate xml\tCtrl-V")
            self.add_menu(val_menu, "Validate")

        self.toolbar = None
        self.init_toolbar()

        gridsizer = wx.BoxSizer(wx.VERTICAL)
        gridsizer.Add(self.xml, 1, wx.EXPAND)
        self.view = gridsizer

        self.Bind(wx.EVT_MENU, self.on_find_dialog, id=ID_FIND_XML_MENU)
        self.Bind(wx.EVT_MENU, self.on_save, id=ID_SAVE_XML_MENU)
        if self.node.has_validation():
            self.Bind(wx.EVT_MENU, self.on_validate, id=ID_VALIDATE_XML_MENU)
        self.Bind(wx.EVT_FIND, self.on_find)
        self.Bind(wx.EVT_FIND_NEXT, self.on_find)
        self.Bind(wx.EVT_FIND_CLOSE, self.on_close_find)

    def init_toolbar(self):
        """ Set up the toolbar at the top of the window. """
        t_size = (24, 24)
        find_bmp = wx.Bitmap(os.path.join(self.icon_folder, "find_24.png"), wx.BITMAP_TYPE_ANY)
        save_bmp = wx.Bitmap(os.path.join(self.icon_folder, "save_24.png"), wx.BITMAP_TYPE_ANY)
        validate_bmp = None
        if self.node.has_validation():
            validate_bmp = wx.Bitmap(os.path.join(self.icon_folder, "xml_validate_24.png"), wx.BITMAP_TYPE_ANY)

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        self.toolbar.SetToolBitmapSize(t_size)
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddTool(ID_FIND_XML_MENU, "Find", find_bmp)
        self.toolbar.AddTool(ID_SAVE_XML_MENU, "Save", save_bmp)
        if self.node.has_validation():
            self.toolbar.AddTool(ID_VALIDATE_XML_MENU, "Validate", validate_bmp)
        self.toolbar.Realize()

    def on_find_dialog(self, evt):
        # self.txt = self.txt.GetValue()
        self.find_data = wx.FindReplaceData()   # initializes and holds search parameters
        self.find_data.SetFlags(wx.FR_DOWN)
        dlg = wx.FindReplaceDialog(self.xml, self.find_data, 'Find')
        dlg.Show()

    def on_find(self, evt):
        flags = evt.GetFlags()
        down = flags & wx.FR_DOWN > 0
        whole = flags & wx.FR_WHOLEWORD > 0
        case = flags & wx.FR_MATCHCASE > 0
        logger.debug("Down search: %s, whole words: %s, case sensitive: %s > %s" % (down, whole, case, flags))

        end_of_words = [" ", "\n", ",", ";", ".", "-"]

        find_string = evt.GetFindString()
        if find_string != self.last_search:
            self.last_search = find_string
            self.start = 0
        len_str = len(find_string)

        txt = self.xml.GetValue()
        if not case:
            find_string = find_string.lower()
            txt = txt.lower()

        if down:
            if whole:
                while True:
                    pos = txt.find(find_string, self.start)
                    if pos == -1:
                        break
                    logger.debug("%s: %s, %s" % (txt[pos - 1: pos + len_str], txt[pos - 1],  txt[pos + len_str + 1]))
                    if txt[pos - 1] in end_of_words and txt[pos + len_str] in end_of_words:
                        logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
                        break
                    self.start = pos + 1
            else:
                pos = txt.find(find_string, self.start)
                logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
        else:
            if whole:
                while True:
                    pos = txt.rfind(find_string, 0, self.start)
                    if pos == -1:
                        break
                    if txt[pos - 1] in end_of_words and txt[pos + len_str + 1] in end_of_words:
                        logger.debug("%s from %s down > pos: %s" % (find_string, self.start, pos))
                        break
                    self.start = pos - 1
            else:
                pos = txt.rfind(find_string, 0, self.start)
                logger.debug("%s from %s up > pos: %s" % (find_string, self.start, pos))
        if pos == -1:
            dlg = wx.MessageDialog(self, 'No match for %s' % find_string, 'Text Search',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.start = 0
            return

        end = pos + len_str

        self.xml.SetFocus()
        self.xml.GotoPos(pos)
        self.xml.SetSelection(pos, end)
        self.start = pos + 1

    def on_close_find(self, evt):
        evt.GetDialog().Destroy()
        self.start = 0

    def on_validate(self, evt):
        """ User has chosen to validate the current XML """
        if self.node.has_validation():
            logger.debug("validating: %s" % self.node.key)
            self.text_viewer = TextViewerFrame(self.node.validation)
            self.text_viewer.Show()
        else:
            logger.warning("this node type has not validation: %s" % self.node)

    def on_save(self, evt):
        """ User has chosen to save the current XML """
        logger.debug("saving: %s" % self.node.key)

        save_file_dialog = wx.FileDialog(self, "Save XML file", "", "text.xml",
                                         "Xml files (*.xml)|*.xml", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_file_dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        with open(save_file_dialog.GetPath(), 'w') as fod:
            fod.write(self.node.text)
