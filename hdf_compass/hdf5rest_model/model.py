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

"""
Implementation of compass_model classes for HDF5 REST API.
"""
from itertools import groupby
import sys
import os.path as op
import posixpath as pp
import json
import requests
import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from hdf_compass import compass_model
from hdf_compass.utils import url2path
from hdf_compass.hdf5rest_model import hdf5dtype


def get_json(endpoint, domain=None, uri=None):
               
    # try to do a GET from the domain
    req = endpoint
    if uri is not None:
        req += uri

    headers = {}
    if domain is not None:        
        headers['host'] = domain
    
    logger.debug("GET: " + req)
     
    rsp = requests.get(req, headers=headers, verify=False)
    logger.debug("RSP: " + str(rsp.status_code) + ':' + rsp.text)
    
    if rsp.status_code != 200:
        raise IOError(rsp.reason)  
    rsp_json = json.loads(rsp.text)
                    
    return rsp_json


def sort_key(name):
    """ Sorting key for names in an HDF5 group.

    We provide "natural" sort order; e.g. "7" comes before "12".
    """
    return [(int(''.join(g)) if k else ''.join(g)) for k, g in groupby(name, key=unicode.isdigit)]


class HDF5RestStore(compass_model.Store):
    """
    Data store implementation for an HDF Service endpoint

    Keys are valid h5paths to the object:
        e.g.:
            /g1
            /g1/dset1.1
            /g1/dtype
            
    Values are URI's to the resource
            /groups/<uuid>
            /datasets/<uuid>
            /datatypes/<uuid>
    """
    @staticmethod
    def plugin_name():
        return "HDF5 Rest"

    @staticmethod
    def plugin_description():
        return "A plugin used to access HDF Services."

    def __contains__(self, key):
        if key in self.f:
            return True
        try:
            pkey = self.get_parent(key)
        except KeyError:
            return False
        if pkey not in self.f:
            # assumes that we've loaded any parents, before querying for children
            return False
        pkey_uri = self.f[pkey]
        if not pkey_uri.startswith("/groups/"):
            # if the parent is not a group, this is not a valid key
            return False
        # do a get on the link name
        linkname = pp.basename(key)
        contains = False
        try:
            link_json = self.get(pkey_uri + "/links/" + linkname)
            if link_json["class"] == "H5L_TYPE_HARD":
                logger.debug("add key to store:" + key)
                self.f[key] = '/' + link_json["collection"] + '/' + link_json["id"]
                contains = True
            else:
                pass  # todo support soft/external links
            
        except IOError:
            # invalid link
            # todo - verify it is a 404
            logger.debug("invalid key:"+key)
        return contains
        
     

    @property
    def url(self):
        return self._url

    @property
    def display_name(self):
        if self.domain:
            return self.domain
        else:
            return self.endpoint
         
    @property
    def root(self):
        return self['/']

    @property
    def valid(self):
        return '/' in self.f
        

    @staticmethod
    def can_handle(url):
        logger.debug("hdf5rest can_handle: " + url)
        try:
            flag = True
            rsp_json = get_json(url)
            for key in ("root", "created", "hrefs", "lastModified"):
                if key not in rsp_json:
                    flag = False
                    break
            logger.debug("able to handle %s? %r" % (url, flag))
            return flag
        except Exception:
            logger.debug("able to handle %s? no" % url)
            return False
        return True
        

    def __init__(self, url):
        if not self.can_handle(url):
            raise ValueError(url)
            
        self._url = url
        # extract domain if there's a "host" query param
        queryParam = "host="
       
        nindex = url.find('?' + queryParam)
        if nindex < 0:
            nindex = url.find('&' + queryParam)
        if nindex > 0:
            domain = url[(nindex + len(queryParam) + 1):]
            # trim any additional query params
            nindex = domain.find('&')
            if nindex > 0:
                domain = domain[:nindex]
            self._domain = domain
        else:
            self._domain = None
            
        nindex = url.find('?')
        if nindex < 0:
            self._endpoint = url
        else:
            self._endpoint = url[:(nindex)]
            if self._endpoint.endswith('/'):
                # trim any trailing '/'
                self._endpoint = self._endpoint[:-1]
         
        self.cache = {} # http cache    
        rsp = self.get('/')
        
        self.f = {}
        self.f['/'] = "/groups/" + rsp['root']
        
        
    @property
    def endpoint(self):
        return self._endpoint
        
    @property
    def domain(self):
        return self._domain
        
    @property
    def objid(self):
        return self._objid
        
    def get(self, uri):
        
        if uri in self.cache:
            rsp = self.cache[uri]
        else:
            rsp = get_json(self.endpoint, domain=self.domain, uri=uri)
            self.cache[uri] = rsp
        return rsp
        
    def close(self):
        self.f = {}  # clear the key store

    def get_parent(self, key):
        # HDFCompass requires the parent of the root container be None
        if key == "" or key == "/":
            return None
            
        pkey = pp.dirname(key)
        if pkey == "":
            pkey = "/"
            
        if pkey not in self.f:
            # is it possible to get to a key without traversing the parents?
            # if so, we should query the server for the given path
            raise KeyError("parent not found: " + pkey)
        return self[pkey]


