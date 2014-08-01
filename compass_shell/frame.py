class Frame(object):
    """ Base class for shell view of node objects
    """
    
    def __init__(self, node):
        """ Create a new frame.

        node:   Node to display.
        """

    # --- Begin history support functions -------------------------------------

    @property
    def node(self):
        """ return current node """
        raise NotImplementedError

    def go_back(self):
        """ Go to the previously displayed item """
        raise NotImplementedError


    def go_next(self):
        """ Go to the next displayed item """
        raise NotImplementedError


    def go_up(self):
        """ Go to the enclosing container """
        raise NotImplementedError


    def go(self, newnode):
        """ Go to a particular node.

        Adds the node to the history.
        """
        raise NotImplementedError

    # --- End history support functions ---------------------------------------

    def Show(self, option=None):
        raise NotImplementedError

    
