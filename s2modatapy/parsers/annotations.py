"""
Parser de metadados OData com anotações de UI.

Lê o documento $metadata (XML padrão OData V4 ou JSON enriquecido)
e produz objetos Python tipados que descrevem como cada entidade
deve ser apresentada: colunas de listagem, grupos de formulário,
campos filtráveis e regras de validação.

Author: Christopher N. S. M. Mauricio
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Enumerações
# ─────────────────────────────────────────────────────────────────────────────

class FieldType(Enum):
    """Tipo de dado lógico de um campo da entidade."""
    TEXT      = "text"
    NUMBER    = "number"
    DATE      = "date"
    BOOLEAN   = "boolean"
    DROPDOWN  = "dropdown"


# ─────────────────────────────────────────────────────────────────────────────
# Dataclasses — modelo de dados das anotações
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class UIField:
    """Representa um campo com suas configurações de apresentação."""
    name:       str
    label:      str
    type:       FieldType        = FieldType.TEXT
    visible:    bool             = True
    sortable:   bool             = False
    filterable: bool             = False
    required:   bool             = False
    max_length: Optional[int]    = None
    width:      Optional[str]    = None


@dataclass
class UIListView:
    """Configuração de exibição em modo lista / tabela."""
    entity_name:  str
    title:        str
    columns:      List[UIField]  = field(default_factory=list)
    default_sort: Optional[str] = None
    page_size:    int            = 20


@dataclass
class UIFieldGroup:
    """Grupo de campos para exibição em formulário."""
    name:        str
    label:       str
    fields:      List[UIField]  = field(default_factory=list)
    collapsible: bool           = False


@dataclass
class UIForm:
    """Configuração completa de formulário (conjunto de grupos de campos)."""
    groups: List[UIFieldGroup] = field(default_factory=list)


@dataclass
class UIAnnotations:
    """
    Todas as anotações de UI de uma entidade.

    Produzida pelo ODataAnnotationParser e usada para gerar
    telas, tabelas e formulários dinamicamente.

    Attributes:
        entity_name:  Nome técnico da entidade (ex: 'Customers').
        label:        Rótulo legível da entidade (ex: 'Clientes').
        list_view:    Configuração da listagem (colunas, ordenação padrão).
        form:         Configuração do formulário (grupos de campos).
        filters:      Lista de campos disponíveis para filtro.
        validations:  Regras de validação por campo.
    """
    entity_name:  str
    label:        str
    icon:         Optional[str]       = None
    list_view:    Optional[UIListView] = None
    form:         Optional[UIForm]     = None
    filters:      List[str]           = field(default_factory=list)
    validations:  Dict[str, Any]      = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Parser principal
# ─────────────────────────────────────────────────────────────────────────────

class ODataAnnotationParser:
    """
    Parser de metadados OData com anotações de UI.

    Aceita duas fontes de entrada:
    - XML padrão OData V4 (endpoint /$metadata)
    - JSON enriquecido (endpoint /$metadata.json)

    O JSON enriquecido é o formato preferido por ser mais simples
    de processar e por incluir informações de validação que o XML
    padrão não contempla diretamente.

    Uso com XML:
        parser = ODataAnnotationParser(metadata_xml=xml_string)
        ann = parser.parse_entity("Customers")

    Uso com JSON (via cliente):
        parser = ODataAnnotationParser.from_dict(metadata_dict)
        ann = parser.parse_entity("Customers")
        print(ann.label)
        print(ann.list_view.columns)

    Uso direto pelo cliente:
        ann = client.get_ui_annotations("Customers")
    """

    # Namespaces padrão OData V4
    _NS = {
        "edmx":   "http://docs.oasis-open.org/odata/ns/edmx",
        "edm":    "http://docs.oasis-open.org/odata/ns/edm",
        "common": "http://docs.oasis-open.org/odata/ns/Common",
        "ui":     "http://docs.oasis-open.org/odata/ns/UI",
    }

    def __init__(self, metadata_xml: Optional[str] = None):
        """
        Inicializa o parser com documento XML.

        Para JSON, utilize o método de classe ODataAnnotationParser.from_dict().

        Args:
            metadata_xml (str, optional): Conteúdo XML do $metadata OData V4.
        """
        self._metadata_dict: Optional[dict] = None
        self._root: Optional[ET.Element]    = None

        if metadata_xml:
            self._root = ET.fromstring(metadata_xml)

    @classmethod
    def from_dict(cls, metadata_dict: dict) -> "ODataAnnotationParser":
        """
        Cria o parser a partir de um dicionário JSON (/$metadata.json).

        Args:
            metadata_dict (dict): Dicionário retornado pelo endpoint
                                  /$metadata.json do servidor.

        Returns:
            ODataAnnotationParser: Instância pronta para uso.
        """
        instance = cls()
        instance._metadata_dict = metadata_dict
        return instance

    # ─────────────────────────────────────────────────────────────────────────
    # Interface pública
    # ─────────────────────────────────────────────────────────────────────────

    def get_all_entities(self) -> List[str]:
        """
        Retorna os nomes de todas as entidades disponíveis nos metadados.

        Returns:
            list[str]: Lista de nomes de entidades.
        """
        if self._metadata_dict is not None:
            return [e["name"] for e in self._metadata_dict.get("entities", [])]
        if self._root is not None:
            return [
                et.get("Name")
                for et in self._root.findall(".//edm:EntityType", self._NS)
            ]
        return []

    def parse_entity(self, entity_name: str) -> UIAnnotations:
        """
        Extrai e devolve todas as anotações de UI para uma entidade.

        Args:
            entity_name (str): Nome da entidade (ex: 'Customers').

        Returns:
            UIAnnotations: Objeto completo com configurações de UI.
                           Retorna objeto vazio (apenas com entity_name e label)
                           se a entidade não for encontrada.
        """
        if self._metadata_dict is not None:
            return self._parse_entity_from_dict(entity_name)
        if self._root is not None:
            return self._parse_entity_from_xml(entity_name)
        return UIAnnotations(entity_name=entity_name, label=entity_name)

    def to_ui_config(self, entity_name: str) -> dict:
        """
        Retorna um dicionário simples com a configuração de UI da entidade,
        adequado para serialização JSON ou passagem a componentes de frontend.

        Args:
            entity_name (str): Nome da entidade.

        Returns:
            dict: Configuração com chaves 'entity', 'label',
                  'listView', 'form', 'filters'.
        """
        ann = self.parse_entity(entity_name)
        result: dict = {
            "entity":  ann.entity_name,
            "label":   ann.label,
            "filters": ann.filters,
        }

        if ann.list_view:
            result["listView"] = {
                "title":       ann.list_view.title,
                "defaultSort": ann.list_view.default_sort,
                "columns": [
                    {
                        "field":      col.name,
                        "label":      col.label,
                        "sortable":   col.sortable,
                        "filterable": col.filterable,
                        "width":      col.width,
                    }
                    for col in ann.list_view.columns
                ],
            }

        if ann.form:
            result["form"] = {
                "groups": [
                    {
                        "name":   g.name,
                        "label":  g.label,
                        "fields": [
                            {"name": f.name, "label": f.label, "required": f.required}
                            for f in g.fields
                        ],
                    }
                    for g in ann.form.groups
                ]
            }

        if ann.validations:
            result["validations"] = ann.validations

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Parsing a partir de JSON (/_metadata.json)
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_entity_from_dict(self, entity_name: str) -> UIAnnotations:
        """Processa anotações a partir do formato JSON enriquecido."""
        entities = self._metadata_dict.get("entities", [])
        entity_data = next(
            (e for e in entities if e.get("name") == entity_name), None
        )
        if entity_data is None:
            return UIAnnotations(entity_name=entity_name, label=entity_name)

        label = entity_data.get("label", entity_name)
        ui    = entity_data.get("ui", {})
        validations = entity_data.get("validations", {})
        properties  = {p["name"]: p for p in entity_data.get("properties", [])}

        # ListView
        list_view = None
        lv_data = ui.get("listView")
        if lv_data:
            columns = []
            for col in lv_data.get("columns", []):
                prop = properties.get(col["name"], {})
                columns.append(
                    UIField(
                        name=col["name"],
                        label=col.get("label", col["name"]),
                        sortable=col.get("sortable", False),
                        filterable=col.get("filterable", False),
                        width=col.get("width"),
                        required=prop.get("required", False),
                        max_length=prop.get("maxLength"),
                        type=self._edm_to_field_type(prop.get("type", "Edm.String")),
                    )
                )
            list_view = UIListView(
                entity_name=entity_name,
                title=label,
                columns=columns,
                default_sort=lv_data.get("default_sort"),
            )

        # Form (FieldGroups)
        form = None
        groups_data = ui.get("fieldGroups", [])
        if groups_data:
            groups = []
            for gd in groups_data:
                fields_in_group = []
                for field_name in gd.get("fields", []):
                    prop = properties.get(field_name, {})
                    val_rules = validations.get(field_name, [])
                    is_required = prop.get("required", False) or any(
                        r.get("type") == "required" for r in val_rules
                    )
                    fields_in_group.append(
                        UIField(
                            name=field_name,
                            label=field_name,
                            required=is_required,
                            max_length=prop.get("maxLength"),
                            type=self._edm_to_field_type(prop.get("type", "Edm.String")),
                        )
                    )
                groups.append(
                    UIFieldGroup(
                        name=gd.get("name", "group"),
                        label=gd.get("label", gd.get("name", "Grupo")),
                        fields=fields_in_group,
                        collapsible=gd.get("collapsible", False),
                    )
                )
            form = UIForm(groups=groups)

        # Campos filtráveis
        filters = [
            p["name"]
            for p in entity_data.get("properties", [])
            if "String" in p.get("type", "")
        ]

        return UIAnnotations(
            entity_name=entity_name,
            label=label,
            list_view=list_view,
            form=form,
            filters=filters,
            validations=validations,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Parsing a partir de XML (/$metadata)
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_entity_from_xml(self, entity_name: str) -> UIAnnotations:
        """Processa anotações a partir do XML OData V4 padrão."""
        entity_type = self._root.find(
            f".//edm:EntityType[@Name='{entity_name}']", self._NS
        )
        if entity_type is None:
            return UIAnnotations(entity_name=entity_name, label=entity_name)

        label     = self._xml_extract_label(entity_type)
        list_view = self._xml_extract_list_view(entity_name, entity_type)
        form      = self._xml_extract_form(entity_type)
        filters   = self._xml_extract_filterable_fields(entity_type)

        return UIAnnotations(
            entity_name=entity_name,
            label=label,
            list_view=list_view,
            form=form,
            filters=filters,
        )

    def _xml_extract_label(self, entity_type: ET.Element) -> str:
        label_ann = entity_type.find(".//Annotation[@Term='Common.Label']", self._NS)
        if label_ann is not None:
            string_elem = label_ann.find(".//String", self._NS)
            if string_elem is not None:
                return string_elem.get("String", entity_type.get("Name", ""))
        return entity_type.get("Name", "")

    def _xml_extract_list_view(
        self, entity_name: str, entity_type: ET.Element
    ) -> Optional[UIListView]:
        line_item = entity_type.find(".//Annotation[@Term='UI.LineItem']", self._NS)
        if line_item is None:
            return None

        columns = []
        collection = line_item.find(".//Collection", self._NS)
        if collection is not None:
            for record in collection.findall(".//Record", self._NS):
                uif = self._xml_parse_column(record)
                if uif:
                    columns.append(uif)

        return UIListView(
            entity_name=entity_name,
            title=entity_name,
            columns=columns,
            default_sort=None,
        )

    def _xml_parse_column(self, record: ET.Element) -> Optional[UIField]:
        field_name = label = None
        sortable   = filterable = False
        for prop in record.findall(".//PropertyValue", self._NS):
            pname = prop.get("Property")
            if pname == "Value":
                field_name = prop.get("Path")
            elif pname == "Label":
                label = prop.get("String")
            elif pname == "Sortable":
                sortable = prop.get("Bool") == "true"
            elif pname == "Filterable":
                filterable = prop.get("Bool") == "true"
        if field_name:
            return UIField(
                name=field_name,
                label=label or field_name,
                sortable=sortable,
                filterable=filterable,
            )
        return None

    def _xml_extract_form(self, entity_type: ET.Element) -> Optional[UIForm]:
        groups = []
        for fg in entity_type.findall(".//Annotation[@Term='UI.FieldGroup']", self._NS):
            collection = fg.find(".//Collection", self._NS)
            if collection is None:
                continue
            for record in collection.findall(".//Record", self._NS):
                group = self._xml_parse_field_group(record)
                if group:
                    groups.append(group)
        return UIForm(groups=groups) if groups else None

    def _xml_parse_field_group(self, record: ET.Element) -> Optional[UIFieldGroup]:
        group_name = group_label = None
        fields_list: List[UIField] = []
        for prop in record.findall(".//PropertyValue", self._NS):
            pname = prop.get("Property")
            if pname == "Name":
                group_name = prop.get("String")
            elif pname == "Label":
                group_label = prop.get("String")
            elif pname == "Fields":
                for path in prop.findall(".//PropertyPath", self._NS):
                    fname = path.get("Path")
                    if fname:
                        fields_list.append(UIField(name=fname, label=fname))
        if group_name or group_label:
            return UIFieldGroup(
                name=group_name or "group",
                label=group_label or group_name or "Grupo",
                fields=fields_list,
            )
        return None

    def _xml_extract_filterable_fields(self, entity_type: ET.Element) -> List[str]:
        filterable = []
        for prop in entity_type.findall(".//edm:Property", self._NS):
            pname = prop.get("Name")
            ptype = prop.get("Type", "")
            if "String" in ptype and pname:
                filterable.append(pname)
        return filterable

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _edm_to_field_type(edm_type: str) -> FieldType:
        """Converte tipo EDM OData para FieldType interno."""
        mapping = {
            "Edm.String":          FieldType.TEXT,
            "Edm.Int16":           FieldType.NUMBER,
            "Edm.Int32":           FieldType.NUMBER,
            "Edm.Int64":           FieldType.NUMBER,
            "Edm.Double":          FieldType.NUMBER,
            "Edm.Decimal":         FieldType.NUMBER,
            "Edm.Single":          FieldType.NUMBER,
            "Edm.Boolean":         FieldType.BOOLEAN,
            "Edm.Date":            FieldType.DATE,
            "Edm.DateTimeOffset":  FieldType.DATE,
        }
        return mapping.get(edm_type, FieldType.TEXT)
