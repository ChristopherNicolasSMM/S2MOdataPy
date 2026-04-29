"""
Exemplo básico de uso do S2MOdataPy
Author: Christopher N. S. M. Mauricio
"""

from s2modatapy import S2MClient


def main():
    """Exemplo de consultas OData"""
    
    # Inicializa o cliente
    print("🚀 S2MOdataPy - Exemplo de uso")
    print(f"👤 Biblioteca criada por: Christopher N. S. M. Mauricio\n")
    
    client = S2MClient(
        base_url="https://services.odata.org/V4/Northwind/Northwind.svc/",
        debug=True,  # Ativa debug para ver as URLs geradas
        response_format='json'
    )
    
    # Exemplo 1: Clientes do Brasil
    print("\n" + "="*50)
    print("Exemplo 1: Clientes do Brasil")
    print("="*50)
    
    result = (client.entity("Customers")
              .select("CustomerID", "CompanyName", "Country")
              .filter("Country eq 'Brazil'")
              .orderby("CompanyName", "asc")
              .get())
    
    for customer in result.get('value', []):
        print(f"ID: {customer['CustomerID']} - {customer['CompanyName']}")
    
    # Exemplo 2: Produtos caros
    print("\n" + "="*50)
    print("Exemplo 2: Produtos com preço > 50")
    print("="*50)
    
    result = (client.entity("Products")
              .select("ProductName", "UnitPrice")
              .filter("UnitPrice gt 50")
              .orderby("UnitPrice", "desc")
              .top(5)
              .get())
    
    for product in result.get('value', []):
        print(f"{product['ProductName']}: ${product['UnitPrice']}")
    
    # Exemplo 3: Contagem de registros
    print("\n" + "="*50)
    print("Exemplo 3: Contagem de pedidos")
    print("="*50)
    
    total = (client.entity("Orders")
             .filter("OrderDate ge 1998-01-01")
             .count_only())
    
    print(f"Total de pedidos após 1998: {total}")


if __name__ == "__main__":
    main()