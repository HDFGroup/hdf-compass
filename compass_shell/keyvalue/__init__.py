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

class KeyValueFrame(Frame):

    """
    A class to display a Container class, and browse its contents.
    """

    def __init__(self, node):
        """ Create a new display.

        node:   Container instance to display.
        """

        self.node = node
    
    @property
    def node(self):
        return self.node

    # --- Begin history support functions -------------------------------------

    def go_back(self):
       raise NotImplementedError


    def go_next(self):
        raise NotImplementedError

    def go_up(self):
        raise NotImplementedError

    def go(self, newnode):
        """ Go to a particular node.

        """
        self.node = newnode

    # --- End history support functions ---------------------------------------

    def Show(self, option=None):
        node = self.node
        print node.displaytitle, ":"
        for o in node:
            print '\t', o.displayname, o.classkind
        
     

   


        