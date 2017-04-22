How to release `[developer]`
============================

Versioning
----------

The following files need to be update for each new release:

- HDFCompass.1file.spec
- HDFCompass.1folder.spec
- setup.cfg
- setup.py
- spec.json
- docs/conf.py
- hdf_compass/utils/__init__.py


PyInstaller
-----------

For the `HDFCompass.1file.spec` file, you need to verify that the following parameters are passed to the ``EXE()`` function:

* ``console=False``: to avoid that a console window is opened at run-time for standard I/O
* ``debug=False``: to avoid that the boot-loader issues progress messages while initializing and starting the bundled app

