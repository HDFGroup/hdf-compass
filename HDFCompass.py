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
import logging
from hdf_compass import compass_viewer

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-7s %(name)s.%(funcName)s:%(lineno)d > %(message)s'
)
logging.getLogger("hdf_compass").setLevel(logging.DEBUG)  # INFO to minimize verbosity, DEBUG for higher verbosity

compass_viewer.run()
