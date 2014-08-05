"""
HDF Compass plugin for accessing an OpENDAP server. 
"""
import numpy as np
import pydap as dap

import compass_model

class Server(compass_model.Store):

	"""
		Represents the remote OpENDAP derver to be accessed
	"""

	# Methods related to the plugin system
	def __getitem__(self, key):
        # Open an object in the store, using the last registered class which reports it can open the key.
		pass

	def gethandlers(self, key=None):
        # Retrieve all registered Node subclasses, optionally filtering by those which report they can handle "key"
		pass

	def __contains__(self, key):
        # True if "key" exists in the store. False otherwise.
		pass

	# Other methods & properties
	@staticmethod
	def canhandle(url):
        # Return True if this class can make sense of "url". False otherwise.
		pass

	def __init__(self, url):
        #Create a new store instance from the data at "url". False otherwise.
		pass

	def close(self):
        # Discontinue access to the data store
        self._valid = False
		#pass

	def getparent(self, key):
        # Return the object which contains "key", or None if no object exists
		pass

	@property
	def url(self):
        # The "URL" used to open the store
        return self._url
		#pass

	@property
	def displayname(self):
        # A short name used for the store
		pass

	@property
	def root(self):
        # A node instance representing the starting point in the file
        # For hierarchiacal formats, this would be the root container.
		pass

	@property
	def valid(self):
        return self._valid
		#pass

class Structure(compass_model.Container):

	"""
		Represents Structure/StructureType Object in OpENDAP/Pydap
	"""

	# Unique to the Container class
	@property
	def __len__(self):
        # Get the number of ojects directly attached to the Container
		pass

	def __getitem__(self, index):
        # Retrieve the node at index.
        # Returns a NODE INSTANCE, not a key
		pass

    def __iter__(self):
        pass

	# General Node class implementations

	classkind = "Structure"

	@staticmethod
	def canhandle(store, key):
        # Determine whether this class can usefully represent the object.
        # Keys are not technically required to be strings
		pass

	def __init__(self, store, key):
        # Create a new instance representing the object pointed to by "key" in "store"
		pass

	@property
	def key(self):
        # Unique key which identifies this object in the store
        # Keys may be any hashable object, although strings are the most common
		pass

	@property
	def store(self):
        # The data store to which the object belongs
		pass

	@property
	def displayname(self):
        # A short name for display purposes 
		pass

	@property
	def description(self):
        # Descriptive string
		pass

class Array(compass_model.Array):

	"""
		Represents Array/BaseType Object in OpENDAP/Pydap
	"""

	# Implementations unique to Array class

	@property
	def shape(self):
        # Shape of the array, as a Python tuple
        return self.shape
		#pass

	@property
	def dtype(self):
        # NumPy data type object representing the type of the array
		return self.type
        #pass

	def __getitem__(self, indices):
        # Retrieve data from the array, using the standard array-slicing syntax.
        # "indices" are slicing arguments
		pass

    # General Node class implementations

    classkind = "Array"

    @staticmethod
    def canhandle(store, key):
        # Determine whether this class can usefully represent the object
        # Keys are not technically required to be strings.
        pass

    def __init__(self, store, key):
        # Create a new instance representing the object pointed to by "key" in "store"
        pass

    @property
    def key(self):
        # Unique key which identifies this object in the store.
        # Keys may be any hashable object
        self._key
        #pass

    @property
    def store(self):
        # The data store to which the object belongs
        return self._store
        #pass

    @property
    def displayname(self):
        #  A short name for display purposes
        return self.name
        #pass

    @property
    def description(self):
        # A descriptive string
        return self.id
        #pass

class Grid(compass_model.Array):

    """
        Represents Grid/GridType Object in OpENDAP/Pydap
    """

    # Implementations unique to Array class

    @property
    def shape(self):
        # Shape of the array, as a Python tuple
        return self.shape
        #pass

    @property
    def dtype(self):
        # NumPy data type object representing the type of the array
        return self.type
        #pass

    def __getitem__(self, indices):
        # Retrieve data from the array, using the standard array-slicing syntax
        # "Indices" are slicing arguments
        pass

    # General Node class implementations

    classkind = "Grid"

    @staticmethod
    def canhandle(store, key):
        # Determine whether this class can usefully represent the object
        pass

    def __init__(self, store, key):
        # Create a new instance representing the object pointed to by "key" in "store"
        pass

    @property
    def key(self):
        # Unique key which identifies this object in the store
        # Keys may be any hashable object, although strings are the most common
        pass

    @property
    def store(self):
        # The data store to which the object belongs
        pass

    @property
    def displayname(self):
        # A short name for display purposes
        pass

    @property
    def description(self):
        # Descriptive string
        pass

