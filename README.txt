This is the source code repository for HDF Compass, a viewer program for
HDF and HDF-related files.

The project is divided into components, each of which is a top-level Python
package:

compass_viewer
    The GUI viewer application, based on wxPython.  The file HDFCompass.py
    is a two-line script that launches the viewer, and is provided as the
    entry point for Py2App and PyInstaller.
    
compass_model
    Defines the classes available for the pluggable data model.  This is the
    main dependency for plugins.  The interfaces defined in compass_model are
    implemented by plugins, and those implementations are called by the viwer
    to populate the various views in HDFCompass (container, array, etc.).
    
hdf5_model
    A basic HDF5 plugin, using h5py.
    
filesystem_model
    An example filesystem plugin.  Access through the GUI by opening the
    resource "file://localhost".
    
array_model
    An example/debugging array plugin.  Access through the GUI by opening the
    resource "array://localhost".