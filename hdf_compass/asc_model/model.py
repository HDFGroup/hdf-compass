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
HDF Compass "pilot" plugin for viewing ASCII Grid Data.

Subclasses consist of a Container and an Array, representing
directories and the ASCII grid data respectively.
See: http://en.wikipedia.org/wiki/Esri_grid for a description of
the file format
"""
import os.path as op
import linecache

import numpy as np

import logging
logger = logging.getLogger(__name__)

from hdf_compass import compass_model
from hdf_compass.utils import url2path


class AsciiGrid(compass_model.Store):
    """ A "data store" represented by an ascii grid file. """

    @staticmethod
    def plugin_name():
        return "Ascii Grid"

    @staticmethod
    def plugin_description():
        return "A plugin used to browse Ascii Grid."

    file_extensions = {'ASC File': ['*.asc']}

    def __contains__(self, key):
        if key == '/':
            return True
        return False

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
        return op.basename(self._url)

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return self._valid

    @staticmethod
    def can_handle(url):
        if not url.startswith('file://'):
            logger.debug("able to handle %s? no, not starting with file://" % url)
            return False
        if not url.endswith('.asc'):
            logger.debug("able to handle %s? no, missing .asc extension" % url)
            return False

        first_line = open(url2path(url)).readline()
        if first_line.split()[0].upper() != "NCOLS":
            logger.debug("able to handle %s? no, invalid first line" % url)
            return False

        logger.debug("able to handle %s? yes" % url)
        return True

    def __init__(self, url):
        if not self.can_handle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True

    def close(self):
        self._valid = False

    def get_parent(self, key):
        return None

    def getFilePath(self):
        return url2path(self._url)


class ASCFile(compass_model.Array):
    """ Represents a .asc grid file. """

    class_kind = "ASCII Grid File"

    @staticmethod
    def can_handle(store, key):
        if key == '/':
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        file_path = self._store.getFilePath()
        self._nrows = int(linecache.getline(file_path, 1).lstrip("ncols"))
        self._ncols = int(linecache.getline(file_path, 2).lstrip("nrows"))
        self._data = None

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return self._store.display_name

    @property
    def description(self):
        return 'File "%s", size %d bytes' % (self.display_name, op.getsize(self.key))

    @property
    def shape(self):
        return self._nrows, self._ncols

    @property
    def dtype(self):
        return np.dtype('float')

    def __getitem__(self, args):
        if self._data is None:
            self._data = np.loadtxt(self._store.getFilePath(), skiprows=6, unpack=True)
        return self._data[args]


class Attributes(compass_model.KeyValue):
    class_kind = "Attributes of ASC Grid File"

    @staticmethod
    def can_handle(store, key):
        if key == '/':
            return True
        return False

    def __init__(self, store, key):
        self._store = store
        self._key = key
        file_path = self._store.getFilePath()
        self.data = {'NODATA Value': float(linecache.getline(file_path, 6).lstrip("NODATA_value")),
                     'cellsize': float(linecache.getline(file_path, 5).lstrip("cellsize")),
                     'yllcorner': float(linecache.getline(file_path, 4).lstrip("yllcorner")),
                     'xllcorner': float(linecache.getline(file_path, 3).lstrip("xllcorner"))}

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return self.key

    @property
    def description(self):
        return self.display_name

    def close(self):
        self._valid = False

    @property
    def keys(self):
        return self.data.keys()

    def __getitem__(self, args):
        return self.data[args]


AsciiGrid.push(Attributes)  # attribute data
AsciiGrid.push(ASCFile)  # array

compass_model.push(AsciiGrid)
