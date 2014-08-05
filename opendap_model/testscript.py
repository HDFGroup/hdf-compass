from pydap.model import *
from pydap.client import open_url
from pydap.proxy import ArrayProxy
# url - http://test.opendap.org/dap/data/nc/coads_climatology.nc



a = BaseType(name='a', data=1, shape=(), dimensions=(), type=Int32, attributes={'long_name':'variable a'})
a.history = 'Created by me'
a.attributes['history'] = 'Created by me'

b = a 

c = BaseType(name='long & complicated')

s = StructureType(name='s')
s['a'] = a
s[c.name] = c

dataset = DatasetType(name='example')
dataset['s'] = s

print 'a, b, c, s, dataset are variables'

if type(dataset) == DatasetType:
	print "heck yea"
	
test_dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')