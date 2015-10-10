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

import logging

import wx
import wx.stc as stc

log = logging.getLogger(__name__)

from ..frame import BaseFrame


if wx.Platform == '__WXMSW__':
    faces = {'times': 'Times New Roman',
             'mono': 'Courier New',
             'helv': 'Arial',
             'other': 'Comic Sans MS',
             'size': 10,
             'size2': 8,
             }
else:
    faces = {'times': 'Times',
             'mono': 'Courier',
             'helv': 'Helvetica',
             'other': 'new century schoolbook',
             'size': 13,
             'size2': 11,
             }


class TextViewerFrame(BaseFrame):

    """
    Base class for Matplotlib plot windows.

    Override draw_figure() to plot your figure on the provided axes.
    """

    def __init__(self, data, title="Validation"):
        """ Create a new Matplotlib plotting window for a 1D line plot """
        BaseFrame.__init__(self, id=wx.ID_ANY, title=title, size=(800, 400))

        self.data = data

        self.txt = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt.SetValue(self.data)

        gridsizer = wx.BoxSizer(wx.VERTICAL)
        gridsizer.Add(self.txt, 1, wx.LEFT | wx.TOP | wx.GROW)

        self.view = gridsizer


class XmlStc(stc.StyledTextCtrl):
    def __init__(self, parent, xml_string, keywords=None):
        stc.StyledTextCtrl.__init__(self, parent, -1)
        self.SetLexer(stc.STC_LEX_XML)
        if keywords is not None:
            self.SetKeyWords(0, keywords)

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

        self.StyleSetSpec(stc.STC_H_VALUE, "fore:#0000cc,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_DEFAULT, "fore:#0000cc,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_ENTITY, "fore:#0000cc,face:%(helv)s,size:%(size)d" % faces)
        # initial XML tag
        self.StyleSetSpec(stc.STC_H_XMLSTART, "fore:#ffcccc,bold,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_XMLEND, "fore:#ffcccc,bold,face:%(helv)s,size:%(size)d" % faces)
        # XML tags
        self.StyleSetSpec(stc.STC_H_TAG, "fore:#555555,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_TAGEND, "fore:#555555,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_TAGUNKNOWN, "fore:#555555,face:%(helv)s,size:%(size)d" % faces)
        # XML attributes
        self.StyleSetSpec(stc.STC_H_ATTRIBUTE, "fore:#BDB76B,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_ATTRIBUTEUNKNOWN, "fore:#BDB76B,face:%(helv)s,size:%(size)d" % faces)
        # XML comments and quotes
        self.StyleSetSpec(stc.STC_H_COMMENT, "fore:#888888,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_SINGLESTRING, "fore:#aa2222,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_DOUBLESTRING, "fore:#aa2222,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_SGML_SIMPLESTRING, "fore:#aa2222,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_H_SGML_DOUBLESTRING, "fore:#aa2222,face:%(helv)s,size:%(size)d" % faces)

        # Keyword
        self.StyleSetSpec(stc.STC_P_WORD, "fore:#990000,size:%(size)d" % faces)

        # Caret color
        self.SetCaretForeground("BLUE")
        # Selection background
        self.SetSelBackground(1, '#66CCFF')

        self.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        self.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        self.SetProperty("fold", "1")  # Enable folding
        self.SetProperty("fold.html", "1")  # Enable folding
        self.SetProperty("tab.timmy.whinge.level", "1")  # Highlight tab/space mixing (shouldn't be any)
        self.SetMargins(3, 3)  # Set left and right margins
        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)  # Set up the numbers in the margin for margin #1
        self.SetMarginWidth(1, 40)  # Reasonable value for, say, 4-5 digits using a mono font (40 pix)
        # self.SetViewWhiteSpace(False)
        self.SetWrapMode(stc.STC_WRAP_WORD)
        self.SetUseVerticalScrollBar(True)
        self.SetUseHorizontalScrollBar(True)

        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 15)
        # marker style
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "black")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#cccccc")
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "black")
        stc.EVT_STC_MARGINCLICK(self, -1, self.on_margin_click)

        self.SetText(xml_string)
        self.SetEditable(False)

    def on_margin_click(self, evt):
        """ Folds and unfolds as needed """

        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.fold_all()

            else:
                line_clicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(line_clicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(line_clicked, True)
                        self.expand_item(line_clicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(line_clicked):
                            self.SetFoldExpanded(line_clicked, False)
                            self.expand_item(line_clicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(line_clicked, True)
                            self.expand_item(line_clicked, True, True, 100)
                    else:
                        self.ToggleFold(line_clicked)

    def fold_all(self):
        line_count = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for line_num in range(line_count):
            if self.GetFoldLevel(line_num) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(line_num)
                break

        line_num = 0
        while line_num < line_count:
            level = self.GetFoldLevel(line_num)
            if level & stc.STC_FOLDLEVELHEADERFLAG and (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(line_num, True)
                    line_num = self.expand_item(line_num, True)
                    line_num -= 1
                else:
                    last_child = self.GetLastChild(line_num, -1)
                    self.SetFoldExpanded(line_num, False)
                    if last_child > line_num:
                        self.HideLines(line_num + 1, last_child)

            line_num += 1

    def expand_item(self, line, do_expand, force=False, vis_levels=0, level=-1):
        last_child = self.GetLastChild(line, level)
        line += 1
        while line <= last_child:
            if force:
                if vis_levels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if do_expand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if vis_levels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.expand_item(line, do_expand, force, vis_levels - 1)

                else:
                    if do_expand and self.GetFoldExpanded(line):
                        line = self.expand_item(line=line, do_expand=True, force=force, vis_levels=(vis_levels - 1))
                    else:
                        line = self.expand_item(line=line, do_expand=False, force=force, vis_levels=(vis_levels - 1))
            else:
                line += 1

        return line

