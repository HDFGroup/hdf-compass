"""
HDF Compass plugin for accessing an OpENDAP server. 
"""

import numpy as np
import posixpath as pp
from pydap.client import open_url
from pydap.model import *
from pydap.proxy import ArrayProxy

import compass_model

class Server(compass_model.Store):

    """
        #Represents the remote OpENDAP derver to be accessed
    """

    def __contains__(self, key):
        if key == '/':
            return True
        return False

    @staticmethod
    def canhandle(url):
        if not url.startswith('http://'):
            return False
        return True

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True
        self._dataset = open_url(self._url)

    def close(self):
        self._valid = False
        print 5

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
        return self['/']

    @property
    def valid(self):
        return self._valid


class Structure(compass_model.Container):

    """
        Represents Structure/StructureType Object in OpENDAP/Pydap
    """

    classkind = "Structure"

    def __len__(self):
        return len(self._dset.data)

    def __getitem__(self, index):
        return self._dset.get(self._dset.keys()[index])

    def __iter__(self):
        pass

    @staticmethod
    def canhandle(store, key):
        if type(store._dataset) == DatasetType or type(store._dataset) == StructureType:
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key 
        self._url = store.url
        self._dset = open_url(self._url)

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
    #Represents Array/BaseType Object in OpENDAP/Pydap
    """

    classkind = "Base"

    @property
    def shape(self):
        return self._dset.shape

    @property
    def dtype(self):
        return self._dset.dtype

    def __getitem__(self, indices):
        return self._dset[indices]

    @staticmethod
    def canhandle(store, key):
        if type(store._dataset) == BaseType:
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._id = self.id
        self._url = store.url
        self._shape = self.shape
        self._dset = ArrayProxy(self._id, self._url, self._shape)#[:]

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
        return self._dset.id

    @property
    def id(self):
        return self._id

# Register Handlers
Server.push(Structure)
Server.push(Base)

compass_model.push(Server)