## 🏗️ Arquitetura Proposta (Visão Geral)

```
┌─────────────────────────────────────────────────────────────────┐
│                       FASE 1: SERVIDOR OData                    │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI + OData Lib → Serviço com $metadata anotado            │
│  - Models (SQLAlchemy/Pydantic)                                 │
│  - Anotações CDS-style (Python decorators)                      │
│  - Exporta $metadata com SAP UI Annotations                     │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASE 2: CLIENTE S2MOdataPy                   │
├─────────────────────────────────────────────────────────────────┤
│  Biblioteca aprimorada com:                                     │
│  - Parser de $metadata com anotações                            │
│  - Query Builder melhorado                                      │
│  - Validações baseadas em anotações                             │
│  - Geração de configuração UI (JSON)                            │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASE 3: GERADOR DE UI                        │
├─────────────────────────────────────────────────────────────────┤
│  - Python: CLI para gerar HTML/React/Vue                        │
│  - JS: Componentes dinâmicos que leem $metadata                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Diretórios Proposta

```
S2MOdataPy/
├── s2modatapy/                    # Biblioteca cliente
│   ├── __init__.py
│   ├── client.py                  # Cliente OData (existente)
│   ├── annotations/               # NOVO: Parser de anotações
│   │   ├── __init__.py
│   │   ├── parser.py              # Lê SAP UI Annotations
│   │   ├── models.py              # Dataclasses para anotações
│   │   └── validator.py           # Validações baseadas em anotações
│   ├── server/                    # NOVO: Suporte a servidor OData
│   │   ├── __init__.py
│   │   ├── fastapi_odata.py       # FastAPI + OData
│   │   ├── annotations_builder.py # Cria anotações SAP UI
│   │   └── cds_decorators.py      # Decorators estilo CDS
│   └── ...
├── demo_server/                   # Servidor de exemplo
│   ├── main.py                    # FastAPI app
│   ├── models/                    # Modelos de dados
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── product.py
│   ├── annotations/               # Anotações via código
│   │   └── ui_annotations.py
│   └── data/                      # Dados mock
│       └── northwind_data.py
└── tests/
    └── test_annotations.py
```

---

## 📋 FASE 1: Servidor OData com Anotações

### 1.1 Modelos de Dados (estilo CDS)

```python
# demo_server/models/customer.py
from s2modatapy.server.cds_decorators import Entity, UI, Common

@Entity
@UI.ListView(
    columns=[
        UI.Field("CustomerID", label="Código", width="100px"),
        UI.Field("CompanyName", label="Empresa", sortable=True),
        UI.Field("Country", label="País", filterable=True),
    ],
    default_sort="CompanyName asc"
)
@UI.FieldGroup("BasicInfo", label="Informações Básicas", fields=[
    "CustomerID", "CompanyName", "ContactName", "ContactTitle"
])
@UI.FieldGroup("Location", label="Localização", fields=[
    "Country", "City", "Address", "PostalCode"
])
@Common.Label("Clientes")
class Customer(BaseModel):
    CustomerID: str = Field(..., max_length=5, description="Código único")
    CompanyName: str = Field(..., description="Nome da empresa")
    ContactName: Optional[str] = None
    ContactTitle: Optional[str] = None
    Country: str
    City: str
    Address: Optional[str] = None
```

### 1.2 Gerador de Anotações SAP UI

```python
# s2modatapy/server/annotations_builder.py
class SAPUIAnnotationsBuilder:
    """
    Constrói anotações SAP UI no formato OData XML
    """
    
    def build_line_item(self, columns: List[UI.Field]) -> str:
        """Gera UI.LineItem anotation para listas"""
        return f"""
        <Annotation Term="UI.LineItem">
            <Collection>
                {self._build_columns(columns)}
            </Collection>
        </Annotation>
        """
    
    def build_field_group(self, group: UI.FieldGroup) -> str:
        """Gera UI.FieldGroup para formulários"""
        pass
    
    def build_selection_fields(self, fields: List[str]) -> str:
        """Gera UI.SelectionFields para filtros"""
        pass
```

### 1.3 Servidor FastAPI + OData

```python
# demo_server/main.py
from fastapi import FastAPI
from s2modatapy.server.fastapi_odata import ODataServer
from .models import Customer, Order, Product

