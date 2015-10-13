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
Implementation of compass_model classes for BAG files.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import groupby
import sys
import os.path as op
import posixpath as pp
import h5py

from hydroffice.bag import is_bag
from hydroffice.bag import BAGFile
from hydroffice.bag import BAGError

from hdf_compass import compass_model
from hdf_compass.utils import url2path

import logging
log = logging.getLogger(__name__)


def sort_key(name):
    """ Sorting key for names in an BAG group.

    We provide "natural" sort order; e.g. "7" comes before "12".
    """
    return [(int(''.join(g)) if k else ''.join(g)) for k, g in groupby(name, key=unicode.isdigit)]


class BAGStore(compass_model.Store):
    """
    Data store implementation using a BAG file (closely mimicking HDF5Store).

    Keys are the full names of objects in the file.
    """
    file_extensions = {'BAG File': ['*.bag']}

    def __contains__(self, key):
        return key in self.f

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
        return op.basename(self.f.filename)

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return bool(self.f)

    @staticmethod
    def can_handle(url):
        log.debug("able to handle %s?" % url)
        if not url.startswith('file://'):
            log.debug("Invalid url: %s" % url)
            return False

        path = url2path(url)
        if not is_bag(path):
            log.debug("Not a BAG")
            return False

        log.debug("Yes")
        return True

    def __init__(self, url):
        if not self.can_handle(url):
            raise ValueError(url)
        self._url = url
        path = url2path(url)
        self.f = BAGFile(path, 'r')

    def close(self):
        self.f.close()

    def get_parent(self, key):
        # HDFCompass requires the parent of the root container be None
        if key == "" or key == "/":
            return None
        p_key = pp.dirname(key)
        if p_key == "":
            p_key = "/"
        return self[p_key]


class BAGGroup(compass_model.Container):
    """ Represents an BAG group (closely mimicking HDF5Group). """
    class_kind = "BAG Group"

    @staticmethod
    def can_handle(store, key):
        return (key in store) and (isinstance(store.f[key], h5py.Group))

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
    def display_name(self):
        name = pp.basename(self.key)
        if name == "":
            name = '/'
        return name

    @property
    def display_title(self):
        return "%s %s" % (self.store.display_name, self.key)

    @property
    def description(self):
        return 'Group "%s" (%d members)' % (self.display_name, len(self))

    def __len__(self):
        return len(self._group)

    def __iter__(self):
        for name in self._names:
            yield self.store[pp.join(self.key, name)]

    def __getitem__(self, idx):
        name = self._names[idx]
        return self.store[pp.join(self.key, name)]


class BAGRoot(compass_model.Container):
    """ Represents the BAG root. """
    class_kind = "BAG Root"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root") and (key in store) and (isinstance(store.f[key], h5py.Group))

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
    def display_name(self):
        name = pp.basename(self.key)
        return name

    @property
    def display_title(self):
        return "%s %s" % (self.store.display_name, self.key)

    @property
    def description(self):
        return 'Root Group "%s" (%d members)' % (self.display_name, len(self))

    def __len__(self):
        return len(self._group)

    def __iter__(self):
        for name in self._names:
            yield self.store[pp.join(self.key, name)]

    def __getitem__(self, idx):
        name = self._names[idx]
        return self.store[pp.join(self.key, name)]


class BAGDataset(compass_model.Array):
    """ Represents a BAG dataset (closely mimicking HDF5Dataset). """
    class_kind = "BAG Dataset"

    @staticmethod
    def can_handle(store, key):
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
    def display_name(self):
        return pp.basename(self.key)

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


class BAGElevation(compass_model.Array):
    """ Represents a BAG elevation. """
    class_kind = "BAG Elevation"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/elevation") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f.elevation(mask_nan=True)

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

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


class BAGTrackinList(compass_model.Array):
    """ Represents a BAG tracking list. """
    class_kind = "BAG Tracking List"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/tracking_list") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f.tracking_list()

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

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


class BAGMetadataRaw(compass_model.Array):
    """ Represents a raw BAG metadata. """
    class_kind = "BAG Metadata [raw]"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/metadata") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f.metadata(as_string=False, as_pretty_xml=False)

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

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


class BAGMetadataText(compass_model.Text):
    """ Represents a text BAG metadata. """

    class_kind = "BAG Metadata [text]"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/metadata") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    def __init__(self, store, key):
        self._store = store
        self._key = key
        try:
            self._dset = store.f.metadata(as_string=True, as_pretty_xml=True)
        except BAGError as e:
            log.warning("unable to retrieve metadata as xml")
            self._dset = ""

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

    @property
    def description(self):
        return 'Dataset "%s"' % (self.display_name,)

    @property
    def text(self):
        return self._dset


class BAGMetadataXml(compass_model.Xml):
    """ Represents a text BAG metadata. """

    class_kind = "BAG Metadata [xml]"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/metadata") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    @staticmethod
    def has_validation():
        """For BAG data there is a known validation mechanism based on XSD and Schematron"""
        return True

    def __init__(self, store, key):
        self._store = store
        self._key = key
        try:
            self._dset = store.f.metadata(as_string=True, as_pretty_xml=True)
        except BAGError as e:
            log.warning("unable to retrieve metadata as xml")
            self._dset = ""

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

    @property
    def description(self):
        return 'Dataset "%s"' % (self.display_name,)

    @property
    def text(self):
        return self._dset

    @property
    def validation(self):
        """ Collect a message string with the result of the validation """
        msg = str()

        msg += "XML input source: %s\nValidation output: " % self.key
        if self.store.f.validate_metadata():
            msg += "VALID"
        else:
            msg += "INVALID\nReasons:\n"
            for err_msg in self.store.f.meta_errors:
                msg += " - %s\n" % err_msg
        return msg


class BAGUncertainty(compass_model.Array):
    """ Represents a BAG uncertainty. """
    class_kind = "BAG Uncertainty"

    @staticmethod
    def can_handle(store, key):
        return (key == "/BAG_root/uncertainty") and (key in store) and (isinstance(store.f[key], h5py.Dataset))

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._dset = store.f.uncertainty(mask_nan=True)

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

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


class BAGKV(compass_model.KeyValue):
    """ A KeyValue node used for BAG attributes (closely mimicking HDF5KV). """
    class_kind = "BAG Attributes"

    @staticmethod
    def can_handle(store, key):
        return key in store.f

    def __init__(self, store, key):
        log.debug("init")
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
        return self._obj.attrs[name]


class BAGImage(compass_model.Image):
    """ BAG true-color images (closely mimicking HDF5Image). """
    class_kind = "BAG Truecolor Image"

    @staticmethod
    def can_handle(store, key):
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
        log.debug("init")
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
    def display_name(self):
        n = pp.basename(self.key)
        return n if n != '' else '/'

    @property
    def description(self):
        return self.display_name

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
BAGStore.push(BAGKV)
BAGStore.push(BAGDataset)
BAGStore.push(BAGElevation)
BAGStore.push(BAGUncertainty)
BAGStore.push(BAGTrackinList)
BAGStore.push(BAGMetadataRaw)
BAGStore.push(BAGMetadataText)
BAGStore.push(BAGMetadataXml)
BAGStore.push(BAGGroup)
BAGStore.push(BAGRoot)
BAGStore.push(BAGImage)

compass_model.push(BAGStore)
