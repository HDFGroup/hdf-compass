##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of the HDF Compass Viewer. The full HDF Compass          #
# copyright notice, including terms governing use, modification, and         #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################

# Builds a single-file EXE for distribution.
# Note that an "unbundled" distribution launches much more quickly, but
# requires an installer program to distribute.
#
# To compile, execute the following within the source directory:
#
# pyinstaller --clean -y HDFCompass.1folder.spec
#
# The resulting .exe file is placed in the dist/HDFCompass folder.

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE, TOC
from PyInstaller import is_darwin
import os


def collect_pkg_data(package, include_py_files=False, subdir=None):
    """ helper function to collect data based on the passed package """
    from PyInstaller.utils.hooks import get_package_paths, remove_prefix, PY_IGNORE_EXTENSIONS

    # Accept only strings as packages.
    if type(package) is not str:
        raise ValueError

    pkg_base, pkg_dir = get_package_paths(package)
    if subdir:
        pkg_dir = os.path.join(pkg_dir, subdir)
    # Walk through all file in the given package, looking for data files.
    data_toc = TOC()
    for dir_path, dir_names, files in os.walk(pkg_dir):
        for f in files:
            extension = os.path.splitext(f)[1]
            if include_py_files or (extension not in PY_IGNORE_EXTENSIONS):
                source_file = os.path.join(dir_path, f)
                dest_folder = remove_prefix(dir_path, os.path.dirname(pkg_base) + os.sep)
                dest_file = os.path.join(dest_folder, f)
                data_toc.append((dest_file, source_file, 'DATA'))

    return data_toc

pkg_data_hdf_compass = collect_pkg_data('hdf_compass')
cartopy_aux = []
try:  # for GeoArray we use cartopy that can be challenging to freeze on OSX to dependencies (i.e. geos)
    import cartopy.crs as ccrs
    cartopy_aux = collect_pkg_data('cartopy')
except (ImportError, OSError):
    pass

if is_darwin:
    icon_file = os.path.abspath('HDFCompass.icns')
else:
    icon_file = os.path.abspath('HDFCompass.ico')
if not os.path.exists(icon_file):
    raise RuntimeError("invalid path to icon: %s" % icon_file)

a = Analysis(['HDFCompass.py'],
             pathex=[],
             hiddenimports=['scipy.linalg.cython_blas', 'scipy.linalg.cython_lapack'],  # for cartopy
             excludes=["PySide"],  # exclude libraries from being bundled (in case that are installed)
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='HDFCompass',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=icon_file)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               pkg_data_hdf_compass,
               cartopy_aux,
               strip=None,
               upx=True,
               name='HDFCompass')
if is_darwin:
    app = BUNDLE(coll,
                 name='HDFCompass.app',
                 icon=icon_file,
                 bundle_identifier=None)
