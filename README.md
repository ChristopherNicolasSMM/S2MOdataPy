# S2MOdataPy

Biblioteca Python para consumo de serviços **OData V4** com suporte a
metadados enriquecidos com **anotações de UI** — permitindo a geração
dinâmica de telas a partir da definição das entidades.

**Versão:** 0.2.0  
**Autor:** Christopher N. S. M. Mauricio  
**Licença:** MIT with Attribution

---

## Instalação

```bash
pip install s2modatapy
```

Ou a partir do fonte:

```bash
pip install -e ".[dev]"
```

---

## Início Rápido

```python
from s2modatapy import S2MClient

client = S2MClient("http://localhost:8000/odata/")

# Consulta com filtro, ordenação e paginação
result = (
    client.entity("Customers")
    .filter("Country eq 'Brazil'")
    .orderby("CompanyName")
    .top(10)
    .get()
)

for c in result["value"]:
    print(c["CompanyName"])
```

---

## Funcionalidades

### Consultas (leitura)

| Método           | Parâmetro OData | Descrição                        |
|------------------|-----------------|----------------------------------|
| `.select(*fields)` | `$select`     | Escolhe quais campos retornar    |
| `.filter(expr)`    | `$filter`     | Filtra registros por condição    |
| `.orderby(f, dir)` | `$orderby`    | Ordena por campo                 |
| `.orderby_multi()` | `$orderby`    | Ordenação por múltiplos campos   |
| `.top(n)`          | `$top`        | Limita número de registros       |
| `.skip(n)`         | `$skip`       | Pula N registros (paginação)     |
| `.expand(*ents)`   | `$expand`     | Expande entidades relacionadas   |
| `.count()`         | `$count`      | Inclui total de registros        |
| `.page(pg, size)`  | —             | Atalho de paginação              |

#### Métodos de execução

```python
result = builder.get()        # Retorna dict com "value" e "@odata.count"
record = builder.first()      # Retorna o primeiro registro ou None
total  = builder.count_only() # Retorna apenas o count total (inteiro)
```

### Escrita

```python
# Criar registro
novo = client.entity("Customers").create({
    "CustomerID": "BRASI",
    "CompanyName": "Brasil Ltda",
    "Country": "Brazil"
})

# Atualização parcial (PATCH — só os campos enviados são alterados)
client.entity("Customers").patch("BRASI", {"ContactName": "João Silva"})

# Substituição completa (PUT — todos os campos devem ser enviados)
client.entity("Customers").update("BRASI", {
    "CustomerID": "BRASI",
    "CompanyName": "Brasil S.A.",
    "Country": "Brazil"
})

# Remover registro
client.entity("Customers").delete("BRASI")
```

### Metadados e Anotações de UI

O cliente pode consultar os metadados do servidor para obter informações
de apresentação (colunas de lista, grupos de formulário, validações):

```python
# Listar entidades disponíveis
entidades = client.list_entities()
# ['Customer', 'Order', 'Product']

# Obter anotações de UI de uma entidade
ann = client.get_ui_annotations("Customer")

print(ann.label)  # "Clientes"

# Colunas da listagem
for col in ann.list_view.columns:
    print(col.name, col.label, col.sortable, col.filterable)

# Grupos do formulário
for grupo in ann.form.groups:
    print(grupo.label)
    for campo in grupo.fields:
        print(f"  {campo.name} {'(obrigatório)' if campo.required else ''}")

# Validações
for campo, regras in ann.validations.items():
    for r in regras:
        print(f"{campo}: {r['type']} — {r['message']}")
```

### Autenticação

```python
# Basic Auth
client = S2MClient("http://servidor/odata/", auth=("usuario", "senha"))

# Bearer Token
client = S2MClient("http://servidor/odata/", bearer_token="meu-token")
```

### Tratamento de Erros

```python
from s2modatapy import (
    S2MODataConnectionError,
    S2MODataNotFoundError,
    S2MODataAuthenticationError,
    S2MODataError,
)

try:
    result = client.entity("Customers").get()
except S2MODataConnectionError:
    print("Servidor inacessível")
except S2MODataAuthenticationError:
    print("Credenciais inválidas")
except S2MODataNotFoundError:
    print("Entidade não encontrada")
except S2MODataError as e:
    print(f"Erro: {e}")
    print(f"Detalhes: {e.details}")
```

---

## Usando o Parser Diretamente

```python
from s2modatapy.parsers.annotations import ODataAnnotationParser

# A partir de JSON (endpoint /$metadata.json)
metadata = client.get_metadata_json()
parser = ODataAnnotationParser.from_dict(metadata)

# A partir de XML (endpoint /$metadata)
import requests
xml = requests.get("http://servidor/odata/$metadata").text
parser = ODataAnnotationParser(metadata_xml=xml)

# Obter configuração pronta para uso em componentes de UI
config = parser.to_ui_config("Customer")
# {
#   "entity": "Customer",
#   "label": "Clientes",
#   "listView": {"columns": [...], "defaultSort": "..."},
#   "form": {"groups": [...]},
#   "filters": [...],
#   "validations": {...}
# }
```

---

## Executar os Testes

```bash
pytest
# ou com cobertura
pytest --cov=s2modatapy --cov-report=term-missing
```

---

## Changelog

### 0.2.0
- Adicionado suporte a operações de escrita: `create()`, `update()`, `patch()`, `delete()`
- Adicionado suporte a autenticação Basic Auth e Bearer Token
- Adicionado `ODataAnnotationParser` com suporte a JSON (`from_dict`) e XML
- Adicionados métodos `S2MClient.get_metadata_json()`, `get_ui_annotations()`, `list_entities()`
- Adicionado atalho de paginação `page(number, size)`
- Adicionado `orderby_multi()` para ordenação por múltiplos campos
- Adicionada exceção `S2MODataParseError`
- Erro HTTP 401/403 agora levanta `S2MODataAuthenticationError`
- Erro HTTP 404 agora levanta `S2MODataNotFoundError`
- Resposta vazia (DELETE 204) tratada corretamente
- Removida dependência `lxml` (não utilizada)
- Testes expandidos cobrindo todos os novos métodos

### 0.1.2
- Versão inicial com leitura básica e debug monitor
