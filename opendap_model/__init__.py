"""
HDF Compass plugin for accessing an OpENDAP server. 
"""
import numpy as np
from pydap.client import open_url
import pydap as dap
from pydap.model import *

import compass_model

class Server(compass_model.Store):

    """
        Represents the remote OpENDAP derver to be accessed
    """
    # For practice I will implement using the OpENDAP Test Server, found at:
    # http://test.opendap.org/dap/data/nc/coads_climatology.nc

    # Methods related to the plugin system
    '''
    def __getitem__(self, key):
        # Open an object in the store, using the last registered class which reports it can open the key.
        print 1
        #return open_url(self._url)
        #return self._dset
        pass
    '''
    '''
    def gethandlers(self, key=None):
        # Retrieve all registered Node subclasses, optionally filtering by those which report they can handle "key"
        print 2
        pass
    '''

    def __contains__(self, key):
        # True if "key" exists in the store. False otherwise.
        print 3
        #return key in self._dset.keys()
        if key == '/':
            return True
        return False
        #pass

    # Other methods & properties
    @staticmethod
    def canhandle(url):
        print 'canhandle'
        if not url.startswith('http://'):
            return False
        #if not url.endswith('.nc'):
        #    return False
        return True
        # Return True if this class can make sense of "url". False otherwise.
        #pass

    def __init__(self, url):
        #Create a new store instance from the data at "url". False otherwise.
        print 4
        if not self.canhandle(url):
            raise ValueError(url)
        self._url = url
        self._valid = True
        self._dataset = open_url(self._url)

    def close(self):
        # Discontinue access to the data store
        self._valid = False
        print 5
        #pass

    def getparent(self, key):
        # Return the object which contains "key", or None if no object exists
        print 6
        return None
        #pass

    @property
    def url(self):
        # The "URL" used to open the store
        print 7
        return self._url
        #pass

    @property
    def displayname(self):
        # A short name used for the store
        print 8
        return "OpENDAP Test Dataset"
        #pass

    @property
    def root(self):
        # A node instance representing the starting point in the file
        # For hierarchiacal formats, this would be the root container.
        print 9
        return self['/']
        #pass

    @property
    def valid(self):
        print 10
        return self._valid
        #pass


class Structure(compass_model.Container):

    """
        Represents Structure/StructureType Object in OpENDAP/Pydap
    """

    classkind = "Structure"

    # Unique to the Container class
    
    def __len__(self):
        # Get the number of ojects directly attached to the Container
        print 11
        #print "the length is ", len(self._dset.data)
        return len(self._dset.data)
        #pass
    

    def __getitem__(self, index):
        # Retrieve the node at index.
        # Returns a NODE INSTANCE, not a key
        item = self._dset.get(self._dset.keys()[index])
        print 12
        return item
        #return self._dset.get(self._dset.keys()[index])
        #return open_url(self._url)
        #pass

    def __iter__(self):
        print 13
        for name in self._names:
            yield self.store[pp.join(self.key, name)]
        #pass

    # General Node class implementations

    @staticmethod
    def canhandle(store, key):
        # Determine whether this class can usefully represent the object.
        # Keys are not technically required to be strings
        print 14
        print "key is", key, " store is ", store
        return key in store
        if type(store._dataset) == DatasetType or type(store._dataset) == StructureType:
        #if type(self._dest) == DatasetType or type(self._dset) == StructureType:
            return True
        return False

    def __init__(self, store, key):
        # Create a new instance representing the object pointed to by "key" in "store"
        print 15
        self._store = store
        self._key = key 
        self._url = store.url
        self._dset = open_url(self._url)

        print "self._dset.name is ", self._dset.name
        #pass

    @property
    def key(self):
        # Unique key which identifies this object in the store
        # Keys may be any hashable object, although strings are the most common
        print 16
        print "self._key is ", self._key
        return self._key
        #pass

    @property
    def store(self):
        # The data store to which the object belongs
        print 17
        print "self._store is ", self._store
        return self._store
        #pass

    @property
    def displayname(self):
        # A short name for display purposes 
        print 18
        return "test"
        #return self._dset.name
        #pass

    @property
    def description(self):
        # Descriptive string
        print 19
        return "Testing Structure Implementation"
        #pass


class BaseType(compass_model.Array):

    """
    Represents Array/BaseType Object in OpENDAP/Pydap
    """

    classkind = "Base"

    # Imports only used within this class
    from pydap.proxy import ArrayProxy

    # Implementations unique to Array class

    @property
    def shape(self):
        # Shape of the array, as a Python tuple
        print 20
        return self._dset.shape
        #pass

    @property
    def dtype(self):
        # NumPy data type object representing the type of the array
        print 21
        return self._dset.dtype
        #pass

    def __getitem__(self, indices):
        # Retrieve data from the array, using the standard array-slicing syntax.
        # "indices" are slicing arguments
        print 22
        return self._dset[indices]
        #pass

    # General Node class implementations

    @staticmethod
    def canhandle(store, key):
        # Determine whether this class can usefully represent the object
        # Keys are not technically required to be strings.

        # If the type of the key stored in store is not 'pydap.model.BaseType' then false
        #return key in store and type(key)
        print 23
        if type(store._dataset) == BaseType:
            return True
        return False
        #pass

    def __init__(self, store, key):
        # Create a new instance representing the object pointed to by "key" in "store"
        print 24
        self._store = store
        self._key = key
        self._id = self.id
        self._url = store.url
        self._shape = self.shape
        self._dset = ArrayProxy(self._id, self._url, self._shape)#[:]
        #pass

    @property
    def key(self):
        # Unique key which identifies this object in the store.
        # Keys may be any hashable object
        print 25
        return self._key
        #pass

    @property
    def store(self):
        # The data store to which the object belongs
        print 26
        return self._store
        #pass

    @property
    def displayname(self):
        #  A short name for display purposes
        print 27
        return "test"
        #return self._dset.name
        #pass

    @property
    def description(self):
        # A descriptive string
        print 28
        return "A Descriptive String"
        #pass

    @property
    def id(self):
        print 29
        return self._id
        #pass


# Register Handlers
Server.push(Structure)
Server.push(BaseType)

compass_model.push(Server)