"""
Construtor de metadados OData V4 com anotações de UI.

Gera dois formatos de saída:
- XML padrão OData V4 (endpoint /$metadata)
- JSON enriquecido customizado (endpoint /$metadata.json)

O formato JSON é o preferido para consumo pelo cliente S2MOdataPy,
pois inclui informações de validação e configuração de UI de forma
mais direta.

Author: Christopher N. S. M. Mauricio
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from sqlalchemy.inspection import inspect
from sqlalchemy import String, Integer, Float, Boolean


# ─────────────────────────────────────────────────────────────────────────────
# Mapeamento de tipos
# ─────────────────────────────────────────────────────────────────────────────

def _map_sql_type_to_edm(sql_type) -> str:
    """Converte tipo SQLAlchemy para tipo EDM OData V4."""
    type_name = type(sql_type).__name__.lower()
    mapping = {
        "integer":       "Edm.Int32",
        "smallinteger":  "Edm.Int16",
        "biginteger":    "Edm.Int64",
        "string":        "Edm.String",
        "varchar":       "Edm.String",
        "text":          "Edm.String",
        "float":         "Edm.Double",
        "numeric":       "Edm.Decimal",
        "decimal":       "Edm.Decimal",
        "datetime":      "Edm.DateTimeOffset",
        "date":          "Edm.Date",
        "boolean":       "Edm.Boolean",
    }
    return mapping.get(type_name, "Edm.String")


def _is_pk(column) -> bool:
    """Retorna True se a coluna faz parte da chave primária."""
    return column.primary_key


# ─────────────────────────────────────────────────────────────────────────────
# Gerador de XML padrão OData V4
# ─────────────────────────────────────────────────────────────────────────────

def build_metadata_xml(entities: list) -> str:
    """
    Gera o documento $metadata em XML padrão OData V4.

    Inclui:
    - Definição de EntityType por modelo
    - Anotações de UI: ListView (UI.LineItem), FieldGroups (UI.FieldGroup)
    - Anotação de rótulo (Common.Label)
    - Indicação de campo obrigatório por coluna nullable=False

    Args:
        entities (list): Lista de classes de modelo SQLAlchemy.

    Returns:
        str: XML OData V4 formatado.
    """
    ns = {
        "edmx":   "http://docs.oasis-open.org/odata/ns/edmx",
        "edm":    "http://docs.oasis-open.org/odata/ns/edm",
        "common": "http://docs.oasis-open.org/odata/ns/Common",
        "ui":     "http://docs.oasis-open.org/odata/ns/UI",
    }

    root = ET.Element("edmx:Edmx", {
        "Version":       "4.0",
        "xmlns:edmx":    ns["edmx"],
        "xmlns:edm":     ns["edm"],
        "xmlns:common":  ns["common"],
        "xmlns:ui":      ns["ui"],
    })

    data_services = ET.SubElement(root, "edmx:DataServices")
    schema = ET.SubElement(data_services, "edm:Schema", {"Namespace": "S2MOdataPyDemo"})

    for entity_cls in entities:
        entity_type_elem = ET.SubElement(
            schema, "edm:EntityType", {"Name": entity_cls.__name__}
        )
        mapper = inspect(entity_cls)

        # Propriedades da entidade
        for column in mapper.columns:
            edm_type = _map_sql_type_to_edm(column.type)
            attrs = {
                "Name":     column.name,
                "Type":     edm_type,
                "Nullable": str(column.nullable).lower(),
            }
            if isinstance(column.type, String) and column.type.length:
                attrs["MaxLength"] = str(column.type.length)

            prop_elem = ET.SubElement(entity_type_elem, "edm:Property", attrs)

            # Marca campos não-PK nullable=False como obrigatórios
            if not column.nullable and not _is_pk(column):
                field_ctrl = ET.SubElement(
                    prop_elem, "Annotation", {"Term": "common.FieldControl"}
                )
                ET.SubElement(
                    field_ctrl, "EnumMember",
                    {"EnumMember": "common.FieldControlType/Mandatory"}
                )

        # Anotações declaradas via decorators
        ui_ann = getattr(entity_cls, "_ui_annotations", {})

        # Common.Label
        if "Label" in ui_ann:
            ann = ET.SubElement(entity_type_elem, "Annotation", {"Term": "common.Label"})
            ET.SubElement(ann, "String", {"String": ui_ann["Label"]})

        # UI.LineItem (ListView)
        if "ListView" in ui_ann:
            lv = ui_ann["ListView"]
            ann = ET.SubElement(entity_type_elem, "Annotation", {"Term": "ui.LineItem"})
            coll = ET.SubElement(ann, "Collection")
            for col in lv.get("columns", []):
                record = ET.SubElement(coll, "Record")
                ET.SubElement(record, "PropertyValue",
                              {"Property": "Label", "String": col["label"]})
                ET.SubElement(record, "PropertyValue",
                              {"Property": "Value", "Path": col["name"]})
                if col.get("sortable"):
                    ET.SubElement(record, "PropertyValue",
                                  {"Property": "Sortable", "Bool": "true"})
                if col.get("filterable"):
                    ET.SubElement(record, "PropertyValue",
                                  {"Property": "Filterable", "Bool": "true"})
            if lv.get("default_sort"):
                ET.SubElement(entity_type_elem, "Annotation",
                              {"Term": "ui.DefaultSort", "String": lv["default_sort"]})

        # UI.FieldGroup
        for group in ui_ann.get("FieldGroups", []):
            ann = ET.SubElement(entity_type_elem, "Annotation", {"Term": "ui.FieldGroup"})
            record = ET.SubElement(ann, "Record")
            ET.SubElement(record, "PropertyValue",
                          {"Property": "Name",  "String": group["name"]})
            ET.SubElement(record, "PropertyValue",
                          {"Property": "Label", "String": group["label"]})
            fields_elem = ET.SubElement(record, "PropertyValue", {"Property": "Fields"})
            coll = ET.SubElement(fields_elem, "Collection")
            for field_name in group.get("fields", []):
                ET.SubElement(coll, "PropertyPath", {"Path": field_name})

    rough = ET.tostring(root, encoding="utf-8", method="xml")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Gerador de JSON enriquecido
# ─────────────────────────────────────────────────────────────────────────────

def build_metadata_dict(entities: list) -> dict:
    """
    Gera os metadados no formato JSON enriquecido.

    Formato consumido pelo cliente S2MOdataPy via endpoint /$metadata.json.
    Inclui propriedades, anotações de UI e regras de validação.

    Args:
        entities (list): Lista de classes de modelo SQLAlchemy.

    Returns:
        dict: Dicionário com metadados completos de todas as entidades.
    """
    metadata = {
        "version":   "4.0",
        "namespace": "S2MOdataPyDemo",
        "entities":  [],
    }

    for entity_cls in entities:
        mapper = inspect(entity_cls)
        properties = []

        for column in mapper.columns:
            prop: dict = {
                "name":     column.name,
                "type":     _map_sql_type_to_edm(column.type),
                "nullable": column.nullable,
                "pk":       _is_pk(column),
            }
            if isinstance(column.type, String) and column.type.length:
                prop["maxLength"] = column.type.length
            # Campos não-PK nullable=False são obrigatórios
            if not column.nullable and not _is_pk(column):
                prop["required"] = True
            properties.append(prop)

        ui_ann      = getattr(entity_cls, "_ui_annotations", {})
        validations = getattr(entity_cls, "_validations", {})

        entity_info = {
            "name":        entity_cls.__name__,
            "label":       ui_ann.get("Label", entity_cls.__name__),
            "properties":  properties,
            "ui": {
                "listView":    ui_ann.get("ListView"),
                "fieldGroups": ui_ann.get("FieldGroups", []),
            },
            "validations": validations,
        }
        metadata["entities"].append(entity_info)

    return metadata
