from __future__ import absolute_import, division, print_function

from hdf_compass.compass_model.test import container, store
from hdf_compass.filesystem_model import Filesystem, Directory

url = "file://localhost"

s = store(Filesystem, url)
c = container(Filesystem, url, Directory, "/")
