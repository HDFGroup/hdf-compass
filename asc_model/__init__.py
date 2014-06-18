import os
import os.path as op
import numpy as np

import compass_model

'''
That sounds like a great place to start.  Here are some more explicit
requirements for your "pilot" plugin:

1. The user should be able to browse the filesystem (you can borrow
code from the "filesystem" plugin for this).  You'll need to implement
two classes: a subclass of Container (to handle directories), and a
subclass of Array (to handle the csv files).

2. The user should be able to load array data from files with the
".csv" extension (hint: use out the canhandle() static method so your
class is only associated with ".csv" files).

3. Values in the text file must be read in and displayed with the
array control.  You can assume comma-delimited data with
newline-separated rows; for example, this 2 x 3 array:

1,2,3
4,5,6

You should implement the plugin as a new top-level package, let's call
it "csv_model", similar in structure to "hdf5_model" and
"filesystem_model".  Some hints on testing:

1. in analogy to the filesystem and array plugins (file://localhost
and array://localhost), you can have your Store subclass respond to
"csv://localhost" URLS.
2. To make the viewer aware of your plugin (so the "csv://localhost"
URL can actually be opened), add "import csv_model" to the import
statements in the run() function of compass_viewer/__init__.py.

Also may be useful for the actual reading:

http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html

Give it a shot and let me know if you run into problems.
'''

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
		return "Local File System"

	@property
	def root(self):
		return self['/']

	@property
	def valid(self):
		return self._valid

	@staticmethod
	def canhandle(url):
		if url == "asc://localhost":
			return True
		return False

	def __init__(self, url):
		if not self.canhandle(url):
			raise ValueError(url)
		self._url = url
		self._value = True

	def close(self):
		self._valid = False

	def getparent(self, key):
		if key == '/':
			return None
		return self[op.dirname(key)]

class Directory(compass_model.Container):

	"""
		Represents a directory in the file system.
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
		except OSError: 
			self._names = []

	@property
	def key(self):
		return self._key

	@property
	def store(self):
		return self._store

	@property
	def description(self):
		return 'folder "%s" (%d members)' % (self.displayname, len(self))

	def __len__(self):
		return len(self._names)

	def __iter__(self):
		for name in self._names:
			key = op.join(self.key, name)
			yield self._store[key]