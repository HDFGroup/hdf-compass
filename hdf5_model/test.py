from compass_model.test import container, store
from . import HDF5Group, HDF5Store

url = "file:///Users/andrew/Documents/Compass/Demo files/2_5.hdf5"

s = store(HDF5Store, url)
c = container(HDF5Store, url, HDF5Group, "/")

