"""
Testes de escrita — POST, PUT, PATCH, DELETE

Utiliza o cliente S2MOdataPy e chamadas diretas ao TestClient
para verificar todas as operações de escrita do servidor OData.

Author: Christopher N. S. M. Mauricio
"""

import pytest


class TestCriar:
    """Testes de POST — criação de registros."""

    def test_criar_cliente_retorna_201(self, http_client):
        payload = {
            "CustomerID": "TSTCR",
            "CompanyName": "Empresa Criação Teste",
            "ContactName": "Criador",
            "Country": "Brazil",
        }
        resp = http_client.post("/odata/Customers", json=payload)
        assert resp.status_code == 201

    def test_criar_cliente_retorna_dados(self, http_client):
        payload = {
            "CustomerID": "TSTDT",
            "CompanyName": "Empresa Dados Teste",
            "Country": "Brazil",
        }
        resp = http_client.post("/odata/Customers", json=payload)
        data = resp.json()
        assert data["CustomerID"] == "TSTDT"
        assert data["CompanyName"] == "Empresa Dados Teste"
        assert data["Country"] == "Brazil"

    def test_criar_produto(self, http_client):
        payload = {
            "ProductName": "Produto Teste",
            "Category": "Test Category",
            "UnitPrice": 99.90,
            "UnitsInStock": 50,
        }
        resp = http_client.post("/odata/Products", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["ProductName"] == "Produto Teste"
        assert data["UnitPrice"] == 99.90

    def test_criar_pedido(self, http_client):
        payload = {
            "CustomerID": "ALFKI",
            "OrderDate": "2024-05-01",
            "Freight": 25.00,
            "ShipCountry": "Germany",
        }
        resp = http_client.post("/odata/Orders", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["CustomerID"] == "ALFKI"

    def test_criar_via_s2modatapy(self, odata_client):
        payload = {
            "CustomerID": "TSTPY",
            "CompanyName": "Empresa via S2MOdataPy",
            "Country": "Brazil",
        }
        resultado = odata_client.entity("Customers").create(payload)
        assert resultado["CustomerID"] == "TSTPY"
        assert resultado["CompanyName"] == "Empresa via S2MOdataPy"


class TestAtualizar:
    """Testes de PUT — substituição completa."""

    def _ensure_customer(self, http_client, customer_id="TPUTX"):
        """Cria o cliente se não existir."""
        if http_client.get(f"/odata/Customers('{customer_id}')").status_code == 404:
            http_client.post(
                "/odata/Customers",
                json={
                    "CustomerID": customer_id,
                    "CompanyName": "Empresa Original",
                    "Country": "Brazil",
                },
            )

    def test_put_substitui_registro(self, http_client):
        self._ensure_customer(http_client, "TPUTX")
        payload = {
            "CompanyName": "Empresa Substituída",
            "Country": "Argentina",
        }
        resp = http_client.put("/odata/Customers('TPUTX')", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["CompanyName"] == "Empresa Substituída"
        assert data["Country"] == "Argentina"

    def test_put_chave_inexistente_retorna_404(self, http_client):
        resp = http_client.put("/odata/Customers('XXXXX')", json={"CompanyName": "X"})
        assert resp.status_code == 404

    def test_put_via_s2modatapy(self, http_client, odata_client):
        # Garante que o registro existe
        http_client.post(
            "/odata/Customers",
            json={
                "CustomerID": "TPTSP",
                "CompanyName": "Original",
                "Country": "Brazil",
            },
        )
        odata_client.entity("Customers").update(
            "TPTSP",
            {
                "CompanyName": "Atualizado via S2MOdataPy",
                "Country": "Chile",
            },
        )
        # Lê o estado atual via http diretamente (update pode retornar 204)
        resultado = http_client.get("/odata/Customers('TPTSP')").json()
        assert resultado.get("CompanyName") == "Atualizado via S2MOdataPy"
        assert resultado.get("Country") == "Chile"


class TestAtualizarParcial:
    """Testes de PATCH — atualização parcial."""

    def _ensure_customer(self, http_client, customer_id="TPCHX"):
        if http_client.get(f"/odata/Customers('{customer_id}')").status_code == 404:
            http_client.post(
                "/odata/Customers",
                json={
                    "CustomerID": customer_id,
                    "CompanyName": "Empresa Patch Teste",
                    "ContactName": "Contato Original",
                    "Country": "Brazil",
                },
            )

    def test_patch_altera_apenas_campos_enviados(self, http_client):
        self._ensure_customer(http_client, "TPCHX")
        resp = http_client.patch(
            "/odata/Customers('TPCHX')", json={"ContactName": "Contato Atualizado"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ContactName"] == "Contato Atualizado"
        assert data["CompanyName"] == "Empresa Patch Teste"  # campo não enviado permanece

    def test_patch_chave_inexistente_retorna_404(self, http_client):
        resp = http_client.patch("/odata/Customers('XXXXX')", json={"ContactName": "X"})
        assert resp.status_code == 404

    def test_patch_via_s2modatapy(self, http_client, odata_client):
        http_client.post(
            "/odata/Customers",
            json={
                "CustomerID": "TPSPY",
                "CompanyName": "Empresa Patch",
                "ContactName": "Original",
                "Country": "Brazil",
            },
        )
        odata_client.entity("Customers").patch("TPSPY", {"ContactName": "Patchado"})
        resultado = http_client.get("/odata/Customers('TPSPY')").json()
        assert resultado.get("ContactName") == "Patchado"
        assert resultado.get("CompanyName") == "Empresa Patch"  # não alterado


class TestDeletar:
    """Testes de DELETE — remoção de registros."""

    def _create_temp(self, http_client, customer_id, company="Empresa Temp"):
        http_client.post(
            "/odata/Customers",
            json={
                "CustomerID": customer_id,
                "CompanyName": company,
                "Country": "Brazil",
            },
        )

    def test_delete_retorna_204(self, http_client):
        self._create_temp(http_client, "TDEL1")
        resp = http_client.delete("/odata/Customers('TDEL1')")
        assert resp.status_code == 204

    def test_delete_remove_registro(self, http_client):
        self._create_temp(http_client, "TDEL2")
        http_client.delete("/odata/Customers('TDEL2')")
        resp = http_client.get("/odata/Customers('TDEL2')")
        assert resp.status_code == 404

    def test_delete_chave_inexistente_retorna_404(self, http_client):
        resp = http_client.delete("/odata/Customers('XXXXX')")
        assert resp.status_code == 404

    def test_delete_via_s2modatapy(self, http_client, odata_client):
        self._create_temp(http_client, "TDELP")
        resultado = odata_client.entity("Customers").delete("TDELP")
        assert resultado is True
        resp = http_client.get("/odata/Customers('TDELP')")
        assert resp.status_code == 404


class TestFluxoCompleto:
    """Testa o ciclo completo de CRUD em uma única entidade."""

    def test_ciclo_completo_cliente(self, odata_client, http_client):
        """Cria → lê → atualiza parcialmente → deleta um cliente."""
        customer_id = "CYCLO"

        # Cria
        criado = odata_client.entity("Customers").create(
            {
                "CustomerID": customer_id,
                "CompanyName": "Ciclo Completo Ltda",
                "Country": "Brazil",
            }
        )
        assert criado["CustomerID"] == customer_id

        # Lê via http direto
        resp = http_client.get(f"/odata/Customers('{customer_id}')")
        assert resp.status_code == 200
        assert resp.json()["CompanyName"] == "Ciclo Completo Ltda"

        # Atualiza parcialmente
        odata_client.entity("Customers").patch(customer_id, {"CompanyName": "Ciclo Completo S.A."})
        resp = http_client.get(f"/odata/Customers('{customer_id}')")
        assert resp.json()["CompanyName"] == "Ciclo Completo S.A."
        assert resp.json()["Country"] == "Brazil"  # campo não alterado

        # Substitui completamente
        odata_client.entity("Customers").update(
            customer_id,
            {
                "CompanyName": "Ciclo Final",
                "Country": "Argentina",
            },
        )
        resp = http_client.get(f"/odata/Customers('{customer_id}')")
        assert resp.json()["CompanyName"] == "Ciclo Final"
        assert resp.json()["Country"] == "Argentina"

        # Deleta
        odata_client.entity("Customers").delete(customer_id)
        resp = http_client.get(f"/odata/Customers('{customer_id}')")
        assert resp.status_code == 404

    def test_ciclo_produto_inteiro_pk(self, odata_client, http_client):
        """Cria → atualiza → deleta produto com PK inteira."""
        criado = odata_client.entity("Products").create(
            {
                "ProductName": "Produto Ciclo",
                "UnitPrice": 15.00,
            }
        )
        product_id = criado["ProductID"]
        assert product_id is not None

        # Patch
        odata_client.entity("Products").patch(product_id, {"UnitPrice": 25.00})
        resp = http_client.get(f"/odata/Products({product_id})")
        assert resp.json().get("UnitPrice") == 25.00

        # Delete
        odata_client.entity("Products").delete(product_id)
        resp = http_client.get(f"/odata/Products({product_id})")
        assert resp.status_code == 404