class HDF5RestGroup(compass_model.Container):
    """ Represents an HDF5 group, to be displayed in the browser view. """

    class_kind = "HDF5 Group"

    @staticmethod
    def can_handle(store, key):
        return key in store and store.f[key].startswith("/groups/")

    def get_names(self):

        # Lazily build the list of names; this helps when browsing big files
        if self._xnames is None:
            rsp = self.store.get(self._uri + "/links")
            self._xnames = []
            links = rsp["links"]
            logger.debug("got %d links for key: %s" % (len(links), self._key))
            for link in links:
                name = link["title"]
                self._xnames.append(name)
                link_key = pp.join(self.key, name)
                if link_key not in self.store.f:
                    if link["class"] == "H5L_TYPE_HARD":
                        logger.debug("add key to store:" + link_key)
                        self.store.f[link_key] = '/' + link["collection"] + '/' + link["id"]
                    else:
                        pass  # todo support soft/external links

            # Natural sort is expensive
            if len(self._xnames) < 1000:
                self._xnames.sort(key=sort_key)

        return self._xnames

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._uri = store.f[key]
        self._xnames = None
        rsp = store.get(self._uri)
        self._count = rsp["linkCount"]
        logger.debug("new group node: " + self._key)
        self.get_names()

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        name = pp.basename(self.key)
        if name == "":
            name = '/'
        return name

    @property
    def display_title(self):
        return "%s %s" % (self.store.display_name, self.key)

    @property
    def description(self):
        return 'Group "%s" (%d members)' % (self.display_name, len(self))

    def __len__(self):
        return self._count

    def __iter__(self):
        for name in self._xnames:
            yield self.store[pp.join(self.key, name)]

    def __getitem__(self, idx):
        name = self._xnames[idx]
        return self.store[pp.join(self.key, name)]


class HDF5RestDataset(compass_model.Array):
    """ Represents an HDF5 dataset. """

    class_kind = "HDF5 Dataset"

    @staticmethod
    def can_handle(store, key):
        return key in store and store.f[key].startswith("/datasets/")

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._uri = store.f[key]
        rsp = store.get(self._uri)
        shape_json = rsp["shape"]
        if shape_json["class"]  == "H5S_SCALAR":
            self._shape = ()
        elif shape_json["class"] == "H5S_SIMPLE":
            self._shape = shape_json["dims"]
        else:
            raise IOError("Unexpected shape class: " + shape_json["class"])
        type_json = rsp["type"]
        self._dtype = hdf5dtype.createDataType(type_json)
            

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        return pp.basename(self.key)

    @property
    def description(self):
        return 'Dataset "%s"' % (self.display_name,)

    @property
    def shape(self):
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    def __getitem__(self, args):
         logger.debug("getitem: " + str(args))
         req = self._uri + "/value"
         rank = len(self._shape)
         if rank > 0:
             sel_query = '['
             for dim in range(rank):
                 if dim < len(args):
                     s = args[dim]
                 else:
                     s = slice(0, self._shape[dim])
                 sel_query += str(s.start)
                 sel_query += ':'
                 if s.stop > self._shape[dim]:
                     sel_query += str(self._shape[dim])
                 else:
                    sel_query += str(s.stop)
                 sel_query += ','
             sel_query = sel_query[:-1]  # trim trailing comma
             sel_query += ']'
             req += "?select=" + sel_query
         
             
         rsp = self.store.get(req)
         value = rsp["value"]
         arr = np.array(value, dtype=self._dtype)
         return arr
               

    def is_plottable(self):
        if self.dtype.kind == 'S':
            logger.debug("Not plottable since ASCII String (characters: %d)" % self.dtype.itemsize)
            return False
        if self.dtype.kind == 'U':
            logger.debug("Not plottable since Unicode String (characters: %d)" % self.dtype.itemsize)
            return False
        return True


class HDF5RestKV(compass_model.KeyValue):
    """ A KeyValue node used for HDF5 attributes. """

    class_kind = "HDF5 Attributes"

    @staticmethod
    def can_handle(store, key):
        canhandle = False
        if key in store:
            uri = store.f[key]
            if uri.startswith("/groups/"):
                canhandle = True
            elif uri.startswith("/datasets/"):
                canhandle = True
            elif uri.startswith("/datatypes/"):
                canhandle = True
        return canhandle

    def __init__(self, store, key):
        self._store = store
        self._key = key
        self._uri = store.f[key]
        
        rsp = store.get(self._uri + "/attributes")
        attributes = rsp["attributes"]
        names = []
        for attr in attributes:
            names.append(attr["name"])
        self._names = names

    @property
    def key(self):
        return self._key

    @property
    def store(self):
        return self._store

    @property
    def display_name(self):
        n = pp.basename(self.key)
        return n if n != '' else '/'

    @property
    def description(self):
        return self.display_name

    @property
    def keys(self):
        return self._names[:]

    def __getitem__(self, name):
        rsp = self._store.get(self._uri + "/attributes/" + name)
        type_json = rsp["type"]
        value_json = rsp["value"]
        arr_dtype = hdf5dtype.createDataType(type_json)
        arr = np.array(value_json, dtype=arr_dtype)
        return arr

# Register handlers    
HDF5RestStore.push(HDF5RestKV)
HDF5RestStore.push(HDF5RestDataset)
#HDF5RestStore.push(HDF5Text)
HDF5RestStore.push(HDF5RestGroup)
#HDF5RestStore.push(HDF5Image)

compass_model.push(HDF5RestStore)
