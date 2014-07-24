"""
HDF Compass "pilot" plugin for viewing ASCII Grid Data.

Subclasses consist of a Container and an Array, representing
directories and the ASCII grid data respectively.
See: http://en.wikipedia.org/wiki/Esri_grid for a description of
the file format
"""

import os
import os.path as op
import numpy as np
import linecache

import compass_model


class AsciiGrid(compass_model.Store):

    """
        A "data store" represented by an ascii grid file.
    """

    file_extensions = {'ASC File': ['*.asc']}

    def __contains__(self, key):
        if key == '/':
            return True
        return False

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return op.basename(self._url)

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return self._valid

    @staticmethod
    def canhandle(url):
        if not url.startswith('file://'):
            return False
        if not url.endswith('.asc'):
            return False
        return True

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._value = True

    def close(self):
        self._valid = False

    def getparent(self, key):
        return None

    def getFilePath(self):
        prefixLen = len('file://')
        return self._url[prefixLen:]


class Root(compass_model.Container):

    """
        Represents the root (and only) group for ASCII Grid
    """

    classkind = "Root"

    @staticmethod
    def canhandle(store, key):
        print "container can handle, ", key
        if key == '/':
            return True
        return False

    def __init__(self, store, key):
        pass

    @property
    def key(self):
        return "/"

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return self_store.displayname

    @property
    def displaytitle(self):
        return "%s %s" % (self.store.displayname, self.key)

    @property
    def description(self):
        return 'folder "%s" (%d members)' % (self.displayname, len(self))

    def __len__(self):
        return 0

    def __iter__(self):
        names = []
        return iter(names)

    def __getitem__(self, idx):
        return None


class ASCFile(compass_model.Array):

    """
        Represents a .asc grid file.
    """

    classkind = "ASCII Grid File"

    @staticmethod
    def canhandle(store, key):
        if key == '/':
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        filePath = self._store.getFilePath()
        self._nrows = int(linecache.getline(filePath, 1).lstrip("ncols"))
        self._ncols = int(linecache.getline(filePath, 2).lstrip("nrows"))
        self._data = None

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return self._store.displayname

    @property
    def description(self):
        return 'File "%s", size %d bytes' % (self.displayname, op.getsize(self.key))

    @property
    def shape(self):
        return (self._nrows, self._ncols)

    @property
    def dtype(self):
        return np.dtype('float')

    def __getitem__(self, args):
        if self._data is None:
            self._data = np.loadtxt(self._store.getFilePath(), skiprows=6, unpack=True)
        return self._data[args]


class Attributes(compass_model.KeyValue):

    classkind = "Attributes of ASC Grid File"

    @staticmethod
    def canhandle(store, key):
        if key == '/':
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        filePath = self._store.getFilePath()
        self.data = {'NODATA Value': float(linecache.getline(filePath, 6).lstrip("NODATA_value")),
          'cellsize': float(linecache.getline(filePath, 5).lstrip("cellsize")),
          'yllcorner': float(linecache.getline(filePath, 4).lstrip("yllcorner")),
          'xllcorner': float(linecache.getline(filePath, 3).lstrip("xllcorner"))}

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        self._store

    @property
    def displayname(self):
        return self.key

    @property
    def description(self):
        return self.displayname

    @property
    def keys(self):
        return self.data.keys()

    def __getitem__(self, args):
        return self.data[args]


AsciiGrid.push(Attributes)   # attribute data
AsciiGrid.push(Root)         # container
AsciiGrid.push(ASCFile)      # array

compass_model.push(AsciiGrid)
