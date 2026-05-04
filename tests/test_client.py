"""
Testes para S2MOdataPy

Cobre: S2MClient, ODataQueryBuilder, ODataAnnotationParser e exceções.

Author: Christopher N. S. M. Mauricio
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from s2modatapy import (
    S2MClient,
    S2MODataError,
    S2MODataConnectionError,
    S2MODataNotFoundError,
    S2MODataAuthenticationError,
    ODataAnnotationParser,
    UIAnnotations,
    UIListView,
    UIForm,
    UIField,
    FieldType,
)
from s2modatapy.query_builder import ODataQueryBuilder


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return S2MClient("http://localhost:8000/odata/")


@pytest.fixture
def mock_response_customers():
    return {
        "@odata.context": "http://localhost:8000/odata/$metadata#Customers",
        "@odata.count": 91,
        "value": [
            {"CustomerID": "ALFKI", "CompanyName": "Alfreds Futterkiste", "Country": "Germany"},
            {"CustomerID": "ANATR", "CompanyName": "Ana Trujillo", "Country": "Mexico"},
        ],
    }


@pytest.fixture
def mock_metadata_json():
    return {
        "version": "4.0",
        "namespace": "S2MOdataPyDemo",
        "entities": [
            {
                "name": "Customer",
                "label": "Clientes",
                "properties": [
                    {"name": "CustomerID", "type": "Edm.String", "nullable": False, "maxLength": 5},
                    {"name": "CompanyName", "type": "Edm.String", "nullable": False, "maxLength": 80},
                    {"name": "Country", "type": "Edm.String", "nullable": True},
                ],
                "ui": {
                    "listView": {
                        "columns": [
                            {"name": "CustomerID", "label": "Código", "sortable": False, "filterable": False},
                            {"name": "CompanyName", "label": "Empresa", "sortable": True, "filterable": False},
                            {"name": "Country", "label": "País", "filterable": True},
                        ],
                        "default_sort": "CompanyName asc",
                    },
                    "fieldGroups": [
                        {
                            "name": "BasicInfo",
                            "label": "Informações Básicas",
                            "fields": ["CustomerID", "CompanyName"],
                        }
                    ],
                },
                "validations": {
                    "CustomerID": [
                        {"type": "required", "message": "Campo obrigatório"},
                        {"type": "max_length", "max": 5, "message": "Máximo 5 caracteres"},
                    ],
                    "CompanyName": [
                        {"type": "required", "message": "Campo obrigatório"},
                    ],
                },
            }
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Testes — S2MClient inicialização
# ─────────────────────────────────────────────────────────────────────────────

class TestS2MClientInit:
    def test_base_url_trailing_slash_removed(self):
        c = S2MClient("http://localhost:8000/odata/")
        assert c.base_url == "http://localhost:8000/odata"

    def test_default_accept_header(self):
        c = S2MClient("http://localhost:8000/odata/")
        assert c.session.headers["Accept"] == "application/json"

    def test_basic_auth_set(self):
        c = S2MClient("http://localhost:8000/odata/", auth=("user", "pass"))
        assert c.session.auth == ("user", "pass")

    def test_bearer_token_header(self):
        c = S2MClient("http://localhost:8000/odata/", bearer_token="mytoken123")
        assert "Authorization" in c.session.headers
        assert c.session.headers["Authorization"] == "Bearer mytoken123"

    def test_debug_flag_stored(self):
        c = S2MClient("http://localhost:8000/odata/", debug=True)
        assert c.debug is True

    def test_timeout_stored(self):
        c = S2MClient("http://localhost:8000/odata/", timeout=60)
        assert c.timeout == 60


# ─────────────────────────────────────────────────────────────────────────────
# Testes — ODataQueryBuilder (leitura)
# ─────────────────────────────────────────────────────────────────────────────

class TestQueryBuilderRead:
    def test_entity_returns_builder(self, client):
        builder = client.entity("Customers")
        assert isinstance(builder, ODataQueryBuilder)
        assert builder.entity_name == "Customers"

    def test_select_single_field(self, client):
        builder = client.entity("Customers").select("CustomerID")
        assert builder.params["$select"] == "CustomerID"

    def test_select_multiple_fields(self, client):
        builder = client.entity("Customers").select("CustomerID", "CompanyName", "Country")
        assert builder.params["$select"] == "CustomerID,CompanyName,Country"

    def test_filter_string(self, client):
        builder = client.entity("Customers").filter("Country eq 'Brazil'")
        assert builder.params["$filter"] == "Country eq 'Brazil'"

    def test_orderby_asc_default(self, client):
        builder = client.entity("Customers").orderby("CompanyName")
        assert builder.params["$orderby"] == "CompanyName asc"

    def test_orderby_desc(self, client):
        builder = client.entity("Customers").orderby("CompanyName", "desc")
        assert builder.params["$orderby"] == "CompanyName desc"

    def test_orderby_invalid_direction_defaults_to_asc(self, client):
        builder = client.entity("Customers").orderby("CompanyName", "invalid")
        assert builder.params["$orderby"] == "CompanyName asc"

    def test_orderby_multi(self, client):
        builder = client.entity("Customers").orderby_multi("Country asc", "CompanyName desc")
        assert builder.params["$orderby"] == "Country asc,CompanyName desc"

    def test_top(self, client):
        builder = client.entity("Customers").top(10)
        assert builder.params["$top"] == 10

    def test_top_zero_allowed(self, client):
        builder = client.entity("Customers").top(0)
        assert builder.params["$top"] == 0

    def test_top_negative_ignored(self, client):
        builder = client.entity("Customers").top(-1)
        assert "$top" not in builder.params

    def test_skip(self, client):
        builder = client.entity("Customers").skip(20)
        assert builder.params["$skip"] == 20

    def test_expand(self, client):
        builder = client.entity("Orders").expand("Customer", "OrderDetails")
        assert builder.params["$expand"] == "Customer,OrderDetails"

    def test_count(self, client):
        builder = client.entity("Customers").count()
        assert builder.params["$count"] == "true"

    def test_chaining(self, client):
        builder = (
            client.entity("Customers")
            .select("CustomerID", "CompanyName")
            .filter("Country eq 'Brazil'")
            .orderby("CompanyName")
            .top(5)
            .skip(10)
            .count()
        )
        assert builder.params["$select"] == "CustomerID,CompanyName"
        assert builder.params["$filter"] == "Country eq 'Brazil'"
        assert builder.params["$orderby"] == "CompanyName asc"
        assert builder.params["$top"] == 5
        assert builder.params["$skip"] == 10
        assert builder.params["$count"] == "true"


# ─────────────────────────────────────────────────────────────────────────────
# Testes — ODataQueryBuilder (escrita — chave)
# ─────────────────────────────────────────────────────────────────────────────

class TestQueryBuilderKeyEndpoint:
    def test_string_key_quoted(self, client):
        builder = client.entity("Customers")
        assert builder._build_key_endpoint("ALFKI") == "Customers('ALFKI')"

    def test_integer_key_unquoted(self, client):
        builder = client.entity("Orders")
        assert builder._build_key_endpoint(1) == "Orders(1)"


# ─────────────────────────────────────────────────────────────────────────────
# Testes — ODataQueryBuilder (execução via mock)
# ─────────────────────────────────────────────────────────────────────────────

class TestQueryBuilderExecution:
    def test_get_calls_request(self, client, mock_response_customers):
        client._request = MagicMock(return_value=mock_response_customers)
        result = client.entity("Customers").get()
        client._request.assert_called_once_with("GET", "Customers", params={})
        assert result == mock_response_customers

    def test_get_with_params(self, client, mock_response_customers):
        client._request = MagicMock(return_value=mock_response_customers)
        client.entity("Customers").filter("Country eq 'Mexico'").top(5).get()
        _, _, kwargs = client._request.mock_calls[0]
        params = client._request.call_args[1]["params"]
        assert params["$filter"] == "Country eq 'Mexico'"
        assert params["$top"] == 5

    def test_first_returns_first_record(self, client, mock_response_customers):
        client._request = MagicMock(return_value=mock_response_customers)
        result = client.entity("Customers").first()
        assert result["CustomerID"] == "ALFKI"

    def test_first_returns_none_when_empty(self, client):
        client._request = MagicMock(return_value={"value": []})
        result = client.entity("Customers").first()
        assert result is None

    def test_count_only(self, client):
        client._request = MagicMock(return_value={"@odata.count": 91, "value": []})
        total = client.entity("Customers").count_only()
        assert total == 91

    def test_create_calls_post(self, client):
        client._request = MagicMock(return_value={"CustomerID": "BRASI"})
        payload = {"CustomerID": "BRASI", "CompanyName": "Brasil Ltda"}
        client.entity("Customers").create(payload)
        client._request.assert_called_once_with("POST", "Customers", data=payload)

    def test_update_calls_put(self, client):
        client._request = MagicMock(return_value={})
        payload = {"CompanyName": "Brasil S.A."}
        client.entity("Customers").update("BRASI", payload)
        client._request.assert_called_once_with("PUT", "Customers('BRASI')", data=payload)

    def test_patch_calls_patch(self, client):
        client._request = MagicMock(return_value={})
        client.entity("Customers").patch("BRASI", {"ContactName": "João"})
        client._request.assert_called_once_with("PATCH", "Customers('BRASI')", data={"ContactName": "João"})

    def test_delete_calls_delete(self, client):
        client._request = MagicMock(return_value={})
        result = client.entity("Customers").delete("BRASI")
        client._request.assert_called_once_with("DELETE", "Customers('BRASI')")
        assert result is True

    def test_page_helper(self, client, mock_response_customers):
        client._request = MagicMock(return_value=mock_response_customers)
        client.entity("Customers").page(3, 10)
        params = client._request.call_args[1]["params"]
        assert params["$top"] == 10
        assert params["$skip"] == 20  # (3-1) * 10


# ─────────────────────────────────────────────────────────────────────────────
# Testes — ODataAnnotationParser (JSON)
# ─────────────────────────────────────────────────────────────────────────────

class TestODataAnnotationParserJson:
    def test_from_dict_creates_instance(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        assert parser is not None

    def test_get_all_entities(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        entities = parser.get_all_entities()
        assert "Customer" in entities

    def test_parse_entity_label(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        assert ann.label == "Clientes"

    def test_parse_entity_list_view_columns(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        assert ann.list_view is not None
        assert len(ann.list_view.columns) == 3
        assert ann.list_view.columns[0].name == "CustomerID"
        assert ann.list_view.columns[0].label == "Código"

    def test_parse_entity_sortable_flag(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        empresa_col = next(c for c in ann.list_view.columns if c.name == "CompanyName")
        assert empresa_col.sortable is True

    def test_parse_entity_default_sort(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        assert ann.list_view.default_sort == "CompanyName asc"

    def test_parse_entity_form_groups(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        assert ann.form is not None
        assert len(ann.form.groups) == 1
        assert ann.form.groups[0].label == "Informações Básicas"

    def test_parse_entity_validations(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        assert "CustomerID" in ann.validations
        assert ann.validations["CustomerID"][0]["type"] == "required"

    def test_parse_entity_not_found_returns_empty(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("NonExistentEntity")
        assert ann.entity_name == "NonExistentEntity"
        assert ann.label == "NonExistentEntity"
        assert ann.list_view is None

    def test_to_ui_config_structure(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        config = parser.to_ui_config("Customer")
        assert "entity"   in config
        assert "label"    in config
        assert "listView" in config
        assert "form"     in config
        assert "columns"  in config["listView"]

    def test_field_type_mapping(self, mock_metadata_json):
        parser = ODataAnnotationParser.from_dict(mock_metadata_json)
        ann = parser.parse_entity("Customer")
        col = ann.list_view.columns[0]
        assert col.type == FieldType.TEXT


# ─────────────────────────────────────────────────────────────────────────────
# Testes — Exceções
# ─────────────────────────────────────────────────────────────────────────────

class TestExceptions:
    def test_s2modata_error_message(self):
        err = S2MODataError("erro de teste")
        assert "erro de teste" in str(err)

    def test_s2modata_error_with_details(self):
        err = S2MODataError("erro", details={"status_code": 500})
        assert "500" in str(err)

    def test_connection_error_is_subclass(self):
        assert issubclass(S2MODataConnectionError, S2MODataError)

    def test_not_found_error_is_subclass(self):
        assert issubclass(S2MODataNotFoundError, S2MODataError)

    def test_auth_error_is_subclass(self):
        assert issubclass(S2MODataAuthenticationError, S2MODataError)

    def test_client_raises_auth_error_on_401(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.content = b"Unauthorized"
        with patch.object(client.session, "request", return_value=mock_resp):
            with pytest.raises(S2MODataAuthenticationError):
                client._request("GET", "Customers")

    def test_client_raises_not_found_on_404(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b"Not Found"
        with patch.object(client.session, "request", return_value=mock_resp):
            with pytest.raises(S2MODataNotFoundError):
                client._request("GET", "Customers")

    def test_client_raises_connection_error(self, client):
        import requests as req
        with patch.object(
            client.session, "request",
            side_effect=req.exceptions.ConnectionError("refused")
        ):
            with pytest.raises(S2MODataConnectionError):
                client._request("GET", "Customers")
