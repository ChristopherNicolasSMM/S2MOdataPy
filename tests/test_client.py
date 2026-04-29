"""
Testes unitários para o S2MOdataPy
Author: Christopher N. S. M. Mauricio
"""

import pytest
from s2modatapy import S2MClient


class TestS2MClient:
    """Testes do cliente principal"""
    
    def test_client_initialization(self):
        """Teste de inicialização do cliente"""
        client = S2MClient("https://services.odata.org/V4/Northwind/Northwind.svc/")
        assert client.base_url == "https://services.odata.org/V4/Northwind/Northwind.svc"
        assert client.debug == False
        assert client.response_format == "json"
    
    def test_client_with_debug(self):
        """Teste de inicialização com debug"""
        client = S2MClient("https://test.com/", debug=True)
        assert client.debug == True
    
    def test_query_builder_select(self):
        """Teste do método select"""
        client = S2MClient("https://test.com/")
        query = client.entity("Customers").select("ID", "Name")
        assert query.params["$select"] == "ID,Name"
    
    def test_query_builder_filter(self):
        """Teste do método filter"""
        client = S2MClient("https://test.com/")
        query = client.entity("Customers").filter("Country eq 'Brazil'")
        assert query.params["$filter"] == "Country eq 'Brazil'"
    
    def test_query_builder_chaining(self):
        """Teste de encadeamento de métodos"""
        client = S2MClient("https://test.com/")
        query = (client.entity("Products")
                 .select("Name", "Price")
                 .filter("Price gt 100")
                 .top(10)
                 .orderby("Price", "desc"))
        
        assert query.params["$select"] == "Name,Price"
        assert query.params["$filter"] == "Price gt 100"
        assert query.params["$top"] == 10
        assert query.params["$orderby"] == "Price desc"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])