# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

"""
Testing model for array types.
"""

import os
import os.path as op
import numpy as np

import compass_model

import numpy as np

DT_CMP = np.dtype([('a','i'),('b','f')])

DATA = {'a_0d': np.array(1),
        'a_1d': np.arange(10),
        'a_2d': np.arange(10*10).reshape((10,10)),
        'a_3d': np.arange(10*10*10).reshape((10,10,10)),
        'a_4d': np.arange(10*10*10*10).reshape((10,10,10,10)),
        'cmp_0d': np.array((1,2), dtype=DT_CMP),
        'cmp_1d': np.ones((10,), dtype=DT_CMP),
        'cmp_2d': np.ones((10,10), dtype=DT_CMP),
        'cmp_3d': np.ones((10,10,10),dtype=DT_CMP),
        'cmp_4d': np.ones((10,10,10,10),dtype=DT_CMP),
        's_0d': np.array("Hello"),
        's_1d': np.array(("Hello",)),
        'v_0d': np.array('\x01', dtype='|V1'),
        }

class ArrayStore(compass_model.Store):

    """
        A "data store" represented by the file system.

        Keys are absolute paths on the local file system.
    """

    def __contains__(self, key):
        return key in DATA

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return "Testing arrays"

    @property
    def root(self):
        return ArrayContainer(self, None)

    @staticmethod
    def canhandle(url):
        if url == "array://localhost":
            return True
        return False

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url

    def close(self):
        pass

    def getparent(self, key):
        return self.root


class ArrayContainer(compass_model.Container):

    """
        Represents a directory in the filesystem.
    """

    classkind = "Array Container"

    @staticmethod
    def canhandle(store, key):
        return key is None

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._names = sorted(DATA.keys())

    @property
    def key(self):
        return None

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return "Array Container"

    @property
    def description(self):
        return self.displayname

    def __len__(self):
        return len(DATA)

    def __iter__(self):
        for name in self._names:
            yield self._store[name]

    def __getitem__(self, idx):
        key = self._names[idx]
        return self._store[key]


class Array(compass_model.Array):

    """
        An N-D array
    """

    classkind = "TestArray"

    @staticmethod
    def canhandle(store, key):
        return key in DATA

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self.data = DATA[key]

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return self.key

    @property
    def description(self):
        return self.displayname

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    def __getitem__(self, args):
        return self.data[args]


class ArrayKV(compass_model.KeyValue):

    classkind = "Array Key/Value Attrs"

    @staticmethod
    def canhandle(store, key):
        return key in DATA

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self.data = {'a': np.array((1,2)), 'b': np.array("Hello"), 'c': np.array('\x01', dtype='|V1')}

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

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


ArrayStore.push(ArrayKV)
ArrayStore.push(ArrayContainer)
ArrayStore.push(Array)

compass_model.push(ArrayStore)