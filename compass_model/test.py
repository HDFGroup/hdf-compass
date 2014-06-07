
"""
Provides support for testing basic properties of data model implementations.

Checks to make sure all required properties and methods are implemented, and
does basic sanity/consistency checking.  More specific tests must be written
by plugin authors.

The public interface consists of the following functions, each of which
provides a TestCase sublass which may be used with unittest:

- store
- container
- array
- keyvalue
- image

Example, in my_model.test:

    from compass_model.test import store, container
    from my_model import MyStore, MyContainer

    URL = "file:///path/to/myfile.ext"

    store_tests = store(MyStore, URL)
    container_tests = container(MyStore, URL, MyContainer, "some-key")

To run unittest, which discovers classes "store_tests" and "container_tests":

    $ python -m unittest my_model.test

"""

from . import Node, Store
import unittest as ut


# --- Public API --------------------------------------------------------------

def store(storecls_, url_):
    """ Construct a TestCase appropriate for a Store subclass.

    storecls:   Your compass_model.Store implementation.
    url:        A URL representing a valid datastore to test against.
    """
    class TestStore(_TestStore):
        storecls = storecls_
        url = url_
    return TestStore


def container(storecls_, url_, nodecls_, key_):
    """ Construct a TestCase class appropriate for a Container subclass.

    storecls:   Your compass_model.Store implementation.
    url:        A URL representing a valid datastore to test against.
    nodecls:    Your compass_model.Container implementation.
    key:        A valid key which points to a container.
    """
    class TestContainer(_TestContainer):
        storecls = storecls_
        url = url_
        nodecls = nodecls_
        key = key_
    return TestContainer

# --- End public API ----------------------------------------------------------


class _TestStore(ut.TestCase):

    """
    Base class for testing Stores.
    """

    storecls = None
    url = None


    def setUp(self):
        self.store = self.storecls(self.url)


    def tearDown(self):
        if self.store.valid:
            self.store.close()


    def test_class(self):
        """ Verify the thing we get from storecls is actually a Store """
        self.assertIsInstance(self.store, Store)


    def test_url(self):
        """ Verify store.url produces a string """
        self.assertIsInstance(self.store.url, basestring)


    def test_displayname(self):
        """ Verify store.displayname produces a string. """
        self.assertIsInstance(self.store.displayname, basestring)


    def test_root(self):
        """ Verify store.root exists and has no parent """
        self.assertIsInstance(self.store.root, Node)
        self.assertIs(self.store.getparent(self.store.root.key), None)


    def test_close_valid(self):
        """ Verify that store.close() works and is reflected by store.valid """
        self.assertTrue(self.store.valid)
        self.store.close()
        self.assertFalse(self.store.valid)


    def test_canhandle(self):
        """ Verify canhandle() works properly """
        self.assertTrue(self.storecls.canhandle(self.url))
        self.assertFalse(self.storecls.canhandle("file:///no/such/path"))


    def test_handlers(self):
        """ The implementation has at least one Node handler registered """
        h = self.store.gethandlers()
        # Test for N > 1 because compass_model.Unknown is always present
        self.assertGreater(len(h), 1) 


class _TestNode(ut.TestCase):

    """
    Base class for testing Node objects.
    """

    storecls = None
    nodecls = None
    url = None
    key = None


    def setUp(self):
        self.store = self.storecls(self.url)
        self.node = self.nodecls(self.store, self.key)


    def tearDown(self):
        if self.store.valid:
            self.store.close()


    def test_contains(self):
        """ Consistency check for store __contains___ """
        self.assertTrue(self.key in self.store)
        self.assertFalse("keynotinstore" in self.store)


    def test_icons(self):
        """ Icon dict is present and contains valid items:

        keys: int
        values: callables returning PNG data

        Required sizes: 16x16 and 64x64
        """
        for key, val in self.nodecls.icons.iteritems():
            self.assertIsInstance(key, int)
            data = val()
            self.assertIsInstance(data, bytes)
            self.assertEqual(data[0:8], b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")
        
        # required resolutions
        self.assertIn(16, self.nodecls.icons)
        self.assertIn(64, self.nodecls.icons)


    def test_classkind(self):
        """ classkind is present, and a string """
        self.assertIsInstance(self.nodecls.classkind, basestring)


    def test_canhandle(self):
        """ canhandle() consistency check """
        self.assertTrue(self.nodecls.canhandle(self.store, self.key))
        self.assertFalse(self.nodecls.canhandle(self.store, "/some/random/key"))


    def test_key(self):
        """ Node.key returns a hashable object.

        We also require that the key be unchanged.
        """
        out = self.node.key
        hash(out)
        self.assertEqual(self.node.key, self.key)


    def test_store(self):
        """ Node.store returns a data store of the same class and URL. """
        self.assertIsInstance(self.node.store, self.storecls)
        self.assertEqual(self.node.store.url, self.store.url)


    def test_displayname(self):
        """ displayname exists and is a string """
        self.assertIsInstance(self.node.displayname, basestring)


class _TestContainer(_TestNode):

    """
    Class for testing compass_model.Container implementations.
    """

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
