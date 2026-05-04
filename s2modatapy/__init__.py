"""
S2MOdataPy - Biblioteca Python para cliente OData V4

Fornece interface fluente para consulta e escrita em serviços OData V4,
com suporte a leitura de metadados enriquecidos com anotações de UI.

Author: Christopher N. S. M. Mauricio
License: MIT with Attribution
"""

__version__ = "0.2.0"
__author__ = "Christopher N. S. M. Mauricio"
__license__ = "MIT with Attribution"

from .client import S2MClient
from .exceptions import (
    S2MODataAuthenticationError,
    S2MODataConnectionError,
    S2MODataError,
    S2MODataNotFoundError,
    S2MODataValidationError,
)
from .parsers.annotations import (
    FieldType,
    ODataAnnotationParser,
    UIAnnotations,
    UIField,
    UIFieldGroup,
    UIForm,
    UIListView,
)

__all__ = [
    # Cliente principal
    "S2MClient",
    # Exceções
    "S2MODataError",
    "S2MODataConnectionError",
    "S2MODataNotFoundError",
    "S2MODataValidationError",
    "S2MODataAuthenticationError",
    # Parser de metadados / anotações
    "ODataAnnotationParser",
    "UIAnnotations",
    "UIListView",
    "UIFieldGroup",
    "UIField",
    "UIForm",
    "FieldType",
]
