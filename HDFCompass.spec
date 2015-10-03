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
          console=False, icon='compass.ico')
