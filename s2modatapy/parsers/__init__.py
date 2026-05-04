"""
Módulo de parsers de metadados OData para S2MOdataPy

Author: Christopher N. S. M. Mauricio
"""

from .annotations import (
    FieldType,
    ODataAnnotationParser,
    UIAnnotations,
    UIField,
    UIFieldGroup,
    UIForm,
    UIListView,
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
