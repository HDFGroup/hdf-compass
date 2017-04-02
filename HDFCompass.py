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


class LoggingFilter(logging.Filter):
    """ An example of logging filter that disables the logging from a specific module """
    def filter(self, record):
        # print(record.name)
        if record.name.startswith('hdf_compass.compass_viewer.info'):
            return False
        return True


# logging settings
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to minimize verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-7s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
# ch.addFilter(LoggingFilter())  # uncomment to activate the logging filter
logger.addHandler(ch)

from hdf_compass import compass_viewer

compass_viewer.run()
