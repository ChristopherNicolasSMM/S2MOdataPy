"""
Pacote de anotações de UI para modelos OData.

Author: Christopher N. S. M. Mauricio
"""

from .decorators import UI, Common, Validation
from .metadata_builder import build_metadata_dict, build_metadata_xml

__all__ = [
    "UI",
    "Common",
    "Validation",
    "build_metadata_xml",
    "build_metadata_dict",
]
