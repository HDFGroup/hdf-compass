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
The following class definitions represent the pluggable data model.

By subclassing various things in this module, and implementing the missing
(virtual) methods and properties, you can have the GUI infrastructure display
your own objects without writing a single line of wxPython code.  GUI
support exists for generic kinds of objects including browsable containers,
array-like datasets, and images.

More importantly, you can add support for entirely new file formats.

To implement support for a new kind of "datastore" (HDF5, HDF4, NetCDF, etc.),
start by subclassing Store and overriding the appropriate methods and
properties.  Then, subclass the various Node classes this module provides
(Container, Array, Image, etc.) and implement the various virtual bits of
those classes as well:

    class FooStore(compass_model.Store):
        ...

    class FooGroup(compass_model.Container):
        ...

    class FooDataset(compass_model.Array):
        ...

    class FooPicture(compass_model.Image):
        ...

You're not required to do all of them (and of course not all formats provide
something like an Image), but the more you implement the more capable the
interface will be.

So that your Store class knows which kinds of nodes are available to open,
manually register your Node subclasses:

    FooStore.push(FooGroup)
    FooStore.push(FooDataset)
    FooStore.push(FooPicture)

Finally, let the rest of the world know about your new data store support by
calling this module's register() function:

    compass_model.push(FooStore)

You can also extend other peoples' stores.  Suppose there's a module for
reading HDF5 files, with a store class called foohdf5.HDF5Store,
but the author didn't support the HDF5 Image standard.  Just write a subclass
of Image, and register it with the other person's class:

    class MyHDF5Image(Image):
        ...

    foohdf5.HDF5Store.push(MyHDF5Image)

Of course, this assumes you know enough about the internals of the other
person's Store to make your new class useful.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

_stores = []


def push(store):
    """ Register a new data store class """
    _stores.insert(0, store)


def get_stores():
    """ Get a list containing known data store classes """
    return _stores[:]


icon_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons'))


