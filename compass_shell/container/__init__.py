# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Implements a viewer for compass_model.Container instances.

This frame is a simple browser view with back/forward/up controls.

Currently list and icon views are supported.
"""

import compass_model
from ..frame import Frame

class ContainerFrame(Frame):

    """
    A class to display a Container class, and browse its contents.
    """

    def __init__(self, node):
        """ Create a new display.

        node:   Container instance to display.
        """
        # NodeFrame.__init__(self, node, size=(800, 400), title=node.displaytitle, pos=pos)   

        self.history = [node]
        self.history_ptr = 0


    # --- Begin history support functions -------------------------------------

    @property
    def node(self):
        return self.history[self.history_ptr]

    def go_back(self):
        """ Go to the previously displayed item """
        if self.history_ptr > 0:
            self.history_ptr -= 1


    def go_next(self):
        """ Go to the next displayed item """
        if self.history_ptr < (len(self.history)-1):
            self.history_ptr += 1


    def go_up(self):
        """ Go to the enclosing container """
        node = self.history[self.history_ptr]
        parent = node.store.getparent(node.key)
        if parent.key != node.key:  # at the root item
            self.go(parent)


    def go(self, newnode):
        """ Go to a particular node.

        Adds the node to the history.
        """
        del self.history[self.history_ptr+1:]
        self.history.append(newnode)
        self.history_ptr += 1

    # --- End history support functions ---------------------------------------

    def Show(self, option=None):
        node = self.node
        print node.displaytitle, ":"
        for o in node:
            print '\t', o.displayname, o.classkind
        
     

   


        