"""
HDF Compass plugin for accessing an OpENDAP server.
"""

import numpy as np
import posixpath as pp
import pydap as dap
from pydap.client import open_url
from pydap.proxy import ArrayProxy

import compass_model


def check_key(key, dataset):
    if not '/' in key:
        return key, dataset
    new_dataset = dataset[key.split('/')[0]]
    return key.split('/')[1], new_dataset


class Server(compass_model.Store):

    """
        Represents the remote OpENDAP derver to be accessed
    """
    def __contains__(self, key):
        if key.count('/') not in (0, 1):
            return False

        if '/' not in key:
            return key in self.dataset

        new_dset = self.dataset[key.split('/')[0]]
        new_key = key.rsplit('/')[1]

        return new_key in new_dset

    @staticmethod
    def canhandle(url):
        try:
            return isinstance(open_url(url), dap.model.DatasetType)
        except Exception:
            return False

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True
        self._dataset = open_url(self.url)

        self.dataset.setdefault('')

    def close(self):
        self._valid = False

    def getparent(self, key):
        return None

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return self.dataset.name

    @property
    def root(self):
        return self['']

    @property
    def valid(self):
        return self._valid

    @property
    def dataset(self):
        return self._dataset


class Dataset(compass_model.Container):

    """
        Represents Dataset/DatasetType Object in OpENDAP/Pydap.
    """

    classkind = "Dataset"

    def __len__(self):
        return len(self._dset.data)

    def __getitem__(self, index):
        name = self._dset.keys()[index]

        return self.store[pp.join(self.key, name)]

    def __iter__(self):
        pass

    @staticmethod
    def canhandle(store, key):
        return isinstance(store.dataset, dap.model.DatasetType)

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
        return self.dset.name

    @property
    def description(self):
        return "A Pydap DatasetType Object."

    @property
    def dset(self):
        return self._dset


class Grid(compass_model.Container):

    """
        Represents Structure/StructureType Object in OpENDAP/Pydap.
    """

    classkind = "Grid"

    def __len__(self):
        return len(self._dset.data)

    def __getitem__(self, index):
        name = self._dset.keys()[index]
        return self.store[pp.join(self.key, name)]

    def __iter__(self):
        pass

    @staticmethod
    def canhandle(store, key):
        new_key, new_dset = check_key(key, store.dataset)
        return new_key in new_dset and isinstance(new_dset[new_key], dap.model.GridType)

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._url = store.url
        self._dset = store.dataset[key]

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
        return "A Pydap GridType Object."


class Base(compass_model.Array):

    """
        Represents Array/BaseType Object in OpENDAP/Pydap.
    """

    classkind = "NumPy Array"

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return np.dtype(self._dtype.typecode)

    def __getitem__(self, index):
        if self._data is None:
            self._data = ArrayProxy(self._id, self._url, self._shape)[:]
        return self._data[index]

    @staticmethod
    def canhandle(store, key):
        new_key, new_dset = check_key(key, store.dataset)
        return new_key in new_dset and isinstance(new_dset[new_key], dap.model.BaseType)

    def __init__(self, store, key):
        new_key, new_dset = check_key(key, store.dataset)

        self._store = store
        self._key = new_key
        self._url = store.url
        self._id = new_dset[new_key].id

        self._shape = new_dset[new_key].shape
        self._dtype = new_dset[new_key].type
        self._name = new_dset[new_key].name

        self._data = None

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
        return "A Pydap BaseType Object."

# Register Handlers
Server.push(Dataset)
Server.push(Grid)
Server.push(Base)

compass_model.push(Server)
