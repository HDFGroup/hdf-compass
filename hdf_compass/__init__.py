"""
HDFCompass Namespace
"""
from __future__ import absolute_import, division, print_function
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
