"""
Testes de metadados — $metadata (XML), $metadata.json e anotações de UI

Verifica que o servidor gera metadados corretos e que o cliente
S2MOdataPy consegue interpretá-los via ODataAnnotationParser.

Author: Christopher N. S. M. Mauricio
"""

import pytest


class TestMetadataXML:
    """Testes do endpoint /$metadata em formato XML."""

    def test_metadata_xml_retorna_200(self, http_client):
        resp = http_client.get("/odata/$metadata")
        assert resp.status_code == 200

    def test_metadata_xml_content_type(self, http_client):
        resp = http_client.get("/odata/$metadata")
        assert "xml" in resp.headers.get("content-type", "").lower()

    def test_metadata_xml_contem_entity_types(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "Customer"  in xml
        assert "Order"     in xml
        assert "Product"   in xml

    def test_metadata_xml_contem_anotacoes_listview(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "ui.LineItem" in xml

    def test_metadata_xml_contem_anotacoes_fieldgroup(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "ui.FieldGroup" in xml

    def test_metadata_xml_contem_label(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "common.Label" in xml
        assert "Clientes"     in xml

    def test_metadata_xml_contem_max_length(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "MaxLength" in xml

    def test_metadata_xml_edmx_namespace(self, http_client):
        resp = http_client.get("/odata/$metadata")
        xml = resp.text
        assert "edmx:Edmx" in xml
        assert 'Version="4.0"' in xml


class TestMetadataJSON:
    """Testes do endpoint /$metadata.json em formato JSON enriquecido."""

    def test_metadata_json_retorna_200(self, http_client):
        resp = http_client.get("/odata/$metadata.json")
        assert resp.status_code == 200

    def test_metadata_json_estrutura_raiz(self, http_client):
        data = http_client.get("/odata/$metadata.json").json()
        assert "version"    in data
        assert "namespace"  in data
        assert "entities"   in data
        assert data["version"] == "4.0"

    def test_metadata_json_contem_todas_entidades(self, http_client):
        data  = http_client.get("/odata/$metadata.json").json()
        nomes = [e["name"] for e in data["entities"]]
        assert "Customer" in nomes
        assert "Order"    in nomes
        assert "Product"  in nomes

    def test_metadata_json_entidade_tem_label(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        assert cliente["label"] == "Clientes"

    def test_metadata_json_entidade_tem_properties(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        assert len(cliente["properties"]) > 0
        nomes_props = [p["name"] for p in cliente["properties"]]
        assert "CustomerID"   in nomes_props
        assert "CompanyName"  in nomes_props
        assert "Country"      in nomes_props

    def test_metadata_json_entidade_tem_listview(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        assert "ui"       in cliente
        assert "listView" in cliente["ui"]
        assert "columns"  in cliente["ui"]["listView"]
        assert len(cliente["ui"]["listView"]["columns"]) > 0

    def test_metadata_json_listview_tem_default_sort(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        assert cliente["ui"]["listView"]["default_sort"] == "CompanyName asc"

    def test_metadata_json_entidade_tem_fieldgroups(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        grupos  = cliente["ui"]["fieldGroups"]
        assert len(grupos) >= 2
        nomes_grupos = [g["name"] for g in grupos]
        assert "BasicInfo" in nomes_grupos
        assert "Address"   in nomes_grupos

    def test_metadata_json_entidade_tem_validacoes(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        assert "validations" in cliente
        assert "CustomerID"  in cliente["validations"]
        assert "CompanyName" in cliente["validations"]

    def test_metadata_json_validacao_required(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        regras  = cliente["validations"]["CustomerID"]
        tipos   = [r["type"] for r in regras]
        assert "required"   in tipos
        assert "max_length" in tipos

    def test_metadata_json_max_length_valor(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        regras  = cliente["validations"]["CustomerID"]
        ml_rule = next(r for r in regras if r["type"] == "max_length")
        assert ml_rule["max"] == 5

    def test_metadata_json_sortable_flag(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        colunas = cliente["ui"]["listView"]["columns"]
        empresa = next(c for c in colunas if c["name"] == "CompanyName")
        assert empresa["sortable"] is True

    def test_metadata_json_filterable_flag(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        cliente = next(e for e in data["entities"] if e["name"] == "Customer")
        colunas = cliente["ui"]["listView"]["columns"]
        pais    = next(c for c in colunas if c["name"] == "Country")
        assert pais["filterable"] is True

    def test_metadata_json_property_type_mapping(self, http_client):
        data    = http_client.get("/odata/$metadata.json").json()
        produto = next(e for e in data["entities"] if e["name"] == "Product")
        props   = {p["name"]: p for p in produto["properties"]}
        assert props["UnitPrice"]["type"]    == "Edm.Double"
        assert props["UnitsInStock"]["type"] == "Edm.Int32"
        assert props["ProductName"]["type"]  == "Edm.String"


class TestAnnotationParserViaCliente:
    """Testes do ODataAnnotationParser consumindo o servidor via S2MOdataPy."""

    def test_list_entities(self, odata_client):
        entidades = odata_client.list_entities()
        assert "Customer" in entidades
        assert "Order"    in entidades
        assert "Product"  in entidades

    def test_get_ui_annotations_label(self, odata_client):
        ann = odata_client.get_ui_annotations("Customer")
        assert ann.label == "Clientes"

    def test_get_ui_annotations_entity_name(self, odata_client):
        ann = odata_client.get_ui_annotations("Customer")
        assert ann.entity_name == "Customer"

    def test_get_ui_annotations_list_view(self, odata_client):
        ann = odata_client.get_ui_annotations("Customer")
        assert ann.list_view is not None
        assert len(ann.list_view.columns) > 0

    def test_get_ui_annotations_column_labels(self, odata_client):
        ann     = odata_client.get_ui_annotations("Customer")
        colunas = {c.name: c for c in ann.list_view.columns}
        assert "CustomerID"  in colunas
        assert "CompanyName" in colunas
        assert colunas["CustomerID"].label   == "Código"
        assert colunas["CompanyName"].label  == "Empresa"

    def test_get_ui_annotations_default_sort(self, odata_client):
        ann = odata_client.get_ui_annotations("Customer")
        assert ann.list_view.default_sort == "CompanyName asc"

    def test_get_ui_annotations_form_groups(self, odata_client):
        ann    = odata_client.get_ui_annotations("Customer")
        assert ann.form is not None
        grupos = {g.name: g for g in ann.form.groups}
        assert "BasicInfo" in grupos
        assert "Address"   in grupos
        assert grupos["BasicInfo"].label == "Informações Básicas"
        assert grupos["Address"].label   == "Endereço"

    def test_get_ui_annotations_validations(self, odata_client):
        ann   = odata_client.get_ui_annotations("Customer")
        assert "CustomerID"  in ann.validations
        assert "CompanyName" in ann.validations
        tipos = [r["type"] for r in ann.validations["CustomerID"]]
        assert "required"   in tipos
        assert "max_length" in tipos

    def test_to_ui_config_structure(self, odata_client):
        from s2modatapy.parsers.annotations import ODataAnnotationParser
        metadata = odata_client.get_metadata_json()
        parser   = ODataAnnotationParser.from_dict(metadata)
        config   = parser.to_ui_config("Customer")
        assert "entity"   in config
        assert "label"    in config
        assert "listView" in config
        assert "form"     in config
        assert "columns"  in config["listView"]
        assert "groups"   in config["form"]

    def test_get_ui_annotations_produto(self, odata_client):
        ann = odata_client.get_ui_annotations("Product")
        assert ann.label == "Produtos"
        assert ann.list_view is not None
        colunas = {c.name: c for c in ann.list_view.columns}
        assert "ProductName" in colunas
        assert "UnitPrice"   in colunas

    def test_entidade_inexistente_retorna_objeto_vazio(self, odata_client):
        ann = odata_client.get_ui_annotations("EntidadeInexistente")
        assert ann.entity_name == "EntidadeInexistente"
        assert ann.list_view   is None
        assert ann.form        is None
