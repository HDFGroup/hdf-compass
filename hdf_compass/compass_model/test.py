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
Provides support for testing basic properties of data model implementations.

Checks to make sure all required properties and methods are implemented, and
does basic sanity/consistency checking.  More specific tests must be written
by plugin authors.

The public interface consists of the following functions, each of which
provides a TestCase subclass which may be used with unittest:

- store
- container
- array [not implemented]
- key-value [not implemented]
- image [not implemented]

Example, in my_model.test:

    from hdf_compass.compass_model.test import store, container
    from hdf_compass.my_model import MyStore, MyContainer

    URL = "file:///path/to/myfile.ext"

    store_tests = store(MyStore, URL)
    container_tests = container(MyStore, URL, MyContainer, "some-key")

To run unittest, which discovers classes "store_tests" and "container_tests":

    $ python -m unittest hdf_compass.my_model.test

"""

from __future__ import absolute_import, division, print_function

import unittest as ut

from . import Node, Store


# --- Public API --------------------------------------------------------------

def store(store_cls_, url_):
    """ Construct a TestCase appropriate for a Store subclass.

    store_cls_: Your compass_model.Store implementation.
    url_:       A URL representing a valid data-store to test against.
    """

    class TestStore(_TestStore):
        store_cls = store_cls_
        url = url_

    return TestStore


def container(store_cls_, url_, node_cls_, key_):
    """ Construct a TestCase class appropriate for a Container subclass.

    store_cls_: Your compass_model.Store implementation.
    url_:       A URL representing a valid data-store to test against.
    node_cls_:  Your compass_model.Container implementation.
    key_:       A valid key which points to a container.
    """

    class TestContainer(_TestContainer):
        store_cls = store_cls_
        url = url_
        node_cls = node_cls_
        key = key_

    return TestContainer


# --- End public API ----------------------------------------------------------


class _TestStore(ut.TestCase):
    """ Base class for testing Stores. """

    store_cls = None
    url = None

    def setUp(self):
        self.store = self.store_cls(self.url)

    def tearDown(self):
        if self.store.valid:
            self.store.close()

    def test_class(self):
        """ Verify the thing we get from store_cls is actually a Store """
        self.assertIsInstance(self.store, Store)

    def test_url(self):
        """ Verify store.url produces a string """
        self.assertIsInstance(self.store.url, basestring)

    def test_display_name(self):
        """ Verify store.display_name produces a string. """
        self.assertIsInstance(self.store.display_name, basestring)

    def test_root(self):
        """ Verify store.root exists and has no parent """
        self.assertIsInstance(self.store.root, Node)
        self.assertIs(self.store.get_parent(self.store.root.key), None)

    def test_close_valid(self):
        """ Verify that store.close() works and is reflected by store.valid """
        self.assertTrue(self.store.valid)
        self.store.close()
        self.assertFalse(self.store.valid)

    def test_can_handle(self):
        """ Verify can_handle() works properly """
        self.assertTrue(self.store_cls.can_handle(self.url))
        self.assertFalse(self.store_cls.can_handle("file:///no/such/path"))

    def test_handlers(self):
        """ The implementation has at least one Node handler registered """
        h = self.store.gethandlers()
        # Test for N > 1 because compass_model.Unknown is always present
        self.assertGreater(len(h), 1)


class _TestNode(ut.TestCase):
    """ Base class for testing Node objects. """

    store_cls = None
    node_cls = None
    url = None
    key = None

    def setUp(self):
        self.store = self.store_cls(self.url)
        self.node = self.node_cls(self.store, self.key)

    def tearDown(self):
        if self.store.valid:
            self.store.close()

    def test_contains(self):
        """ Consistency check for store __contains___ """
        self.assertTrue(self.key in self.store)
        self.assertFalse("key_not_in_store" in self.store)

    def test_icons(self):
        """ Icon dict is present and contains valid icon paths:

        keys: int
        values: icon paths

        Required sizes: 16x16 and 64x64
        """
        import os
        for key, val in self.node_cls.icons.iteritems():
            self.assertIsInstance(key, int)
            self.assertIsInstance(val, unicode)
            self.assertTrue(os.path.exists(val))

        # required resolutions
        self.assertIn(16, self.node_cls.icons)
        self.assertIn(64, self.node_cls.icons)

    def test_class_kind(self):
        """ class_kind is present, and a string """
        self.assertIsInstance(self.node_cls.class_kind, basestring)

    def test_can_handle(self):
        """ can_handle() consistency check """
        self.assertTrue(self.node_cls.can_handle(self.store, self.key))
        self.assertFalse(self.node_cls.can_handle(self.store, "/some/random/key"))

    def test_key(self):
        """ Node.key returns a hashable object.

        We also require that the key be unchanged.
        """
        out = self.node.key
        hash(out)
        self.assertEqual(self.node.key, self.key)

    def test_store(self):
        """ Node.store returns a data store of the same class and URL. """
        self.assertIsInstance(self.node.store, self.store_cls)
        self.assertEqual(self.node.store.url, self.store.url)

    def test_display_name(self):
        """ display_name exists and is a string """
        self.assertIsInstance(self.node.display_name, basestring)


class _TestContainer(_TestNode):
    """ Class for testing compass_model.Container implementations. """

    def test_len(self):
        """ Object length is consistent with iter() result """
        self.assertGreaterEqual(len(self.node), 0)
        self.assertEqual(len(self.node), len(list(self.node)))

    def test_getitem(self):
        """ __getitem__ works properly """
        for idx in xrange(len(self.node)):
            out = self.node[idx]
            self.assertIsInstance(out, Node)

    def test_getitem_exception(self):
        """ out-of range indices raise IndexError """
        with self.assertRaises(IndexError):
            self.node[len(self.node)]
