from __future__ import absolute_import, division, print_function

from hdf_compass.compass_model.test import container, store
from hdf_compass.hdf5_model import HDF5Group, HDF5Store
from hdf_compass.utils import is_win

import os
import sys

import hdf_compass

# locate test file
data_folder = os.path.abspath(os.path.join(os.path.dirname(hdf_compass.__file__), 'data'))
test_file = os.path.join(data_folder, 'hdf5', 'tall.h5')
if not os.path.exists(test_file):
    raise RuntimeError("Unable to locate test file: %s" % test_file)

# create url
if is_win:
    url = 'file:///' + os.path.abspath(test_file)
else:
    url = 'file://' + os.path.abspath(test_file)

s = store(HDF5Store, url)
c = container(HDF5Store, url, HDF5Group, "/")

