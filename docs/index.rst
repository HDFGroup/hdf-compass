..   Copyright by The HDF Group.                                                
 All rights reserved.                                                       
                                                                          
 This file is part of the HDF Compass Viewer. The full HDF Compass          
 copyright notice, including terms governing use, modification, and         
 terms governing use, modification, and redistribution, is contained in     
 the file COPYING, which can be found at the root of the source code        
 distribution tree.  If you do not have access to this file, you may        
 request a copy from help@hdfgroup.org.                                     

####
Root
####

Data & Object Model
===================

Introduction
------------

This document describes the publically accessible data model package which is
used by HDFCompass to display objects in a file, OpenDAP server or other
resource.

The data model is implemented as a collection of classes in a top-level Python
package, ``compass_model``, which is completely independent of the GUI code.
It has no dependencies beyond the Python standard library.  This makes it
possible to develop and test new plugins independently of GUI development;
in particular, the automated Python unit-testing framework can be used, which
is impossible for code that depends on the GUI.

The classes in ``compass_model`` are abstract, and define a standard interface
for objects like containers, regular multidimensional arrays, images, and
key/value stores.  "Plug-ins" consist of concrete implementations which
satisfy this interface.  For example, the built-in HDF5 plugin which ships
with HDFCompass implements a ``Group`` class which inherits from
``compass_model.Container``, and a Dataset class which inherits from
``compass_model.Array``.

The GUI has a collection of viewers which can display any object following
the interfaces defined in ``compass_model``.  For example,
``compass_model.Container``
implementations are displayed in a browser-style view, with list, icon, and
tree displays possible.  Likewise, ``compass_model.Array`` implementations
are displayed in a spreadsheet-like view, with facilities for plotting data.

Multiple concrete classes can handle the same object in a file.  For example,
an HDF5 image is implemented as a dataset with special attributes.  Three
classes in the HDF5 plugin are capable of handling such an object, which
inherit respectively from ``compass_model.Image``, ``compass_model.Array``, and
``compass_model.KeyValue``; the last represents HDF5 attributes.

When an icon in the GUI is double-clicked, the default (last-registered) class is
used to open to object in the file.  The other classes are made available in a
context menu, for example, if the user wants to open an image with the
Array viewer or see the HDF5 attributes.


Numeric types (integers, floats, multidimensional data) are handled with the
NumPy type model, which can represent nearly all formats.  Python strings
(byte and Unicode) are also supported. 


Data stores
-----------

.. class:: Store

    Represents a file or remote resource which contains objects.  Objects
    within the store can be retrieved using *keys*, which may be any hashable
    Python object.  For example, an HDF5 store generally uses string keys
    representing paths in the file, although object and region reference
    objects are also valid.

    Objects may be retrieved using the __getitem__ syntax (``obj = store[key]``).
    The retrieved object is a Node instance.  The exact class depends on
    the order in which Node handlers were registered; see the `push` method
    below.

Methods related to the plugin system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, a model will implement several classes based on the ``compass_model``
abstract classes such as ``Container`` or ``Array``.  This rasises the
question: when an object is retrieved from the data store, which class
should be used?

The answer is that each ``Node`` subclass you write should be "registered" with
your ``Store`` subclass, and have a static method called ``canhandle``.  When
an object is opened, by default the most recently registered class which
reports it can understand the object is used.

All registered subclasses may be retrieved via the ``gethandlers`` function,
which an optionally request that only subclasses capable of handling *key*
be returned.  This is the basis for the right-click "Open As" menu in the GUI.

.. classmethod:: Store.push(nodeclass)
    
    Register a Node subclass.  These are kept in a list inside the class;
    when an object is retrieved from the store, the first class for
    which `nodeclass.canhandle(store, key)` returns True is instantiated
    and returned.

.. method:: Store.__getitem__(key)

    Open an object in the store, using the last registered class which
    reports it can open the key.

.. method:: Store.gethandlers(key=None)

    Retrieve all registered Node subclasses, optionally filtering by
    those which report they can handle *key*.

.. method:: Store.__contains__(key)

    **(Abstract)** True if *key* is exists in the store, False otherwise.

Other methods & properties
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. staticmethod:: Store.canhandle(url)

    **(Abstract)** Return True if this class can make sense of *url*, False otherwise.  This
    method is used by the GUI when determining which Store implementation to
    use when opening a file.  For example, the HDF5 plugin uses
    ``h5py.is_hdf5(filename)``.

.. method:: Store.__init__(url)

    **(Abstract)** Create a new store instance from the data at *url*.  URLs are given
    in the ``scheme://locator`` fashion.  For example, an HDF5 file might
    be located by ``file:///path/to/file.hdf5``.

.. method:: Store.close():

    **(Abstract)** Discontinue access to the data store.

