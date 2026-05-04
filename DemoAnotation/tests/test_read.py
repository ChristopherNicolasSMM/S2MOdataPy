"""
Testes de leitura — GET, $filter, $orderby, $top, $skip, $select, $count

Utiliza o cliente S2MOdataPy para consumir o servidor OData,
verificando que os parâmetros OData são processados corretamente.

Author: Christopher N. S. M. Mauricio
"""

import pytest


class TestListagem:
    """Testes básicos de listagem de registros."""

    def test_listar_clientes_retorna_200(self, http_client):
        resp = http_client.get("/odata/Customers")
        assert resp.status_code == 200

    def test_listar_clientes_tem_value(self, http_client):
        resp = http_client.get("/odata/Customers")
        data = resp.json()
        assert "value" in data
        assert isinstance(data["value"], list)

    def test_listar_clientes_tem_odata_context(self, http_client):
        resp = http_client.get("/odata/Customers")
        data = resp.json()
        assert "@odata.context" in data

    def test_listar_retorna_registros_mock(self, http_client):
        resp = http_client.get("/odata/Customers")
        data = resp.json()
        assert len(data["value"]) > 0

    def test_listar_produtos(self, http_client):
        resp = http_client.get("/odata/Products")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["value"]) > 0

    def test_listar_pedidos(self, http_client):
        resp = http_client.get("/odata/Orders")
        assert resp.status_code == 200

    def test_entidade_inexistente_retorna_404(self, http_client):
        resp = http_client.get("/odata/Inexistente")
        assert resp.status_code == 404

    def test_campos_esperados_no_cliente(self, http_client):
        resp = http_client.get("/odata/Customers")
        primeiro = resp.json()["value"][0]
        assert "CustomerID"   in primeiro
        assert "CompanyName"  in primeiro
        assert "Country"      in primeiro


class TestFiltro:
    """Testes de $filter."""

    def test_filter_por_pais_mexico(self, http_client):
        resp = http_client.get("/odata/Customers?$filter=Country eq 'Mexico'")
        assert resp.status_code == 200
        data = resp.json()
        for c in data["value"]:
            assert c["Country"] == "Mexico"

    def test_filter_por_pais_germany(self, http_client):
        resp = http_client.get("/odata/Customers?$filter=Country eq 'Germany'")
        data = resp.json()
        for c in data["value"]:
            assert c["Country"] == "Germany"

    def test_filter_ne_exclui_pais(self, http_client):
        resp = http_client.get("/odata/Customers?$filter=Country ne 'Mexico'")
        data = resp.json()
        for c in data["value"]:
            assert c["Country"] != "Mexico"

    def test_filter_contains(self, http_client):
        resp = http_client.get("/odata/Customers?$filter=contains(CompanyName,'Alfreds')")
        data = resp.json()
        assert len(data["value"]) >= 1
        assert any("Alfreds" in c["CompanyName"] for c in data["value"])

    def test_filter_numerico_gt(self, http_client):
        resp = http_client.get("/odata/Products?$filter=UnitPrice gt 20")
        assert resp.status_code == 200
        data = resp.json()
        for p in data["value"]:
            assert p["UnitPrice"] > 20

    def test_filter_numerico_lt(self, http_client):
        resp = http_client.get("/odata/Products?$filter=UnitPrice lt 15")
        data = resp.json()
        for p in data["value"]:
            assert p["UnitPrice"] < 15

    def test_filter_numerico_le(self, http_client):
        resp = http_client.get("/odata/Products?$filter=UnitsInStock le 20")
        data = resp.json()
        for p in data["value"]:
            assert p["UnitsInStock"] <= 20


class TestOrdenacao:
    """Testes de $orderby."""

    def test_orderby_asc(self, http_client):
        resp = http_client.get("/odata/Customers?$orderby=CompanyName asc")
        data = resp.json()["value"]
        nomes = [c["CompanyName"] for c in data]
        assert nomes == sorted(nomes)

    def test_orderby_desc(self, http_client):
        resp = http_client.get("/odata/Customers?$orderby=CompanyName desc")
        data = resp.json()["value"]
        nomes = [c["CompanyName"] for c in data]
        assert nomes == sorted(nomes, reverse=True)

    def test_orderby_numerico(self, http_client):
        resp = http_client.get("/odata/Products?$orderby=UnitPrice desc")
        data = resp.json()["value"]
        precos = [p["UnitPrice"] for p in data]
        assert precos == sorted(precos, reverse=True)


