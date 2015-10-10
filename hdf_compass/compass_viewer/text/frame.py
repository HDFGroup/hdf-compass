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
Implements a viewer frame for compass_model.Array.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

import wx

log = logging.getLogger(__name__)

from .text_ctrl import TextViewerFrame, XmlStc
from ..frame import NodeFrame


# Menu and button IDs
ID_SAVE_TEXT_MENU = wx.NewId()
ID_VALIDATE_XML_MENU = wx.NewId()
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
        log.debug("init")

        self.node = node

        self.txt = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt.SetValue(node.text)

        save_menu = wx.Menu()
        save_menu.Append(ID_SAVE_TEXT_MENU, "Save Text\tCtrl-T")
        self.add_menu(save_menu, "Save")

        self.toolbar = None
        self.init_toolbar()

        gridsizer = wx.BoxSizer(wx.VERTICAL)
        gridsizer.Add(self.txt, 1, wx.EXPAND)

        self.view = gridsizer

        self.Bind(wx.EVT_MENU, self.on_save, id=ID_SAVE_TEXT_MENU)

    def init_toolbar(self):
        """ Set up the toolbar at the top of the window. """
        t_size = (24, 24)
        plot_bmp = wx.Bitmap(os.path.join(self.icon_folder, "save_24.png"), wx.BITMAP_TYPE_ANY)

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        self.toolbar.SetToolBitmapSize(t_size)
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddLabelTool(ID_SAVE_TEXT_MENU, "Save", plot_bmp,
                                  shortHelp="Save Text", longHelp="Extract and save Text on disk")
        self.toolbar.Realize()

    def on_save(self, evt):
        """ User has chosen to save the current Text """
        log.debug("saving: %s" % self.node.key)

        save_file_dialog = wx.FileDialog(self, "Save XML file", "", "text.txt",
                                         "Text files (*.txt)|*.txt", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_file_dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        with open(save_file_dialog.GetPath(), 'w') as fod:
            fod.write(self.node.text)


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
        log.debug("init")

        self.node = node

        self.xml = XmlStc(self, xml_string=self.node.text)

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

        self.Bind(wx.EVT_MENU, self.on_save, id=ID_SAVE_XML_MENU)
        if self.node.has_validation():
            self.Bind(wx.EVT_MENU, self.on_validate, id=ID_VALIDATE_XML_MENU)

    def init_toolbar(self):
        """ Set up the toolbar at the top of the window. """
        t_size = (24, 24)
        save_bmp = wx.Bitmap(os.path.join(self.icon_folder, "save_24.png"), wx.BITMAP_TYPE_ANY)
        if self.node.has_validation():
            validate_bmp = wx.Bitmap(os.path.join(self.icon_folder, "xml_validate_24.png"), wx.BITMAP_TYPE_ANY)

        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

        self.toolbar.SetToolBitmapSize(t_size)
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddLabelTool(ID_SAVE_XML_MENU, "Save", save_bmp,
                                  shortHelp="Save XML", longHelp="Extract and save XML on disk")
        if self.node.has_validation():
            self.toolbar.AddLabelTool(ID_VALIDATE_XML_MENU, "Validate", validate_bmp,
                                      shortHelp="Validate XML", longHelp="Validate XML in a popup window")
        self.toolbar.Realize()

    def on_validate(self, evt):
        """ User has chosen to validate the current XML """
        if self.node.has_validation():
            log.debug("validating: %s" % self.node.key)
            self.text_viewer = TextViewerFrame(self.node.validation)
            self.text_viewer.Show()
        else:
            log.warning("this node type has not validation: %s" % self.node)

    def on_save(self, evt):
        """ User has chosen to save the current XML """
        log.debug("saving: %s" % self.node.key)

        save_file_dialog = wx.FileDialog(self, "Save XML file", "", "text.xml",
                                         "Xml files (*.xml)|*.xml", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_file_dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...

        # save the current contents in the file
        # this can be done with e.g. wxPython output streams:
        with open(save_file_dialog.GetPath(), 'w') as fod:
            fod.write(self.node.text)
