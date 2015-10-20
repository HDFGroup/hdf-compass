from __future__ import absolute_import, division, print_function

from hdf_compass.compass_model.test import container, store
from hdf_compass.array_model import ArrayStore, ArrayContainer
from hdf_compass.utils import is_win

url = "array://localhost"

s = store(ArrayStore, url)
c = container(ArrayStore, url, ArrayContainer, None)