from hdf_compass.compass_model.test import container, store
from hdf_compass.opendap_model import Server, Dataset

url = "http://test.opendap.org/opendap/hyrax/data/hdf5/grid_1_2d.h5"
s_1 = store(Server, url)

url = "http://test.opendap.org/opendap/hyrax/data/nc/bears.nc"
s_2 = store(Server, url)