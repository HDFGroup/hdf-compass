"""
    HDF Compass plugin for accessing an OpENDAP server.
"""

import numpy as np
import posixpath as pp
from pydap.model import *
from pydap.client import open_url
from pydap.proxy import ArrayProxy

import compass_model


class Server(compass_model.Store):

    """
        Represents the remote OpENDAP derver to be accessed
    """

    def __contains__(self, key):
        return key in self._dataset

    @staticmethod
    def canhandle(url):
        try:
            return isinstance(open_url(url), DatasetType)
        except Exception:
            return False

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True
        self._dataset = open_url(self._url)
        self._dataset.setdefault('')

    def close(self):
        self._valid = False

    def getparent(self, key):
        return None

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return self._dataset.name

    @property
    def root(self):
        return self['']

    @property
    def valid(self):
        return self._valid

    @property
    def dataset(self):
        return self._dataset


class Structure(compass_model.Container):

    """
        Represents Structure/StructureType Object in OpENDAP/Pydap
    """

    classkind = "Structure"

    def __len__(self):
        return len(self._dset.data)

    def __getitem__(self, index):
        name = self._dset.keys()[index]
        return self.store[pp.join(self.key, name)]

    def __iter__(self):
        for name in self._dset.keys():
            yield self.store[pp.join(self.key, name)]

    @staticmethod
    def canhandle(store, key):
        return key in store.dataset and isinstance(store.dataset, StructureType)

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._url = store.url
        self._dset = open_url(store.url)

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return self._dset.name

    @property
    def description(self):
        return "Testing Structure Implementation"


class Base(compass_model.Array):

    """
        Represents Array/BaseType Object in OpENDAP/Pydap
    """

    classkind = "BaseType - NumPy Array"

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return np.dtype(self._dtype)

    def __getitem__(self, index):
        if self._data is None:
            self._data = ArrayProxy(self._id, self._url, self._shape)[:]
        return self._data[index]

    @staticmethod
    def canhandle(store, key):
        return key in store.dataset and isinstance(store.dataset[key], BaseType)

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._url = store.url
        self._data = None

        self._id = store.dataset[key].id
        self._shape = store.dataset[key].shape
        self._dtype = store.dataset[key].type
        self._name = store.dataset[key].name

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return self._name

    @property
    def description(self):
        return "A Descriptive String"

# Register Handlers
Server.push(Structure)
Server.push(Base)

compass_model.push(Server)
