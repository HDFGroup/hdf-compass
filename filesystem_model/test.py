from compass_model.test import container, store
from . import Filesystem, Directory, File

url = "file://localhost"

s = store(Filesystem, url)
c = container(Filesystem, url, Directory, "/")

