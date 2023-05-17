HDF Compass
===========

.. image:: https://badge.fury.io/py/hdf_compass.svg
    :target: https://badge.fury.io/py/hdf_compass
    :alt: PyPI Status

.. image:: https://readthedocs.org/projects/hdf-compass/badge/?version=stable
    :target: http://hdf-compass.readthedocs.org/en/stable/?badge=stable
    :alt: Stable Documentation Status
    
.. image:: https://readthedocs.org/projects/hdf-compass/badge/?version=latest
    :target: http://hdf-compass.readthedocs.org/en/latest/?badge=latest
    :alt: Latest Documentation Status
    
.. image:: https://ci.appveyor.com/api/projects/status/tfg350xo8t7h70ix?svg=true
    :target: https://ci.appveyor.com/project/giumas/hdf-compass
    :alt: AppVeyor Status

        
Welcome to the project!  HDF Compass is an experimental viewer program for
HDF5 and related formats, designed to complement other more complex
applications like HDFView.  Strong emphasis is placed on clean minimal design,
and maximum extensibility through a plugin system for new formats.

HDF Compass is written in Python, but ships as a native application on
Windows, OS X, and Linux, by using PyInstaller to package the app.

Binary executables are available for Windows (Windows 7 or later) and Mac OS X (Yosemite or later) at
the Project Page listed below.

Bug reports and pull requests are welcome!  For non-trivial PRs please
open an issue first, so the core developers can give feedback on your idea.



Development Environment
-----------------------

You will need:

* `Python 2.7 <https://www.python.org/downloads/>`_ *(support for Python 3.4+ in progress)*
* `NumPy <https://github.com/numpy/numpy>`_
* `Matplotlib <https://github.com/matplotlib/matplotlib>`_
* `wxPython Phoenix 3.0.2 <https://github.com/wxWidgets/Phoenix>`_ *(later releases have not been tested)*
* `Cartopy <https://github.com/SciTools/cartopy>`_
* `h5py <https://github.com/h5py/h5py>`_ *[HDF plugin]*
* `hydroffice.bag <https://bitbucket.org/ccomjhc/hyo_bag>`_ *[BAG plugin]*
* `Pydap <https://github.com/robertodealmeida/pydap>`_ *[OPeNDAP plugin]* (<3.2)
* `Requests <https://github.com/kennethreitz/requests>`_ *[HDF Rest API plugin]*
* `adios <https://github.com/ornladios/ADIOS>`_ *[ADIOS Plugin]* (Linux/OSX only)

For packaging the app:

* `PyInstaller <https://github.com/pyinstaller/pyinstaller>`_ *(>= 3.0)*


Running the Program  
-------------------

    ``$ python HDFCompass.py``
      
      
Note: If you are using the Anaconda distribution on the Mac, you will see the
message: "This program needs access to the screen.  Please run with a Framework
build of python...".  In this case use the pythonw command:

    ``$ pythonw HDFCompass.py``
           
Note: on Mac, HDF Compass doesn't create an initial window, use the system Application
menu to open a file or remote resource.


Packaging
---------

Single-file:

    ``$ pyinstaller --clean -y HDFCompass.1file.spec``

Single-folder (useful for debugging the ``pyinstaller`` settings):

    ``$ pyinstaller --clean -y HDFCompass.1folder.spec``


Other info
----------

* Github: `http://github.com/HDFGroup/hdf-compass <http://github.com/HDFGroup/hdf-compass>`_
* Project page: `https://www.hdfgroup.org/projects/compass/ <https://www.hdfgroup.org/projects/compass/>`_
* License: BSD-like HDF Group license (See `COPYING <https://raw.githubusercontent.com/HDFGroup/hdf-compass/master/COPYING>`_)