class TestPaginacao:
    """Testes de $top, $skip e $count."""

    def test_top_limita_resultados(self, http_client):
        resp = http_client.get("/odata/Customers?$top=3")
        data = resp.json()
        assert len(data["value"]) <= 3

    def test_top_zero_retorna_vazio(self, http_client):
        resp = http_client.get("/odata/Customers?$top=0")
        data = resp.json()
        assert len(data["value"]) == 0

    def test_skip_pula_registros(self, http_client):
        todos = http_client.get("/odata/Customers?$orderby=CustomerID asc").json()["value"]
        pulados = http_client.get("/odata/Customers?$skip=2&$orderby=CustomerID asc").json()["value"]
        assert todos[2]["CustomerID"] == pulados[0]["CustomerID"]

    def test_paginacao_combinada(self, http_client):
        resp = http_client.get("/odata/Customers?$top=2&$skip=1&$orderby=CustomerID asc")
        data = resp.json()
        assert len(data["value"]) <= 2

    def test_count_true_retorna_total(self, http_client):
        resp = http_client.get("/odata/Customers?$count=true&$top=2")
        data = resp.json()
        assert "@odata.count" in data
        # Total real deve ser >= 2 (temos mais registros do que $top)
        assert data["@odata.count"] >= 2

    def test_count_false_nao_retorna_total(self, http_client):
        resp = http_client.get("/odata/Customers?$count=false")
        data = resp.json()
        assert "@odata.count" not in data

    def test_count_sem_parametro_nao_retorna_total(self, http_client):
        resp = http_client.get("/odata/Customers")
        data = resp.json()
        assert "@odata.count" not in data

    def test_count_total_independe_de_top(self, http_client):
        """@odata.count deve refletir total real, não o tamanho da página."""
        total_resp = http_client.get("/odata/Customers?$count=true")
        total = total_resp.json()["@odata.count"]

        paginado_resp = http_client.get("/odata/Customers?$count=true&$top=1")
        total_paginado = paginado_resp.json()["@odata.count"]
        registros_pagina = len(paginado_resp.json()["value"])

        assert total == total_paginado  # O count é o total real
        assert registros_pagina == 1    # Mas só retornou 1 registro


class TestSelect:
    """Testes de $select."""

    def test_select_dois_campos(self, http_client):
        resp = http_client.get("/odata/Customers?$select=CustomerID,CompanyName")
        data = resp.json()
        for item in data["value"]:
            assert set(item.keys()) == {"CustomerID", "CompanyName"}

    def test_select_campo_unico(self, http_client):
        resp = http_client.get("/odata/Customers?$select=Country")
        data = resp.json()
        for item in data["value"]:
            assert "Country" in item


class TestBuscarPorChave:
    """Testes de GET /odata/{entity}({key})."""

    def test_buscar_cliente_por_chave(self, http_client):
        resp = http_client.get("/odata/Customers('ALFKI')")
        assert resp.status_code == 200
        data = resp.json()
        assert data["CustomerID"] == "ALFKI"
        assert data["CompanyName"] == "Alfreds Futterkiste"

    def test_buscar_produto_por_id_inteiro(self, http_client):
        resp = http_client.get("/odata/Products(1)")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ProductID"] == 1

    def test_buscar_chave_inexistente_retorna_404(self, http_client):
        resp = http_client.get("/odata/Customers('XXXXX')")
        assert resp.status_code == 404


class TestViaS2MOdataPy:
    """Testes usando o cliente S2MOdataPy diretamente."""

    def test_get_retorna_value(self, odata_client):
        result = odata_client.entity("Customers").get()
        assert "value" in result
        assert len(result["value"]) > 0

    def test_filter_via_builder(self, odata_client):
        result = (
            odata_client.entity("Customers")
            .filter("Country eq 'Mexico'")
            .get()
        )
        for c in result["value"]:
            assert c["Country"] == "Mexico"

    def test_select_via_builder(self, odata_client):
        result = (
            odata_client.entity("Customers")
            .select("CustomerID", "CompanyName")
            .top(5)
            .get()
        )
        for item in result["value"]:
            assert "CustomerID" in item
            assert "CompanyName" in item
            assert "Country" not in item

    def test_orderby_via_builder(self, odata_client):
        result = (
            odata_client.entity("Customers")
            .orderby("CompanyName", "asc")
            .get()
        )
        nomes = [c["CompanyName"] for c in result["value"]]
        assert nomes == sorted(nomes)

    def test_top_skip_via_builder(self, odata_client):
        result = odata_client.entity("Customers").top(2).skip(0).get()
        assert len(result["value"]) <= 2

    def test_count_via_builder(self, odata_client):
        result = odata_client.entity("Customers").count().top(2).get()
        assert "@odata.count" in result
        assert result["@odata.count"] >= 2

    def test_count_total_correto(self, odata_client):
        total = odata_client.entity("Customers").count_only()
        result_paginado = odata_client.entity("Customers").count().top(2).get()
        assert result_paginado["@odata.count"] == total

    def test_page_helper(self, odata_client):
        result = odata_client.entity("Products").page(1, 5)
        assert len(result["value"]) <= 5

    def test_first_retorna_registro(self, odata_client):
        primeiro = odata_client.entity("Customers").orderby("CustomerID").first()
        assert primeiro is not None
        assert "CustomerID" in primeiro

    def test_produtos_filtro_numerico(self, odata_client):
        result = (
            odata_client.entity("Products")
            .filter("UnitPrice gt 20")
            .get()
        )
        for p in result["value"]:
            assert p["UnitPrice"] > 20
