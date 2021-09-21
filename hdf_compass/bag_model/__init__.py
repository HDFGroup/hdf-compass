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
#                                                                            #
# author: gmasetti@ccom.unh.edu                                              #
##############################################################################

__version__ = "0.1.6"

from hdf_compass.bag_model.model import BAGStore, BAGDataset, BAGGroup, BAGImage, BAGKV

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
