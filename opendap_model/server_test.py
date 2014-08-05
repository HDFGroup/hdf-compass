from pydap.client import open_url
from pydap.model import *
from pydap.proxy import ArrayProxy

dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')

print dataset.values()