app = FastAPI(title="S2MOdataPy Demo Server")

# Configura servidor OData
odata = ODataServer(
    app,
    base_url="/odata",
    metadata_url="/odata/$metadata",
    annotations=SAPUIAnnotationsBuilder(),
    entities=[
        Customer,
        Order,
        Product,
    ]
)

# Endpoint para UI consumir anotações via JSON
@app.get("/odata/ui-config/{entity}")
def get_ui_config(entity: str):
    """Retorna apenas as anotações UI (para frontend JS)"""
    return odata.get_annotations_for_entity(entity)
```

---

## 📋 FASE 2: Cliente S2MOdataPy Aprimorado

### 2.1 Parser de Anotações SAP UI

```python
# s2modatapy/annotations/parser.py
class SAPUIAnnotationParser:
    """
    Parser para ler anotações SAP UI do $metadata
    """
    
    def parse_line_item(self, annotation_xml) -> List[UIField]:
        """Extrai UI.LineItem para listas"""
        pass
    
    def parse_field_groups(self, annotation_xml) -> List[UIFieldGroup]:
        """Extrai UI.FieldGroup para formulários"""
        pass
    
    def parse_selection_fields(self, annotation_xml) -> List[str]:
        """Extrai campos que podem ser usados em filtros"""
        pass
    
    def get_all_annotations(self, entity_name: str) -> UIAnnotations:
        """Retorna todas anotações UI para uma entidade"""
        return UIAnnotations(
            label=self.get_label(entity_name),
            list_view=self.get_list_view_config(entity_name),
            form=self.get_form_config(entity_name),
            filters=self.get_filterable_fields(entity_name),
            validations=self.get_validations(entity_name),
        )
```

### 2.2 Estrutura de Dados para Anotações

```python
# s2modatapy/annotations/models.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class FieldType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    DROPDOWN = "dropdown"
    REFERENCE = "reference"

@dataclass
class UIField:
    name: str
    label: str
    type: FieldType = FieldType.TEXT
    visible: bool = True
    sortable: bool = False
    filterable: bool = False
    required: bool = False
    max_length: Optional[int] = None
    width: Optional[str] = None
    reference_to: Optional[str] = None  # Para dropdown de entidades relacionadas

@dataclass
class UIListView:
    entity_name: str
    title: str
    columns: List[UIField]
    default_sort: Optional[str] = None
    page_size: int = 20

@dataclass
class UIForm:
    groups: List[UIFieldGroup]

@dataclass
class UIFieldGroup:
    name: str
    label: str
    fields: List[UIField]
    collapsible: bool = False

@dataclass
class UIAnnotations:
    entity_name: str
    label: str
    icon: Optional[str] = None
    list_view: Optional[UIListView] = None
    form: Optional[UIForm] = None
    filters: List[str] = field(default_factory=list)
    validations: Dict[str, Any] = field(default_factory=dict)
```

### 2.3 Cliente Aprimorado

```python
# s2modatapy/client.py (extensão)
class S2MClient:
    # ... código existente ...
    
    async def get_ui_annotations(self, entity_name: str) -> UIAnnotations:
        """
        Retorna anotações UI para uma entidade
        Pode vir do $metadata ou de endpoint específico
        """
        # Tenta buscar via endpoint otimizado
        try:
            response = self.session.get(f"{self.base_url}/ui-config/{entity_name}")
            if response.status_code == 200:
                return UIAnnotations.from_dict(response.json())
        except:
            pass
        
        # Fallback: parse do $metadata
        metadata = self.get_metadata()
        parser = SAPUIAnnotationParser(metadata)
        return parser.get_all_annotations(entity_name)
    
    def get_list_config(self, entity_name: str) -> dict:
        """Retorna configuração para frontend JS renderizar lista"""
        annotations = self.get_ui_annotations(entity_name)
        return {
            "title": annotations.label,
            "columns": [
                {"field": f.name, "label": f.label, "sortable": f.sortable}
                for f in annotations.list_view.columns
            ],
            "filters": annotations.filters,
            "default_sort": annotations.list_view.default_sort,
        }
```

---

## 📋 FASE 3: Consumo Multi-Plataforma

### 3.1 Python usando as anotações

```python
# Consumo via Python
from s2modatapy import S2MClient

client = S2MClient("http://localhost:8000/odata/")

