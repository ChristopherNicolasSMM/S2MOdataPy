# DemoAnotation — Servidor OData V4 com Anotações de UI

**Versão:** 1.0.0  
**Autor:** Christopher N. S. M. Mauricio

## Visão Geral

O diretório `DemoAnotation` é um projeto de demonstração (demo) que faz parte do repositório da biblioteca **S2MOdataPy**. Seu principal objetivo é servir como um ambiente de testes e validação das funcionalidades da biblioteca, bem como ilustrar o uso prático de um servidor OData com anotações SAP UI e validações.

Nele, você encontrará:

- Um servidor OData construído com **FastAPI** e **SQLAlchemy**.
- Exposição de metadados nos formatos XML (padrão OData) e JSON (customizado).
- Suporte a operações CRUD completas (Create, Read, Update, Delete).
- Filtros, ordenação, paginação e projeção de campos (`$filter`, `$orderby`, `$top`/`$skip`, `$select`).
- Anotações SAP UI (`UI.LineItem`, `UI.FieldGroup`, `Common.Label`, validações).
- Testes automatizados com `pytest` cobrindo todas essas funcionalidades.

---

## Conceito

As anotações de UI — inspiradas no padrão de extensões do protocolo OData V4 —
permitem que o próprio modelo declare como deve ser apresentado:
quais colunas aparecem na lista, quais campos compõem cada grupo de formulário
e quais regras de validação se aplicam.

```python
@Common.Label("Clientes")
@UI.ListView(
    columns=[
        UI.Field("CustomerID",  label="Código"),
        UI.Field("CompanyName", label="Empresa", sortable=True, filterable=True),
    ],
    default_sort="CompanyName asc",
)
@UI.FieldGroup("BasicInfo", label="Informações Básicas",
               fields=["CustomerID", "CompanyName", "ContactName"])
@Validation.Required("CustomerID")
@Validation.MaxLength("CustomerID", 5)
class Customer(Base):
    ...
```

Esses metadados são expostos em:
- `GET /odata/$metadata`      → XML padrão OData V4
- `GET /odata/$metadata.json` → JSON enriquecido, consumido pela biblioteca **S2MOdataPy**

---

## Entidades Disponíveis

| Entidade    | Endpoint              | Descrição         |
|-------------|-----------------------|-------------------|
| `Customers` | `/odata/Customers`    | Clientes          |
| `Orders`    | `/odata/Orders`       | Pedidos           |
| `Products`  | `/odata/Products`     | Produtos          |

---

## Instalação

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Instale a biblioteca cliente (pasta irmã)
pip install -e ../S2MOdataPy
```

---

## Executar o Servidor

```bash
uvicorn main:app --reload --port 8000
```

Acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc:      http://localhost:8000/redoc
- Metadados:  http://localhost:8000/odata/$metadata.json

---

## Endpoints OData

### Leitura

```
GET /odata/Customers
GET /odata/Customers?$filter=Country eq 'Mexico'
GET /odata/Customers?$filter=contains(CompanyName,'Tech')
GET /odata/Customers?$filter=UnitPrice gt 20          # filtro numérico
GET /odata/Customers?$orderby=CompanyName asc
GET /odata/Customers?$top=10&$skip=20
GET /odata/Customers?$count=true
GET /odata/Customers?$select=CustomerID,CompanyName
GET /odata/Customers('ALFKI')
```

### Escrita

```
POST   /odata/Customers          — criar registro
PUT    /odata/Customers('ALFKI') — substituir completamente
PATCH  /odata/Customers('ALFKI') — atualizar parcialmente
DELETE /odata/Customers('ALFKI') — remover
```

---

## Executar os Testes

```bash
pytest -v
# ou com cobertura
pytest --cov=. --cov-report=term-missing
```

Os testes usam banco **SQLite em memória** — completamente isolado
do banco de desenvolvimento. Nenhum dado de dev é alterado.

### Log de Execução dos Testes

Abaixo está um exemplo completo da execução dos testes após a correta configuração do ambiente. Todos os **91 testes** foram aprovados.

```
========================================================================= test session starts ==========================================================================
platform win32 -- Python 3.13.4, pytest-9.0.3, pluggy-1.6.0 -- C:\...\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\...\DemoAnotation
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.13.0, cov-7.1.0
collected 91 items                                                                                                                                                      

