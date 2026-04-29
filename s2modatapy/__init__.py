"""
S2MOdataPy - OData V4 Client Library

Author: Christopher N. S. M. Mauricio
License: MIT with Attribution
"""

__version__ = "0.1.0"
__author__ = "Christopher N. S. M. Mauricio"
__license__ = "MIT with Attribution"

from .client import S2MClient
from .exceptions import S2MODataError, S2MODataConnectionError

__all__ = [
    "S2MClient",
    "S2MODataError",
    "S2MODataConnectionError",
]