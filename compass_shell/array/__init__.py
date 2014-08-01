# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Implements a viewer for compass_model.Array instances.

"""

import compass_model
from ..frame import Frame

class ArrayFrame(Frame):

    """
    A class to display a Container class, and browse its contents.
    """

    def __init__(self, node):
        """ Create a new display.

        node:   Container instance to display.
        """
        # NodeFrame.__init__(self, node, size=(800, 400), title=node.displaytitle, pos=pos)   

        self.node = node

    # --- Begin history support functions -------------------------------------

    @property
    def node(self):
        return self.node

    def go_back(self):
        raise NotImplementedError


    def go_next(self):
        raise NotImplementedError


    def go_up(self):
        raise NotImplementedError


    def go(self, newnode):
        self.node = newnode

    # --- End history support functions ---------------------------------------

    def Show(self, option=None):
        node = self.node
        print node.displaytitle, ":"
        for o in node:
            print '\t', o.displayname, o.classkind
        
     

   


        