HDF Compass
===========

Welcome to the project!  HDF Compass is an experimental viewer program for
HDF5 and related formats, designed to complement other more complex
applications like HDFView.  Strong emphasis is placed on clean minimal design,
and maximum extensibility through a plugin system for new formats.

HDF Compass is written in Python, but ships as a native application on
Windows, OS X, and Linux, by using PyInstaller and Py2App to package the app.

Binary executables are available for Windows and Mac OS X (Yosemite or later) at
the Project Page listed below.

Bug reports and pull requests are welcome!  For non-trivial PRs please
open an issue first, so the core developers can give feedback on your idea.



Development Environment
-----------------------

You will need:

* [Python 2.7](https://www.python.org/downloads/) *(support for Python 3.4+ in progress)*
* [NumPy](https://github.com/numpy/numpy)
* [Matplotlib](https://github.com/matplotlib/matplotlib)
* [wxPython Phoenix](https://github.com/wxWidgets/Phoenix) *(2.9.5.0 or later)*
* [h5py](https://github.com/h5py/h5py) *[HDF plugin]*
* [hydroffice.bag](https://bitbucket.org/ccomjhc/hyo_bag) *[BAG plugin]*
* [Pydap](https://github.com/robertodealmeida/pydap) *[OPeNDAP plugin]*

For packaging the app:

* [PyInstaller](https://github.com/pyinstaller/pyinstaller) (Linux & Windows, experimental for OS X) *(>= 3.0)*
* [Py2App](https://bitbucket.org/ronaldoussoren/py2app) (OS X)

Running the Program  
--------------------

    $ python HDFCompass.py
      
      
Note: If you are using the Anaconda distribution on the Mac, you will see the
message: "This program needs access to the screen.  Please run with a Framework
build of python...".  In this case use the pythonw command:

    $ pythonw HDFCompass.py
           
Note: on Mac, HDF Compass doesn't create an initial window, use the system Application
menu to open a file or remote resource.
    
Packaging on OS X
-----------------

    $ python setup.py py2app
    
Packaging on Windows
--------------------

Single-file:

    $ pyinstaller --clean -y HDFCompass.1file.spec

Single-folder (useful for debugging the `pyinstaller` settings):

    $ pyinstaller --clean -y HDFCompass.1folder.spec
    
Other info
----------

* Github: [http://github.com/HDFGroup/hdf-compass](http://github.com/HDFGroup/hdf-compass)
* Project page: [https://www.hdfgroup.org/projects/compass/](https://www.hdfgroup.org/projects/compass/)
* License: BSD-like HDF Group license (See [COPYING](https://raw.githubusercontent.com/HDFGroup/hdf-compass/master/COPYING))
