"""
Módulo de parsers de metadados OData para S2MOdataPy

Author: Christopher N. S. M. Mauricio
"""

from .annotations import (
    ODataAnnotationParser,
    UIAnnotations,
    UIListView,
    UIFieldGroup,
    UIField,
    UIForm,
    FieldType,
)

__all__ = [
    "ODataAnnotationParser",
    "UIAnnotations",
    "UIListView",
    "UIFieldGroup",
    "UIField",
    "UIForm",
    "FieldType",
]