tests/test_metadata.py::TestMetadataXML::test_metadata_xml_retorna_200 PASSED                                                                                     [  1%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_content_type PASSED                                                                                    [  2%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_contem_entity_types PASSED                                                                             [  3%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_contem_anotacoes_listview PASSED                                                                       [  4%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_contem_anotacoes_fieldgroup PASSED                                                                     [  5%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_contem_label PASSED                                                                                    [  6%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_contem_max_length PASSED                                                                               [  7%]
tests/test_metadata.py::TestMetadataXML::test_metadata_xml_edmx_namespace PASSED                                                                                  [  8%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_retorna_200 PASSED                                                                                   [  9%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_estrutura_raiz PASSED                                                                                [ 10%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_contem_todas_entidades PASSED                                                                        [ 12%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_entidade_tem_label PASSED                                                                            [ 13%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_entidade_tem_properties PASSED                                                                       [ 14%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_entidade_tem_listview PASSED                                                                         [ 15%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_listview_tem_default_sort PASSED                                                                     [ 16%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_entidade_tem_fieldgroups PASSED                                                                      [ 17%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_entidade_tem_validacoes PASSED                                                                       [ 18%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_validacao_required PASSED                                                                            [ 19%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_max_length_valor PASSED                                                                              [ 20%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_sortable_flag PASSED                                                                                 [ 21%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_filterable_flag PASSED                                                                               [ 23%]
tests/test_metadata.py::TestMetadataJSON::test_metadata_json_property_type_mapping PASSED                                                                         [ 24%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_list_entities PASSED                                                                                 [ 25%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_label PASSED                                                                      [ 26%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_entity_name PASSED                                                                [ 27%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_list_view PASSED                                                                  [ 28%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_column_labels PASSED                                                              [ 29%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_default_sort PASSED                                                               [ 30%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_form_groups PASSED                                                                [ 31%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_validations PASSED                                                                [ 32%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_to_ui_config_structure PASSED                                                                        [ 34%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_get_ui_annotations_produto PASSED                                                                    [ 35%]
tests/test_metadata.py::TestAnnotationParserViaCliente::test_entidade_inexistente_retorna_objeto_vazio PASSED                                                     [ 36%]
tests/test_read.py::TestListagem::test_listar_clientes_retorna_200 PASSED                                                                                         [ 37%]
tests/test_read.py::TestListagem::test_listar_clientes_tem_value PASSED                                                                                           [ 38%]
tests/test_read.py::TestListagem::test_listar_clientes_tem_odata_context PASSED                                                                                   [ 39%]
tests/test_read.py::TestListagem::test_listar_retorna_registros_mock PASSED                                                                                       [ 40%]
tests/test_read.py::TestListagem::test_listar_produtos PASSED                                                                                                     [ 41%]
tests/test_read.py::TestListagem::test_listar_pedidos PASSED                                                                                                      [ 42%]
tests/test_read.py::TestListagem::test_entidade_inexistente_retorna_404 PASSED                                                                                    [ 43%]
tests/test_read.py::TestListagem::test_campos_esperados_no_cliente PASSED                                                                                         [ 45%]
tests/test_read.py::TestFiltro::test_filter_por_pais_mexico PASSED                                                                                                [ 46%]
tests/test_read.py::TestFiltro::test_filter_por_pais_germany PASSED                                                                                               [ 47%]
tests/test_read.py::TestFiltro::test_filter_ne_exclui_pais PASSED                                                                                                 [ 48%]
tests/test_read.py::TestFiltro::test_filter_contains PASSED                                                                                                       [ 49%]
tests/test_read.py::TestFiltro::test_filter_numerico_gt PASSED                                                                                                    [ 50%]
tests/test_read.py::TestFiltro::test_filter_numerico_lt PASSED                                                                                                    [ 51%]
tests/test_read.py::TestFiltro::test_filter_numerico_le PASSED                                                                                                    [ 52%]
tests/test_read.py::TestOrdenacao::test_orderby_asc PASSED                                                                                                        [ 53%]
tests/test_read.py::TestOrdenacao::test_orderby_desc PASSED                                                                                                       [ 54%]
tests/test_read.py::TestOrdenacao::test_orderby_numerico PASSED                                                                                                   [ 56%]
tests/test_read.py::TestPaginacao::test_top_limita_resultados PASSED                                                                                              [ 57%]
tests/test_read.py::TestPaginacao::test_top_zero_retorna_vazio PASSED                                                                                             [ 58%]
tests/test_read.py::TestPaginacao::test_skip_pula_registros PASSED                                                                                                [ 59%]
tests/test_read.py::TestPaginacao::test_paginacao_combinada PASSED                                                                                                [ 60%]
tests/test_read.py::TestPaginacao::test_count_true_retorna_total PASSED                                                                                           [ 61%]
tests/test_read.py::TestPaginacao::test_count_false_nao_retorna_total PASSED                                                                                      [ 62%]
tests/test_read.py::TestPaginacao::test_count_sem_parametro_nao_retorna_total PASSED                                                                              [ 63%]
tests/test_read.py::TestPaginacao::test_count_total_independe_de_top PASSED                                                                                       [ 64%]
tests/test_read.py::TestSelect::test_select_dois_campos PASSED                                                                                                    [ 65%]
tests/test_read.py::TestSelect::test_select_campo_unico PASSED                                                                                                    [ 67%]
tests/test_read.py::TestBuscarPorChave::test_buscar_cliente_por_chave PASSED                                                                                      [ 68%]
tests/test_read.py::TestBuscarPorChave::test_buscar_produto_por_id_inteiro PASSED                                                                                 [ 69%]
tests/test_read.py::TestBuscarPorChave::test_buscar_chave_inexistente_retorna_404 PASSED                                                                          [ 70%]
tests/test_read.py::TestViaS2MOdataPy::test_get_retorna_value PASSED                                                                                              [ 71%]
tests/test_read.py::TestViaS2MOdataPy::test_filter_via_builder PASSED                                                                                             [ 72%]
tests/test_read.py::TestViaS2MOdataPy::test_select_via_builder PASSED                                                                                             [ 73%]
tests/test_read.py::TestViaS2MOdataPy::test_orderby_via_builder PASSED                                                                                            [ 74%]
tests/test_read.py::TestViaS2MOdataPy::test_top_skip_via_builder PASSED                                                                                           [ 75%]
tests/test_read.py::TestViaS2MOdataPy::test_count_via_builder PASSED                                                                                              [ 76%]
tests/test_read.py::TestViaS2MOdataPy::test_count_total_correto PASSED                                                                                            [ 78%]
tests/test_read.py::TestViaS2MOdataPy::test_page_helper PASSED                                                                                                    [ 79%]
tests/test_read.py::TestViaS2MOdataPy::test_first_retorna_registro PASSED                                                                                         [ 80%]
tests/test_read.py::TestViaS2MOdataPy::test_produtos_filtro_numerico PASSED                                                                                       [ 81%]
tests/test_write.py::TestCriar::test_criar_cliente_retorna_201 PASSED                                                                                             [ 82%]
tests/test_write.py::TestCriar::test_criar_cliente_retorna_dados PASSED                                                                                           [ 83%]
tests/test_write.py::TestCriar::test_criar_produto PASSED                                                                                                         [ 84%]
tests/test_write.py::TestCriar::test_criar_pedido PASSED                                                                                                          [ 85%]
tests/test_write.py::TestCriar::test_criar_via_s2modatapy PASSED                                                                                                  [ 86%]
tests/test_write.py::TestAtualizar::test_put_substitui_registro PASSED                                                                                            [ 87%]
tests/test_write.py::TestAtualizar::test_put_chave_inexistente_retorna_404 PASSED                                                                                 [ 89%]
tests/test_write.py::TestAtualizar::test_put_via_s2modatapy PASSED                                                                                                [ 90%]
tests/test_write.py::TestAtualizarParcial::test_patch_altera_apenas_campos_enviados PASSED                                                                        [ 91%]
tests/test_write.py::TestAtualizarParcial::test_patch_chave_inexistente_retorna_404 PASSED                                                                        [ 92%]
tests/test_write.py::TestAtualizarParcial::test_patch_via_s2modatapy PASSED                                                                                       [ 93%]
tests/test_write.py::TestDeletar::test_delete_retorna_204 PASSED                                                                                                  [ 94%]
tests/test_write.py::TestDeletar::test_delete_remove_registro PASSED                                                                                              [ 95%]
tests/test_write.py::TestDeletar::test_delete_chave_inexistente_retorna_404 PASSED                                                                                [ 96%]
tests/test_write.py::TestDeletar::test_delete_via_s2modatapy PASSED                                                                                               [ 97%]
tests/test_write.py::TestFluxoCompleto::test_ciclo_completo_cliente PASSED                                                                                        [ 98%]
tests/test_write.py::TestFluxoCompleto::test_ciclo_produto_inteiro_pk PASSED                                                                                      [100%]

=========================================================================== warnings summary ===========================================================================
tests/test_metadata.py: 11 warnings
tests/test_read.py: 11 warnings
tests/test_write.py: 11 warnings
  C:\...\starlette\testclient.py:439: DeprecationWarning: You should not use the 'timeout' argument with the TestClient. See https://github.com/Kludex/starlette/issues/1108 for more information.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================================================== 91 passed, 33 warnings in 2.05s ====================================================================
```

---

## Estrutura de Pastas

```
DemoAnotation/
├── main.py                    ← entry point FastAPI
├── database.py                ← SQLAlchemy engine + Base + get_db
├── mock_data.py               ← dados de exemplo (carregados em dev)
├── requirements.txt
├── pytest.ini
├── .env                       ← configuração de ambiente
├── models/
│   ├── __init__.py
│   ├── customer.py            ← modelo Customer com anotações
│   ├── order.py               ← modelo Order
│   └── product.py             ← modelo Product
├── annotations/
│   ├── __init__.py
│   ├── decorators.py          ← UI, Common, Validation decorators
│   └── metadata_builder.py   ← gera XML e JSON de metadados
├── odata/
│   ├── __init__.py
│   ├── endpoint.py            ← router FastAPI com CRUD completo
│   └── query_parser.py        ← aplica $filter, $orderby, $top, $skip
└── tests/
    ├── __init__.py
    ├── conftest.py            ← fixtures (TestClient + S2MOdataPy)
    ├── test_read.py           ← testes de leitura e filtros
    ├── test_write.py          ← testes de CRUD
    └── test_metadata.py       ← testes de metadados e anotações
```

---

## Observações

- Os **warnings** exibidos referem‑se a uma depreciação no `TestClient` do Starlette (não impactam a funcionalidade do servidor ou da biblioteca) e são esperados.
- O projeto serve como referência viva para desenvolvedores que desejam entender como construir serviços OData ricos em anotações e como testá‑los.

---

## Licença

MIT License with Attribution — Christopher N. S. M. Mauricio.
```