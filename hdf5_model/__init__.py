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
Implementation of compass_model classes for HDF5 files.
"""

from itertools import groupby
import os
import os.path as op
import posixpath as pp
import numpy as np
import h5py

# Py2App can't successfully import otherwise
from h5py import defs, utils, h5ac, _proxy, _conv

import compass_model


def sort_key(name):
    """ Sorting key for names in an HDF5 group.

    We provide "natural" sort order; e.g. "7" comes before "12".
    """
    return [(int(''.join(g)) if k else ''.join(g)) for k, g in groupby(name, key=unicode.isdigit)]


class HDF5Store(compass_model.Store):

    """
    Data store implementation using an HDF5 file.

    Keys are the full names of objects in the file.
    """

    file_extensions = {'HDF5 File': ['*.hdf5', '*.h5']}
    
    def __contains__(self, key):
        return key in self.f


    @property
    def url(self):
        return self._url


    @property
    def displayname(self):
        return op.basename(self.f.filename)


    @property
    def root(self):
        return self['/']


    @property
    def valid(self):
        return bool(self.f)


    @staticmethod
    def canhandle(url):
        if not url.startswith('file://'):
            return False
        path = url.replace('file://','')
        if not h5py.is_hdf5(path):
            return False
        return True


    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        path = url.replace('file://','')
        self.f = h5py.File(path, 'r')


    def close(self):
        self.f.close()


    def getparent(self, key):
        # HDFCompass requires the parent of the root container be None
        if key == "" or key == "/":     
            return None
        pkey = pp.dirname(key)
        if pkey == "":
            pkey = "/"
        return self[pkey]



class HDF5Group(compass_model.Container):

    """
    Represents an HDF5 group, to be displayed in the browser view.
    """

    classkind = "HDF5 Group"


    @staticmethod
    def canhandle(store, key):
        return key in store and isinstance(store.f[key], h5py.Group)


    @property
    def _names(self):

        # Lazily build the list of names; this helps when browsing big files
        if self._xnames is None:

            self._xnames = list(self._group)

            # Natural sort is expensive
            if len(self._xnames) < 1000:
                self._xnames.sort(key=sort_key)

        return self._xnames


    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._group = store.f[key]
        self._xnames = None


    @property
    def key(self):
        return self._key


    @property
    def store(self):
        return self._store


    @property
    def displayname(self):
        name = pp.basename(self.key)
        if name == "":
            name = '/'
        return name


    @property
    def displaytitle(self):
        return "%s %s" % (self.store.displayname, self.key)


    @property
    def description(self):
        return 'Group "%s" (%d members)' % (self.displayname, len(self))


    def __len__(self):
        return len(self._group)


    def __iter__(self):
        for name in self._names:
            yield self.store[pp.join(self.key,name)]


    def __getitem__(self, idx):
        name = self._names[idx]
        return self.store[pp.join(self.key, name)]


class HDF5Dataset(compass_model.Array):

    """
    Represents an HDF5 dataset.
    """

    classkind = "HDF5 Dataset"


    @staticmethod
    def canhandle(store, key):
        return key in store and isinstance(store.f[key], h5py.Dataset)


    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f[key]


    @property
    def key(self):
        return self._key


    @property
    def store(self):
        return self._store


    @property
    def displayname(self):
        return pp.basename(self.key)


    @property
    def description(self):
        return 'Dataset "%s"' % (self.displayname,)


    @property
    def shape(self):
        return self._dset.shape


    @property
    def dtype(self):
        return self._dset.dtype


    def __getitem__(self, args):
        return self._dset[args]


class HDF5KV(compass_model.KeyValue):

    """
    A KeyValue node used for HDF5 attributes.
    """

    classkind = "HDF5 Attributes"


    @staticmethod
    def canhandle(store, key):
        return key in store.f


    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._obj = store.f[key]
        self._names = self._obj.attrs.keys()


    @property
    def key(self):
        return self._key


    @property
    def store(self):
        return self._store


    @property
    def displayname(self):
        n = pp.basename(self.key)
        return n if n != '' else '/'


    @property
    def description(self):
        return self.displayname


    @property
    def keys(self):
        return self._names[:]


    def __getitem__(self, name):
        return self._obj.attrs[name]


class HDF5Image(compass_model.Image):

    """
    True-color images.
    """

    classkind = "HDF5 Truecolor Image"


    @staticmethod
    def canhandle(store, key):
        if key not in store:
            return False
        obj = store.f[key]
        if obj.attrs.get('CLASS') != 'IMAGE':
            return False
        if obj.attrs.get('IMAGE_SUBCLASS') != 'IMAGE_TRUECOLOR':
            return False
        if obj.attrs.get('INTERLACE_MODE') != 'INTERLACE_PIXEL':
            return False
        return True


    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._obj = store.f[key]


    @property
    def key(self):
        return self._key


    @property
    def store(self):
        return self._store


    @property
    def displayname(self):
        n = pp.basename(self.key)
        return n if n != '' else '/'


    @property
    def description(self):
        return self.displayname


    @property
    def width(self):
        return self._obj.shape[1]


    @property
    def height(self):
        return self._obj.shape[0]


    @property
    def palette(self):
        return None


    @property
    def data(self):
        return self._obj[:]


# Register handlers    
HDF5Store.push(HDF5KV)
HDF5Store.push(HDF5Dataset)
HDF5Store.push(HDF5Group)
HDF5Store.push(HDF5Image)

compass_model.push(HDF5Store)