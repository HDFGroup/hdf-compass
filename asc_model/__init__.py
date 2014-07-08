"""
HDF Compass "pilot" plugin for viewing ASCII Grid Data.

Subclasses consist of a Container and an Array, representing
directories and the ASCII grid data respectively.
"""

import os
import os.path as op
import numpy as np
import linecache

import compass_model

class Filesystem(compass_model.Store):
    
    """
        A "data store" represented by the file system.

        Keys are absolute paths on the local file system.
    """

    def __contains__(self, key):
        return op.exists(key)

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return "Local File System"

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return self._valid

    @staticmethod
    def canhandle(url):
        if url == "asc://localhost":
            return True
        return False

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._value = True

    def close(self):
        self._valid = False

    def getparent(self, key):
        if key == '/':
            return None
        return self[op.dirname(key)]


class Directory(compass_model.Container):

    """
        Represents a directory in the file system.
    """

    classkind = "Directory"

    @staticmethod
    def canhandle(store, key):
        return op.isdir(key)

    def __init__(self, store, key):
        self._store = store
        self._key = key
        try:
            self._names = [s for s in os.listdir(key) if s.endswith('.asc') or op.isdir(op.join(key, s))]
        except OSError: 
            self._names = []

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        bn = op.basename(self.key)
        if len(bn) == 0:
            return "/"
        return bn

    @property
    def description(self):
        return 'folder "%s" (%d members)' % (self.displayname, len(self))

    def __len__(self):
        return len(self._names)

    def __iter__(self):
        for name in self._names:
            key = op.join(self.key, name)
            yield self._store[key]

    def __getitem__(self, idx):
        key = op.join(self.key, self._names[idx])
        return self._store[key]


class ASCFile(compass_model.Array):

    """
        Represents a .asc grid file.
    """

    classkind = "ASCII Grid File"

    @staticmethod
    def canhandle(store, key):
        return op.isfile(key) and key.endswith('.asc')

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._nrows = int(linecache.getline(self._key, 1).lstrip("ncols"))
        self._ncols = int(linecache.getline(self._key, 2).lstrip("nrows"))
        self._data = None

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return op.basename(self._key)

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
            self._data = np.loadtxt(self._key, skiprows=6, unpack=True)
        return self._data[args]


class Attributes(compass_model.KeyValue):

    classkind = "Attributes of ASC Grid File" 

    @staticmethod
    def canhandle(store, key):
        return op.isfile(key) and key.endswith('.asc')

    def __init__(self, store, key):
        self._store = store
        self._key = key 
        self.data = {'NODATA Value': float(linecache.getline(self._key, 6).lstrip("NODATA_value")),
          'cellsize': float(linecache.getline(self._key, 5).lstrip("cellsize")),
          'yllcorner': float(linecache.getline(self._key, 4).lstrip("yllcorner")),
          'xllcorner': float(linecache.getline(self._key, 3).lstrip("xllcorner"))}

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


Filesystem.push(Attributes)
Filesystem.push(Directory)
Filesystem.push(ASCFile)

compass_model.push(Filesystem)