class Store(object):
    """
    Represents a data store (i.e. a file or remote resource).
    """

    __metaclass__ = ABCMeta

    # -------------------------------------------------------------------------
    # Plugin support

    __nodeclasses = None

    @classmethod
    def push(cls, nodeclass):
        """ Register a Node subclass.

        When a key is being opened, each subclass is queried in turn.  The
        first one which reports it can handle the key is used.
        """
        if cls.__nodeclasses is None:
            cls.__nodeclasses = [Unknown]
        cls.__nodeclasses.insert(0, nodeclass)

    @abstractmethod
    def __contains__(self, key):
        """ Check if a key is valid. """
        log.error("to be overloaded")

    def __getitem__(self, key):
        """ Return a Node instance  for *key*.

        Figures out the appropriate Node subclass for the object identified by
        "key", creates an instance and returns it.
        """
        return self.gethandlers(key)[0](self, key)

    def gethandlers(self, key=None):
        """ Rather than picking a handler and returning the Node, return a
        list of all handlers which can do something useful with *key*.

        If *key* is not specified, returns all handlers
        """
        if self.__nodeclasses is None:
            self.__nodeclasses = [Unknown]

        if key is None:
            return self.__nodeclasses
        if key not in self:
            raise KeyError(key)

        return [nc for nc in self.__nodeclasses if nc.can_handle(self, key)]

    # End plugin support
    # -------------------------------------------------------------------------


    # For plugins which support local files, this is a dictionary mapping
    # file kinds to lists of extensions, e.g. {'HDF5 File': ['*.hdf5', '*.h5']}
    file_extensions = {}

    @abstractproperty
    def url(self):
        """ Identifies the file or Web resource (string).

        Examples might be "file:///path/to/foo.hdf5" or
        "http://www.example.com/web/resource"
        """
        raise NotImplementedError

    @abstractproperty
    def display_name(self):
        """ Short name for display purposes.

        For example, for a file-based store you could implement this with
        os.path.basename(self.path).
        """
        raise NotImplementedError

    @abstractproperty
    def root(self):
        """ The root node.

        Serves as the entry point into the resource.  Every Store must
        implement this, and is required to return a Container instance.
        """
        raise NotImplementedError

    @staticmethod  # Python 2.x does not have abstractstatic
    def can_handle(url):
        """ Test if this class can open the resource.

        Returns True or False.  Note this may have side effects, but
        the resource must not be modified.
        """
        raise NotImplementedError

    @abstractproperty
    def valid(self):
        """ True if the store is open and ready for use, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def __init__(self, url):
        """ Open the resource.
        """
        raise NotImplementedError

    def close(self):
        """ Discontinue access to the resource.

        Any further use of this object, or retrieved nodes, is undefined.
        """
        pass

    def get_parent(self, key):
        """ Return the parent node of the object identified by *key*.

        If an object has no parent, or contains itself, this should return
        None.  That way, the "up" arrow on the Container view will be
        grayed out.
        """
        pass


class Node(object):
    """
    Base class for all objects which live in a data store.

    You generally shouldn't inherit from Node directly, but from one of the
    more useful Node subclasses in this file.  Direct Node subclasses can't
    do anything interesting in the GUI; all they do is show up in the browser.
    """

    __metaclass__ = ABCMeta

    # Class attribute containing a dict for icon support.
    # Keys should be paths to icon files.
    # Example:      icons = {16: png_16, 32: png_32}

    icons = NotImplemented


    # A short string (2 or 3 words) describing what the class represents.
    # This will show up in e.g. the "Open As" context menu.
    # Example:  "HDF5 Image" or "Swath"

    class_kind = NotImplemented

    @staticmethod
    def can_handle(store, key):
        """ Determine whether this class can usefully represent the object.

        Keep in mind that keys are not technically required to be strings.
        """
        raise NotImplementedError

    def __init__(self, store, key):
        """ Create an instance of this class.

        Subclasses must not modify the signature.
        """
        raise NotImplementedError

    @property
    def key(self):
        """ Unique key which identifies this object in the store.

        Keys may be any hashable object, although strings are the most common.
        """
        raise NotImplementedError

    @property
    def store(self):
        """ The data store to which the object belongs. """
        raise NotImplementedError

    @property
    def display_name(self):
        """ A short name for display purposes """
        raise NotImplementedError

    @property
    def display_title(self):
        """ A longer name appropriate for display in a window title.

        Defaults to *display_name*.
        """
        return self.display_name

    @property
    def description(self):
        """ Descriptive string (possibly multi-line) """
        raise NotImplementedError

    def preview(self, w, h):
        """ [Optional] PNG image preview """
        return None


class Container(Node):
    """
    Represents an object which holds other objects (like an HDF5 group).

    Subclasses will be displayed using the browser view.
    """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "folder_16.png"),
             64:    os.path.join(icon_folder, "folder_64.png")}

    def __len__(self):
        """ Number of child objects """
        raise NotImplementedError

    def __iter__(self):
        """ Iterator over child objects.

        Should yield Nodes, not keys (use your Store.open method).
        """
        raise NotImplementedError

    def __getitem__(self, idx):
        """ Open an item by index (necessary to support ListCtrl).

        Should return a Node, not a key (use your Store.open method).
        """
        raise NotImplementedError


class KeyValue(Node):
    """
    Represents an object which contains a sequence of key: value attributes.

    Keys must be strings.

    Subclasses will be displayed using a list-like control.
    """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "kv_16.png"),
             64:    os.path.join(icon_folder, "kv_64.png")}

    @property
    def keys(self):
        """ Return a list of attribute keys. """
        raise NotImplementedError

    def __getitem__(self, name):
        """ Return the raw attribute value """
        raise NotImplementedError


class Array(Node):
    """
    Represents a NumPy-style regular, rectangular array.

    Subclasses will be displayed in a spreadsheet-style viewer.
    """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "array_16.png"),
             64:    os.path.join(icon_folder, "array_64.png")}

    @property
    def shape(self):
        """ Shape tuple """
        raise NotImplementedError

    @property
    def dtype(self):
        """ Data type """
        raise NotImplementedError

    def __getitem__(self, args):
        """ Retrieve data elements """
        raise NotImplementedError

    def is_plottable(self):
        """ To be overriden in case that there are cases in which the array is not plottable """
        return True


class Image(Node):
    """
    A single raster image.
    """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "image_16.png"),
             64:    os.path.join(icon_folder, "image_64.png")}

    @property
    def width(self):
        """ Image width in pixels """
        pass

    @property
    def height(self):
        """ Image height in pixels """
        pass

    @property
    def palette(self):
        """ Palette array, or None. """
        raise NotImplementedError

    @property
    def data(self):
        """ Image data """


class Text(Node):
    """ A text. """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "text_16.png"),
             64:    os.path.join(icon_folder, "text_64.png")}

    @property
    def text(self):
        """ Text data """


class Xml(Text):
    """ A XML text. """

    __metaclass__ = ABCMeta

    icons = {16:    os.path.join(icon_folder, "xml_16.png"),
             64:    os.path.join(icon_folder, "xml_64.png")}

    def has_validation(self):
        """To be overriden in case that the xml has a known mechanism to be validated"""
        return False

    @property
    def validation(self):
        """ Validation info """


class Unknown(Node):
    """
    "Last resort" node (and the only concrete class in this module).
    These can always be created, but do nothing useful.
    """

    icons = {16:    os.path.join(icon_folder, "unknown_16.png"),
             64:    os.path.join(icon_folder, "unknown_64.png")}

    class_kind = "Unknown"

    @staticmethod
    def can_handle(store, key):
        return True

    def __init__(self, store, key):
        self._key = key
        self._store = store

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        import os.path
        try:
            return os.path.basename(str(self.key))
        except Exception:
            return "Unknown"

    @property
    def description(self):
        return "Unknown object"
