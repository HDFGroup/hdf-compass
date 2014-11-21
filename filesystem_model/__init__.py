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
Example data model which represents the file system.

Subclasses just two node types: Container and Array, representing
directories and files respectively.
"""

import os
import os.path as op
import numpy as np

import compass_model

class Filesystem(compass_model.Store):

    """
        A "data store" represented by the file system.

        Keys are absolute paths on the local file system.
    """

    def __contains__(self, key):
        return op.exists(key)

    @property
    def url(self):
        return self._url

    @property
    def displayname(self):
        return "Local file system"

    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return self._valid

    @staticmethod
    def canhandle(url):
        if url == "file://localhost":
            return True
        return False

    def __init__(self, url):
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True

    def close(self):
        self._valid = False

    def getparent(self, key):
        if key == "/":
            return None
        return self[op.dirname(key)]


class Directory(compass_model.Container):

    """
        Represents a directory in the filesystem.
    """

    classkind = "Directory"

    @staticmethod
    def canhandle(store, key):
        return op.isdir(key)

    def __init__(self, store, key):
        self._store = store
        self._key = key
        try:
            self._names = os.listdir(key)
        except OSError:  # Permissions, etc.
            self._names = []

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        bn = op.basename(self.key)
        if len(bn) == 0:
            return "/"
        return bn

    @property
    def description(self):
        return 'Folder "%s" (%d members)' % (self.displayname, len(self))

    def __len__(self):
        return len(self._names)

    def __iter__(self):
        for name in self._names:
            key = op.join(self.key, name)
            yield self._store[key]

    def __getitem__(self, idx):
        key = op.join(self.key, self._names[idx])
        return self._store[key]


class File(compass_model.Array):

    """
        Represents a file (all loaded as an array of bytes)
    """

    classkind = "File"

    @staticmethod
    def canhandle(store, key):
        return op.isfile(key)

    def __init__(self, store, key):
        self._store = store
        self._key = key

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def displayname(self):
        return op.basename(self.key)

    @property
    def description(self):
        return 'File "%s", size %d bytes' % (self.displayname, op.getsize(self.key))

    @property
    def shape(self):
        return (op.getsize(self.key),)

    @property
    def dtype(self):
        return np.dtype('u1')

    def __getitem__(self, args):
        try:
            with open(self.key, 'rb') as f:
                data = np.fromstring(f.read(), dtype='u1')
        except OSError, IOError:
            data = np.zeros((len(self),), dtype='u1')

        return data[args]

Filesystem.push(File)
Filesystem.push(Directory)

compass_model.push(Filesystem)