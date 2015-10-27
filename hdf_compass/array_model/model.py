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

""" Testing model for array types. """

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import os.path as op

import logging
log = logging.getLogger(__name__)

from hdf_compass import compass_model

DT_CMP = np.dtype([(b'a', b'i'), (b'b', b'f')])

DATA = {'array://localhost/a_0d': np.array(1),
        'array://localhost/a_1d': np.arange(10),
        'array://localhost/a_2d': np.arange(10 * 10).reshape((10, 10)),
        'array://localhost/a_3d': np.arange(10 * 10 * 10).reshape((10, 10, 10)),
        'array://localhost/a_4d': np.arange(10 * 10 * 10 * 10).reshape((10, 10, 10, 10)),
        'array://localhost/cmp_0d': np.array((1, 2), dtype=DT_CMP),
        'array://localhost/cmp_1d': np.ones((10,), dtype=DT_CMP),
        'array://localhost/cmp_2d': np.ones((10, 10), dtype=DT_CMP),
        'array://localhost/cmp_3d': np.ones((10, 10, 10), dtype=DT_CMP),
        'array://localhost/cmp_4d': np.ones((10, 10, 10, 10), dtype=DT_CMP),
        'array://localhost/S_0d': np.array(b"Hello"),
        'array://localhost/S_1d': np.array([b"Hello", b"Ciao"]),
        'array://localhost/S_2d': np.array([[b"Hello", b"Ciao"], [b"Hello", b"Ciao"]]),
        'array://localhost/S_3d': np.array([[[b"Hello", b"Ciao"], [b"Hello", b"Ciao"]],
                                            [[b"Hello", b"Ciao"], [b"Hello", b"Ciao"]]]),
        'array://localhost/U_1d': np.array(["Hello", "Ciao"]),
        'array://localhost/U_2d': np.array([["Hello", "Ciao"], ["Hello", "Ciao"]]),
        'array://localhost/U_3d': np.array([[["Hello", "Ciao"], ["Hello", "Ciao"]],
                                            [["Hello", "Ciao"], ["Hello", "Ciao"]]]),
        'array://localhost/v_0d': np.array('\x01', dtype='|V1'),
        'array://localhost/non_square': np.arange(5 * 10).reshape((5, 10)),
        }


class ArrayStore(compass_model.Store):
    """
        A "data store" represented by a set of arrays in memory.

        Keys are array names as reported in DATA.
    """

    def __contains__(self, key):
        if (key == '/') or (key is None):
            log.debug("is root: %s" % key)
            return True
        return key in DATA

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
        return "Testing arrays"

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return self._valid

    @staticmethod
    def can_handle(url):
        if url == "array://localhost":
            log.debug("able to handle %s? yes" % url)
            return True
        log.debug("able to handle %s? no" % url)
        return False

    def __init__(self, url):
        if not self.can_handle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True

    def close(self):
        self._valid = False

    def get_parent(self, key):
        if key is None:
            return None
        if key == "/":
            return None
        return self[op.dirname(key)]


class ArrayContainer(compass_model.Container):
    """ Represents a container of in-memory array. """

    class_kind = "Array Container"

    @staticmethod
    def can_handle(store, key):
        return (key == '/') or (key is None)

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
    def display_name(self):
        return "/"

    @property
    def description(self):
        return self.display_name

    def __len__(self):
        return len(DATA)

    def __iter__(self):
        for name in self._names:
            yield self._store[name]

    def __getitem__(self, idx):
        key = self._names[idx]
        return self._store[key]


class Array(compass_model.Array):
    """ An N-D array """

    class_kind = "TestArray"

    @staticmethod
    def can_handle(store, key):
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
    def display_name(self):
        return self.key.rsplit('/', 1)[-1]

    @property
    def description(self):
        return self.display_name

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    def __getitem__(self, args):
        return self.data[args]

    def is_plottable(self):
        if self.dtype.kind == 'S':
            log.debug("Not plottable since ASCII String (characters: %d)" % self.dtype.itemsize)
            return False
        if self.dtype.kind == 'U':
            log.debug("Not plottable since Unicode String (characters: %d)" % self.dtype.itemsize)
            return False
        return True


class ArrayText(compass_model.Text):
    """ Represents a text array (both ASCII and UNICODE). """

    class_kind = "TestArray [text]"

    @staticmethod
    def can_handle(store, key):
        if key not in DATA:
            return False

        if DATA[key].dtype.kind == 'S':
            # log.debug("ASCII String (characters: %d)" % DATA[key].dtype.itemsize)
            return True
        if DATA[key].dtype.kind == 'U':
            # log.debug("Unicode String (characters: %d)" % DATA[key].dtype.itemsize)
            return True
        return False

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
    def display_name(self):
        return self.key.rsplit('/', 1)[-1]

    @property
    def description(self):
        return 'Text "%s"' % (self.display_name,)

    @property
    def shape(self):
        return self.data.shape

    @property
    def text(self):
        txt = str()

        if len(self.shape) == 0:
            print(self.data)
            txt += str(self.data)

        elif len(self.shape) == 1:
            for el in self.data:
                txt += el + ",\n"

        elif len(self.shape) == 2:
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):
                    txt += self.data[i, j] + ", "
                txt += "\n"

        else:
            txt = ">> display of more than 2D string array not implemented <<"

        return txt


class ArrayKV(compass_model.KeyValue):
    class_kind = "Array Key/Value Attrs"

    @staticmethod
    def can_handle(store, key):
        return key in DATA

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self.data = {'a': np.array((1, 2)), 'b': np.array("Hello"), 'c': np.array('\x01', dtype='|V1')}

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return self.key.rsplit('/', 1)[-1]

    @property
    def description(self):
        return self.display_name

    @property
    def keys(self):
        return self.data.keys()

    def __getitem__(self, args):
        return self.data[args]


ArrayStore.push(ArrayKV)
ArrayStore.push(ArrayContainer)
ArrayStore.push(Array)
ArrayStore.push(ArrayText)

compass_model.push(ArrayStore)
