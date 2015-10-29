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
from __future__ import absolute_import, division, print_function

from hdf_compass.compass_model.test import container, store
from hdf_compass.hdf5rest_model import HDF5RestGroup, HDF5RestStore
from hdf_compass.utils import data_url

import os

url = "http://127.0.0.1:5000"

s = store(HDF5RestStore, url)
c = container(HDF5RestStore, url, HDF5RestGroup, "/")

