##############################################################################
# Copyright by The HDF Group.                                                #
#              Helmholtz-Zentrum Dresden - Rossendorf,                       #
#                Computational Radiation Physics                             #
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
Implementation of compass_model classes for ADIOS files.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import groupby
import sys
import os.path as op
import posixpath as pp

import adios as ad

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Py2App can't successfully import otherwise
from hdf_compass import compass_model
from hdf_compass.utils import url2path


def sort_key(name):
    """ Sorting key for names in an HDF5 group.
    We provide "natural" sort order; e.g. "7" comes before "12".
    """
    return [(int(''.join(g)) if k else ''.join(g)) for k, g in groupby(name, key=unicode.isdigit)]


class ADIOSStore(compass_model.Store):
    """
    Data store implementation using an ADIOS file.

    Keys are the full names of objects in the file.
    """
    @staticmethod
    def plugin_name():
        return "ADIOS"

    @staticmethod
    def plugin_description():
        return "A plugin used to browse ADIOS files."

    file_extensions = {'ADIOS File': ['*.bp']}

    def __contains__(self, key):
        return key in self.f.var

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
        return op.basename(self.f.name)

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return bool(self.f)

    @staticmethod
    def can_handle(url):
        if not url.startswith('file://'):
            log.debug("able to handle %s? no, not starting with file://" % url)
            return False
        if not url.endswith('.bp'):
            log.debug("able to handle %s? no, missing .bp ending" % url)
            return False

        log.debug("able to handle %s? yes" % url)
        return True

    def __init__(self, url):
        try:
            self._url = url
            path = url2path(url).encode("ascii")
            self.f = ad.file(path)
            
        except:
            raise ValueError(url)

        keylist = self.f.var.keys()
        for key in keylist:
            if(not key.startswith("/")):
                nkey = "/%s" % key
                self.f.var[nkey] = self.f.var.pop(key)
                key = nkey;

            if(key != "/"):
                pkey = pp.dirname(key)
                self.f.var.update({pkey:None})

        self.r = ADIOSGroup(self, "/")

    def close(self):
        self.f.close()

    def get_parent(self, key):
        # HDFCompass requires the parent of the root container be None
        if key == "" or key == "/":
            return None

        pkey = pp.dirname(key)
        if pkey == "":
            pkey = "/"

        return self[pkey]

class ADIOSGroup(compass_model.Container):
    """ Represents an HDF5 group, to be displayed in the browser view. """

    class_kind = "ADIOS Group"

    @staticmethod
    def can_handle(store, key):
        if(key in store):
            if(store.f.var[key] == None):
                return True
        return False

    @property
    def _names(self):
        # Lazily build the list of names; this helps when browsing big files
        if self._xnames is None:
            self._xnames = list(map(lambda k:  op.basename(k), self._group.keys()))
            
            # Natural sort is expensive
            if len(self._xnames) < 1000:
                self._xnames.sort()

        return self._xnames

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._xnames = None

        self._group = {}
        c = self._key.count('/')
        if(self._key != "/"):
            c = c+1

        for k in self._store.f.var.keys():
            if(k.startswith(self._key) and k.count('/') <= c and k != self._key):
                self._group.update({k:store.f.var[k]})

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        name = pp.basename(self.key)
        if name == "":
            name = '/'
        return name

    @property
    def display_title(self):
        return "%s %s" % (self.store.display_name, self._key)

    @property
    def description(self):
        return 'Group "%s" (%d members)' % (self.display_name, len(self))

    def __len__(self):
        return len(self._group)

    def __iter__(self):
        for name in self._names:
            yield self.store.var[pp.join(self._key, name)]

    def __getitem__(self, idx):
        name = self._names[idx]
        key = pp.join(self._key, name)
        return self._store[key]

class ADIOSDataset(compass_model.Array):
    """ Represents an ADIOS dataset. """

    class_kind = "ADIOS Dataset"

    @staticmethod
    def can_handle(store, key):
        if(key != "/" and key in store and isinstance(store.f.var[key], ad.var)):
            return True
        else:
            return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f.var[key]

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self._key)

    @property
    def description(self):
        return 'Dataset "%s"' % (self.display_name,)

    @property
    def shape(self):
        return self._dset.shape

    @property
    def dtype(self):
        return self._dset.dtype

    def __getitem__(self, args):
        return self._dset[args]

    def is_plottable(self):
        if self.dtype.kind == 'S':
            log.debug("Not plottable since ASCII String (characters: %d)" % self.dtype.itemsize)
            return False
        if self.dtype.kind == 'U':
            log.debug("Not plottable since Unicode String (characters: %d)" % self.dtype.itemsize)
            return False
        return True

class ADIOSText(compass_model.Text):
    """ Represents a text array (both ASCII and UNICODE). """

    class_kind = "ADIOS Dataset[text]"

    @staticmethod
    def can_handle(store, key):
        if(key != "/" and key in store and isinstance(store.f.var[key], ad.var)):
            if store.f.var[key].dtype.kind == 'S':
                log.debug("ASCII String (characters: %d)" % DATA[key].dtype.itemsize)
                return True
            if store.f.var[key].dtype.kind == 'U':
                log.debug("Unicode String (characters: %d)" % DATA[key].dtype.itemsize)
                return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self.data = store.f.var[key]

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return "displayname"

    @property
    def description(self):
        return 'Text "%s"' % (self.display_name,)

    @property
    def text(self):
        return self.data;

class ADIOSKV(compass_model.KeyValue):
    """ A KeyValue node used for ADIOS attributes. """

    class_kind = "ADIOS Attributes"

    @staticmethod
    def can_handle(store, key):
        if(key != "/" and key in store and store.f.var[key] != None):
            return True
        else:
            return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._obj = store.f.var[key]
        self._names = self._obj.attrs.keys()

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        n = pp.basename(self.key)
        return n if n != '' else '/'

    @property
    def description(self):
        return self.display_name

    @property
    def keys(self):
        return self._names[:]

    def __getitem__(self, name):
        a = self._obj.attrs[name]
        return a.value

# Register handlers    
ADIOSStore.push(ADIOSGroup)
ADIOSStore.push(ADIOSKV)
ADIOSStore.push(ADIOSDataset)
ADIOSStore.push(ADIOSText)

compass_model.push(ADIOSStore)
