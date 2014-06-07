# This file is part of HDFCompass, a viewer for HDF5 and other formats.
#
# Copyright 2013-2014 Heliosphere Research LLC
# All rights reserved.
#
# This software product comes with ABSOLUTELY NO WARRANTY.

# Builds a single-file EXE for distribution.
# Note that an "unbundled" distribution launches much more quickly, but
# requires an installer program to distribute.
#
# To compile, execute the following within the source directory:
#
# python /path/to/pyinstaller.py HDFCompass.spec
#
# The resulting .exe file is placed in the dist/ folder.

a = Analysis(['HDFCompass.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
             
# The following block is necessary to prevent a hard crash when launching
# the resulting .exe file
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
        
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='HDFCompass.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False , icon='compass.ico')
