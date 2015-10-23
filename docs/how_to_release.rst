How to release `[developer]`
============================

Versioning
----------

You need to manually modify the ``__version__`` variable in the `__init__.py` file present in ``hdf_compass.utils`` package.

The above version value must agree with the variables ``version`` and ``release`` present in the ``conf.py`` under the `docs` folder.


PyInstaller
-----------

For the `HDFCompass.1file.spec` file, you need to verify that the following parameters are passed to the ``EXE()`` function:

* ``console=False``: to avoid that a console window is opened at run-time for standard I/O
* ``debug=False``: to avoid that the boot-loader issues progress messages while initializing and starting the bundled app

