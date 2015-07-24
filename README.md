HDF Compass
===========

Welcome to the project!  HDF Compass is an experimental viewer program for
HDF5 and related formats, designed to complement other more complex
applications like HDFView.  Strong emphasis is placed on clean minimal design,
and maximum extensibility through a plugin system for new formats.

HDF Compass is written in Python, but ships as a native application on
Windows, OS X, and Linux, by using PyInstaller and Py2App to package the app.

Bug reports and pull requests are welcome!  For non-trivial PRs please
open an issue first, so the core developers can give feedback on your idea.

Development Environment
-----------------------

You will need:

* Python 2.7
* NumPy
* Matplotlib
* wxPython Phoenix (2.9.5.0 or later)
* h5py

For packaging the app:

* Py2App (OS X)
* PyInstaller (Linux & Windows)

Running the Program
-------------------

    $ python HDFCompass.py
    
Packaging on OS X
-----------------

    $ python setup.py py2app
    
Packaging on Windows
--------------------

    $ pyinstaller HDFCompass.spec
    
Other info
----------

* Github: http://github.com/HDFGroup/hdf-compass
* Project page: https://www.hdfgroup.org/projects/compass/
* License: BSD-like HDF Group license (See COPYING)