# Obtém configuração da tela
config = client.get_list_config("Customers")
print(f"Lista de {config['title']}")
print(f"Colunas: {config['columns']}")

# Usa as anotações para construir query automaticamente
query = client.entity("Customers")
for filter_field in config['filters']:
    # Adiciona filtros padrão baseados nas anotações
    pass

result = query.get()
```

### 3.2 Frontend JS consumindo via API

```javascript
// React/Vue consumindo configuração
async function loadCustomerList() {
    // Opção 1: Buscar configuração UI
    const config = await fetch('/odata/ui-config/Customers').then(r => r.json());
    
    // Opção 2: Parser do $metadata diretamente
    const metadata = await fetch('/odata/$metadata').then(r => r.text());
    const parser = new ODataAnnotationParser(metadata);
    const config = parser.getListConfig('Customers');
    
    // Renderiza tabela dinâmica
    return (
        <DataTable
            columns={config.columns}
            data={await fetch(`/odata/Customers?$select=${config.columns.join(',')}`)}
        />
    );
}
```

### 3.3 Validações no Cliente

```python
# s2modatapy/annotations/validator.py
class ODataValidator:
    """
    Valida dados baseados nas anotações do $metadata
    """
    
    def validate_entity(self, entity_name: str, data: dict) -> ValidationResult:
        annotations = self.client.get_ui_annotations(entity_name)
        
        for field, value in data.items():
            # Campo obrigatório?
            if field in annotations.validations.get('required', []):
                if not value:
                    return ValidationResult(False, f"{field} é obrigatório")
            
            # Max length?
            max_len = annotations.validations.get('max_length', {}).get(field)
            if max_len and len(str(value)) > max_len:
                return ValidationResult(False, f"{field} excede {max_len} caracteres")
        
        return ValidationResult(True, "OK")

# Uso
validator = ODataValidator(client)
result = validator.validate_entity("Customers", {"CustomerID": "ABC"})
if not result.is_valid:
    print(f"Erro: {result.message}")
```

---

## 🗺️ Roadmap com Marcos Claros

### Sprint 1: Base do Servidor (1-2 semanas)
- [ ] Criar estrutura `demo_server/`
- [ ] Implementar decorators estilo CDS (`@UI.ListView`, `@UI.FieldGroup`)
- [ ] FastAPI + OData básico (fake data)
- [ ] Gerar $metadata com anotações SAP UI simples

### Sprint 2: Parser de Anotações (1-2 semanas)
- [ ] Implementar `SAPUIAnnotationParser`
- [ ] Extrair `UI.LineItem` (listas)
- [ ] Extrair `UI.FieldGroup` (formulários)
- [ ] Extrair `Common.Label` (títulos)

### Sprint 3: Integração Cliente (1 semana)
- [ ] Adicionar `get_ui_annotations()` ao `S2MClient`
- [ ] Implementar `get_list_config()` e `get_form_config()`
- [ ] Validador baseado em anotações

### Sprint 4: Validações e Consumo JS (1 semana)
- [ ] Endpoint `/ui-config/{entity}` para JS
- [ ] Exemplo de consumo com React/Vue
- [ ] Documentação de uso

---

## 💡 Decisões de Design para Debate

### 1. Como referenciar entidades relacionadas?

```python
# Opção A: Automático via NavigationProperty
class Order(BaseModel):
    CustomerID: str
    # O parser detecta NavigationProperty e gera dropdown

# Opção B: Anotação explícita
@UI.SelectionFields(["CustomerID"])
@UI.ValueList("Customers", params={"CustomerID": "CustomerID"})
class Order(BaseModel):
    pass
```

### 2. Validações: Servidor vs Cliente?

| Validação | Servidor | Cliente |
|-----------|----------|---------|
| Required | ✅ Obrigatório | ✅ UI mark |
| MaxLength | ✅ Obrigatório | ⚠️ Opcional |
| Format (email) | ✅ Obrigatório | ⚠️ Opcional |
| Unique | ✅ Obrigatório | ❌ Não |

### 3. Como lidar com múltiplos idiomas?

```python
# Opção: anotações multi-idioma
@UI.Label(locale="pt-BR", value="Clientes")
@UI.Label(locale="en-US", value="Customers")
class Customer(BaseModel):
    pass

# Cliente pede ?locale=pt-BR
```

