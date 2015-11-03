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
from __future__ import absolute_import, division, print_function, unicode_literals

import posixpath as pp

import numpy as np
import pydap as dap
from pydap.client import open_url
from pydap.proxy import ArrayProxy

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from hdf_compass import compass_model


def check_key(key, dataset):
    if '/' not in key:
        return key, dataset
    new_dataset = dataset[key.split('/')[0]]
    return key.split('/')[1], new_dataset


class Server(compass_model.Store):
    """ Represents the remote OpENDAP server to be accessed """
    @staticmethod
    def plugin_name():
        return "OpENDAP"

    @staticmethod
    def plugin_description():
        return "A plugin used to access OpENDAP Servers."

    def __contains__(self, key):
        if '/' not in key:
            return key in self.dataset

        new_dset = self.dataset[key.split('/')[0]]
        new_key = key.rsplit('/')[1]

        return new_key in new_dset

    @staticmethod
    def can_handle(url):
        try:
            flag = isinstance(open_url(url), dap.model.DatasetType)
            log.debug("able to handle %s? %r" % (url, flag))
            return flag
        except Exception:
            log.debug("able to handle %s? no" % url)
            return False

    def __init__(self, url):
        if not self.can_handle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True
        self._dataset = open_url(self.url)
        self._datalength = len(self._dataset.data)
        self._dataset.setdefault('')

    def close(self):
        self._valid = False

    def get_parent(self, key):
        return None

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
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

    @property
    def datalength(self):
        return self._datalength


class Dataset(compass_model.Container):
    """ Represents Dataset/DatasetType Object in OpENDAP/Pydap. """

    class_kind = "Dataset"

    def __len__(self):
        return self._store.datalength

    def __getitem__(self, index):
        name = self._dset.keys()[index]
        return self.store[pp.join(self.key, name)]

    def __iter__(self):
        pass

    @staticmethod
    def can_handle(store, key):
        return key == ''

    def __init__(self, store, key):
        if not key == '':
            raise ValueError("A Dataset object may only represent the root group")
        self._store = store
        self._key = key
        self._url = store.url
        self._dset = store.dataset

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return self._dset.name

    @property
    def description(self):
        return "A Pydap DatasetType Object."

    @property
    def dset(self):
        return self._dset


class Structure(compass_model.Container):
    """ Represents Structure/StructureType Object in OpENDAP/Pydap. """

    class_kind = "Structure/Grid/Sequence"

    def __len__(self):
        return len(self._dset.data)

    def __getitem__(self, index):
        name = self._dset.keys()[index]
        return self.store[pp.join(self.key, name)]

    def __iter__(self):
        pass

    @staticmethod
    def can_handle(store, key):
        new_key, new_dset = check_key(key, store.dataset)
        try:
            return new_key in new_dset and isinstance(new_dset[new_key], dap.model.StructureType)
        except isinstance(new_dset[new_key], dap.model.DatasetType):
            return False

    def __init__(self, store, key):
        new_key, new_dset = check_key(key, store.dataset)

        self._store = store
        self._key = new_key
        self._url = store.url
        self._dset = new_dset[new_key]

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return self._dset.name

    @property
    def description(self):
        return "A Pydap StructureType Object."


class Base(compass_model.Array):
    """ Represents Array/BaseType Object in OpENDAP/Pydap. """

    class_kind = "Array"

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
    def can_handle(store, key):
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
    def display_name(self):
        return self._name

    @property
    def description(self):
        return "A Pydap BaseType Object."

    def is_plottable(self):
        if self.dtype.kind == 'S':
            log.debug("Not plottable since ASCII String (characters: %d)" % self.dtype.itemsize)
            return False
        if self.dtype.kind == 'U':
            log.debug("Not plottable since Unicode String (characters: %d)" % self.dtype.itemsize)
            return False
        return True


class Attributes(compass_model.KeyValue):
    """ Represents the Attributes member of Pydap Objects. """

    class_kind = "Attributes"

    @property
    def keys(self):
        return self._keys.keys()

    def __getitem__(self, name):
        return self._keys[name]

    @staticmethod
    def can_handle(store, key):
        new_key = check_key(key, store.dataset)
        return new_key != ''

    def __init__(self, store, key):
        new_key, new_dset = check_key(key, store.dataset)

        self._store = store
        self._key = new_key
        self._keys = new_dset[self._key].attributes

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return "%s Attributes" % self._key

    @property
    def description(self):
        return "Attributes of %s" % self._key


# Register Handlers
Server.push(Attributes)
Server.push(Dataset)
Server.push(Structure)
Server.push(Base)

compass_model.push(Server)
