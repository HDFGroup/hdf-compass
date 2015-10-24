How to release `[developer]`
============================

Versioning
----------

You need to install ``bumpversion``.

Once installed, you can run something like: ``bumpversion --allow-dirty --new-version 0.6.0.dev0 patch``.

The above release value must agree with the variable ``version`` present in the ``conf.py`` under the `docs` folder.


PyInstaller
-----------

For the `HDFCompass.1file.spec` file, you need to verify that the following parameters are passed to the ``EXE()`` function:

* ``console=False``: to avoid that a console window is opened at run-time for standard I/O
* ``debug=False``: to avoid that the boot-loader issues progress messages while initializing and starting the bundled app