.. method:: Store.getparent(key)

    **(Abstract)** Return the object which contains *key*, or None if no such object exists.

.. attribute:: Store.url

    **(Abstract)** The URL used to open the store

.. attribute:: Store.displayname
    
    **(Abstract)** A short name used for the store (e.g. ``basename(filepath)``).

.. attribute:: Store.root

    **(Abstract)** A Node instance representing the starting point in the file.
    For hierarchical formats, this would be the root container.  For scalar
    formats (FITS, for example), this could be e.g. an Array or Image instance.

.. attribute:: Store.file_extensions

    For plugins that support local file access, this is a dictionary mapping
    file kinds to lists of extensions in "glob" format, e.g. 
    ``{'HDF5 File': ['.h5', '.hdf5']}``.  This will be used to populate the
    filter in the file-open dialog, among other things.
    
Nodes
-----

A "node" is any object which lives in the data store.  The Node class defined
below is the base class for more interesting abstract classes like containers
and arrays.  It defines much of the interface.

.. class:: Node

    Base class for all objects which live in a data store.

    You generally shouldn't inherit from Node directly, but from one of the
    more useful Node subclasses in this file.  Direct Node subclasses can't
    do anything interesting in the GUI; all they do is show up in the browser.


.. attribute:: Node.icons

    Class attribute containing a dict for icon support.
    Keys should be integers giving icon size; values are a callable returning
    a byte string with PNG image data.
    Example:      ``icons = {16: get_png_16, 32: get_png_32}``.
    Since icons are a pain to handle, default icons are provided by
    ``compass_model`` and this attribute is optional.

.. attribute:: Node.classkind

    **(Abstract)**
    A short string (2 or 3 words) describing what the class represents.
    This will show up in e.g. the "Open As" context menu.
    Example:  "HDF5 Image" or "Swath".

.. staticmethod:: Node.canhandle(store, key)

    **(Abstract)** Determine whether this class can usefully represent the object.
    Keep in mind that keys are not technically required to be strings.

.. method:: Node.__init__(store, key):

    **(Abstract)** Create a new instance representing the object pointed to by *key*
    in *store*.


.. attribute:: Node.key

    **(Abstract)** Unique key which identifies this object in the store.
    Keys may be any hashable object, although strings are the most common.


.. attribute:: Node.store

    **(Abstract)** The data store to which the object belongs.

.. attribute:: Node.displayname

    **(Abstract)** 
    A short name for display purposes (16 chars or so; more will be ellipsized).

.. attribute:: Node.description

    **(Abstract)** 
    Descriptive string (possibly multi-line).


Containers
----------

.. class:: Container(Node)

    Represents an object which holds other objects, like an HDF5 group
    or a filesystem directory.
    Implementations will be displayed using the browser view.

.. method:: Container.__len__()

    **(Abstract)** 
    Get the number of objects directly attached to the container.

.. method:: Container.__getitem__(index)

    **(Abstract)** 
    Retrieve the node at *index*.  Note this returns a Node instance, not a key.


Arrays
------

.. class:: Array(Node)

    The array type represents a multidimensional array, using an interface
    inspired by Numpy arrays.

    Implementations will be displayed in a spreadsheet-style viewer with
    controls for subsetting and plotting.

.. attribute:: Array.shape

    Shape of the array, as a Python tuple.

.. attribute:: Array.dtype

    NumPy data type object representing the type of the array.

.. method:: Array.__getitem__(indices)

    Retrieve data from the array, using the standard array-slicing syntax
    ``data = array[idx1, idx2, idx3].  *indices* are the slicing arguments.
    Only integer indexes and slice objects (representing ranges) are
    supported.


Key-Value lists
---------------

.. class:: KeyValue(Node)

    Represents an object which contains a sequence of key: value attributes.
    Keys must be strings.  Values may be Python or NumPy objects.
    Implementations will be displayed using a list-like control.

.. attribute:: KeyValue.keys

    **(Abstract)** 
    A list containing all (string) keys contained in the object.

.. method:: KeyValue.__getitem__(name)

    **(Abstract)** Retrieve the value associated with string *name*.


Images
------

.. class:: Image(Node)

    Represents an image.  The current interface supports only true-color RGB
    images with the origin at upper left, although this could easily be
    extended to more complex formats including RGBA or palette-based images.

    Implementations are displayed in an image viewer.

.. attribute:: Image.width

    Image width in pixels

.. attribute:: Image.height

    Image height in pixels

.. attribute:: Image.data

    Image data.  Currently RGB, pixel-interlaced.


Top-level functions
-------------------

One public function is defined in ``compass_model``:

.. function:: push(storeclass)

    Register a new Store subclass with HDFCompass.  When a URL is being
    opened, the class will be queried (via ``storeclass.canhandle``) to see
    if it can make sense of the URL.