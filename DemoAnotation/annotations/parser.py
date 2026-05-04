# s2modatapy/annotations/parser.py
"""
Parser para anotações SAP UI no $metadata OData
Autor: Christopher N. S. M. Mauricio
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class FieldType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    DROPDOWN = "dropdown"


@dataclass
class UIField:
    """Representa um campo com anotações UI"""
    name: str
    label: str
    type: FieldType = FieldType.TEXT
    visible: bool = True
    sortable: bool = False
    filterable: bool = False
    required: bool = False
    max_length: Optional[int] = None
    width: Optional[str] = None


@dataclass
class UIListView:
    """Configuração de lista/table view"""
    entity_name: str
    title: str
    columns: List[UIField] = field(default_factory=list)
    default_sort: Optional[str] = None
    page_size: int = 20


@dataclass
class UIFieldGroup:
    """Grupo de campos para formulário"""
    name: str
    label: str
    fields: List[UIField] = field(default_factory=list)
    collapsible: bool = False


@dataclass
class UIForm:
    """Configuração de formulário"""
    groups: List[UIFieldGroup] = field(default_factory=list)


@dataclass
class UIAnnotations:
    """Todas as anotações UI para uma entidade"""
    entity_name: str
    label: str
    icon: Optional[str] = None
    list_view: Optional[UIListView] = None
    form: Optional[UIForm] = None
    filters: List[str] = field(default_factory=list)
    validations: Dict[str, Any] = field(default_factory=dict)


class SAPUIAnnotationParser:
    """
    Parser para anotações SAP UI no formato OData $metadata
    
    Exemplo de uso:
        parser = SAPUIAnnotationParser(metadata_xml)
        annotations = parser.parse_entity("Customers")
        print(annotations.label)  # "Clientes"
        print(annotations.list_view.columns[0].label)  # "Código"
    """
    
    def __init__(self, metadata_xml: str):
        self.metadata_xml = metadata_xml
        self.root = ET.fromstring(metadata_xml)
        # Namespaces comuns no OData
        self.ns = {
            'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
            'edm': 'http://docs.oasis-open.org/odata/ns/edm',
            'sap': 'http://www.sap.com/Protocols/SAPData',
            'common': 'http://docs.oasis-open.org/odata/ns/Common',
            'ui': 'http://docs.oasis-open.org/odata/ns/UI'
        }
    
    def parse_entity(self, entity_name: str) -> UIAnnotations:
        """
        Extrai todas as anotações UI para uma entidade específica
        
        Args:
            entity_name: Nome da entidade (ex: "Customers")
            
        Returns:
            UIAnnotations: Objeto com todas as configurações UI
        """
        # Busca o EntityType pelo nome
        entity_type = self.root.find(f".//edm:EntityType[@Name='{entity_name}']", self.ns)
        
        if entity_type is None:
            return UIAnnotations(entity_name=entity_name, label=entity_name)
        
        # Extrai label (Common.Label)
        label = self._extract_label(entity_type)
        
        # Extrai configuração de lista (UI.LineItem)
        list_view = self._extract_list_view(entity_name, entity_type)
        
        # Extrai grupos de formulário (UI.FieldGroup)
        form = self._extract_form(entity_type)
        
        # Extrai campos filtráveis
        filters = self._extract_filterable_fields(entity_type)
        
        return UIAnnotations(
            entity_name=entity_name,
            label=label,
            list_view=list_view,
            form=form,
            filters=filters
        )
    
    def _extract_label(self, entity_type: ET.Element) -> str:
        """Extrai o label da entidade (Common.Label)"""
        label_ann = entity_type.find(".//Annotation[@Term='Common.Label']", self.ns)
        if label_ann is not None:
            string_elem = label_ann.find(".//String", self.ns)
            if string_elem is not None:
                return string_elem.get('String', entity_type.get('Name', ''))
        return entity_type.get('Name', '')
    
    def _extract_list_view(self, entity_name: str, entity_type: ET.Element) -> Optional[UIListView]:
        """Extrai a configuração de lista (UI.LineItem)"""
        line_item = entity_type.find(".//Annotation[@Term='UI.LineItem']", self.ns)
        
        if line_item is None:
            return None
        
        columns = []
        collection = line_item.find(".//Collection", self.ns)
        
        if collection is not None:
            for record in collection.findall(".//Record", self.ns):
                field = self._parse_column_from_record(record)
                if field:
                    columns.append(field)
        
        # Tenta extrair ordenação padrão
        default_sort = self._extract_default_sort(entity_type)
        
        return UIListView(
            entity_name=entity_name,
            title=entity_name,
            columns=columns,
            default_sort=default_sort
        )
    
    def _parse_column_from_record(self, record: ET.Element) -> Optional[UIField]:
        """Converte um Record do UI.LineItem em UIField"""
        field_name = None
        label = None
        sortable = False
        
        for prop in record.findall(".//PropertyValue", self.ns):
            prop_name = prop.get('Property')
            if prop_name == 'Value':
                field_name = prop.get('Path')
            elif prop_name == 'Label':
                label = prop.get('String')
            elif prop_name == 'Sortable':
                sortable = prop.get('Bool') == 'true'
        
        if field_name:
            return UIField(
                name=field_name,
                label=label or field_name,
                sortable=sortable,
                filterable=True  # Por padrão, campos na lista são filtráveis
            )
        return None
    
    def _extract_default_sort(self, entity_type: ET.Element) -> Optional[str]:
        """Extrai ordenação padrão das anotações"""
        # Procura por anotação de ordenação padrão (customizada)
        sort_ann = entity_type.find(".//Annotation[@Term='UI.DefaultSort']", self.ns)
        if sort_ann is not None:
            return sort_ann.get('String')
        return None
    
    def _extract_form(self, entity_type: ET.Element) -> Optional[UIForm]:
        """Extrai configuração de formulário (UI.FieldGroup)"""
        groups = []
        
        for field_group in entity_type.findall(".//Annotation[@Term='UI.FieldGroup']", self.ns):
            collection = field_group.find(".//Collection", self.ns)
            for record in collection.findall(".//Record", self.ns):
                group = self._parse_field_group(record)
                if group:
                    groups.append(group)
        
        if groups:
            return UIForm(groups=groups)
        return None
    
    def _parse_field_group(self, record: ET.Element) -> Optional[UIFieldGroup]:
        """Converte um Record do UI.FieldGroup em UIFieldGroup"""
        group_name = None
        group_label = None
        fields = []
        
        for prop in record.findall(".//PropertyValue", self.ns):
            prop_name = prop.get('Property')
            if prop_name == 'Name':
                group_name = prop.get('String')
            elif prop_name == 'Label':
                group_label = prop.get('String')
            elif prop_name == 'Fields':
                for field_ref in prop.findall(".//PropertyPath", self.ns):
                    field_name = field_ref.get('Path')
                    if field_name:
                        fields.append(UIField(name=field_name, label=field_name))
        
        if group_name or group_label:
            return UIFieldGroup(
                name=group_name or f"group_{len(fields)}",
                label=group_label or group_name or "Grupo",
                fields=fields
            )
        return None
    
    def _extract_filterable_fields(self, entity_type: ET.Element) -> List[str]:
        """Extrai campos marcados como filtráveis"""
        filterable_fields = []
        
        # Procura por propriedades com anotação filterable
        for prop in entity_type.findall(".//edm:Property", self.ns):
            prop_name = prop.get('Name')
            # Verifica se há anotação filterable
            filter_ann = prop.find(".//Annotation[@Term='UI.Filterable']", self.ns)
            if filter_ann is not None:
                is_filterable = filter_ann.get('Bool') == 'true'
                if is_filterable and prop_name:
                    filterable_fields.append(prop_name)
            else:
                # Por padrão, campos string são filtráveis
                prop_type = prop.get('Type', '')
                if 'String' in prop_type and prop_name:
                    filterable_fields.append(prop_name)
        
        return filterable_fields
    
    def get_all_entities(self) -> List[str]:
        """Retorna lista de todas as entidades disponíveis"""
        entities = []
        for entity_type in self.root.findall(".//edm:EntityType", self.ns):
            entities.append(entity_type.get('Name'))
        return entities
    
    def to_json(self, entity_name: str) -> dict:
        """Retorna anotações em formato JSON (para consumo por frontend JS)"""
        annotations = self.parse_entity(entity_name)
        
        result = {
            "entity": annotations.entity_name,
            "label": annotations.label,
            "filters": annotations.filters,
        }
        
        if annotations.list_view:
            result["listView"] = {
                "title": annotations.list_view.title,
                "columns": [
                    {
                        "field": col.name,
                        "label": col.label,
                        "sortable": col.sortable,
                        "filterable": col.filterable
                    }
                    for col in annotations.list_view.columns
                ],
                "defaultSort": annotations.list_view.default_sort
            }
        
        if annotations.form:
            result["form"] = {
                "groups": [
                    {
                        "label": group.label,
                        "fields": [{"name": f.name, "label": f.label} for f in group.fields]
                    }
                    for group in annotations.form.groups
                ]
            }
        
        return result