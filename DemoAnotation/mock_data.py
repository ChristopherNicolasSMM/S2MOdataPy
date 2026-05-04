"""
Dados de exemplo para desenvolvimento.

Carregados automaticamente quando ENVIRONMENT=dev e o banco está vazio.

Author: Christopher N. S. M. Mauricio
"""

from models.customer import Customer
from models.order import Order
from models.product import Product

CUSTOMERS = [
    Customer(
        CustomerID="ALFKI",
        CompanyName="Alfreds Futterkiste",
        ContactName="Maria Anders",
        ContactTitle="Sales Representative",
        Country="Germany",
        City="Berlin",
        Address="Obere Str. 57",
        PostalCode="12209",
    ),
    Customer(
        CustomerID="ANATR",
        CompanyName="Ana Trujillo Emparedados y helados",
        ContactName="Ana Trujillo",
        ContactTitle="Owner",
        Country="Mexico",
        City="Mexico D.F.",
        Address="Avda. de la Constitución 2222",
        PostalCode="05021",
    ),
    Customer(
        CustomerID="ANTON",
        CompanyName="Antonio Moreno Taquería",
        ContactName="Antonio Moreno",
        ContactTitle="Owner",
        Country="Mexico",
        City="Mexico D.F.",
        Address="Mataderos 2312",
        PostalCode="05023",
    ),
    Customer(
        CustomerID="AROUT",
        CompanyName="Around the Horn",
        ContactName="Thomas Hardy",
        ContactTitle="Sales Representative",
        Country="UK",
        City="London",
        Address="120 Hanover Sq.",
        PostalCode="WA1 1DP",
    ),
    Customer(
        CustomerID="BERGS",
        CompanyName="Berglunds snabbköp",
        ContactName="Christina Berglund",
        ContactTitle="Order Administrator",
        Country="Sweden",
        City="Luleå",
        Address="Berguvsvägen 8",
        PostalCode="S-958 22",
    ),
    Customer(
        CustomerID="BLAUS",
        CompanyName="Blauer See Delikatessen",
        ContactName="Hanna Moos",
        ContactTitle="Sales Representative",
        Country="Germany",
        City="Mannheim",
        Address="Forsterstr. 57",
        PostalCode="68306",
    ),
    Customer(
        CustomerID="BONAP",
        CompanyName="Bon app'",
        ContactName="Laurence Lebihan",
        ContactTitle="Owner",
        Country="France",
        City="Marseille",
        Address="12, rue des Bouchers",
        PostalCode="13008",
    ),
    Customer(
        CustomerID="BOTTM",
        CompanyName="Bottom-Dollar Markets",
        ContactName="Elizabeth Lincoln",
        ContactTitle="Accounting Manager",
        Country="Canada",
        City="Tsawassen",
        Address="23 Tsawassen Blvd.",
        PostalCode="T2F 8M4",
    ),
    Customer(
        CustomerID="BSBEV",
        CompanyName="B's Beverages",
        ContactName="Victoria Ashworth",
        ContactTitle="Sales Representative",
        Country="UK",
        City="London",
        Address="Fauntleroy Circus",
        PostalCode="EC2 5NT",
    ),
    Customer(
        CustomerID="CACTU",
        CompanyName="Cactus Comidas para llevar",
        ContactName="Patricio Simpson",
        ContactTitle="Sales Agent",
        Country="Argentina",
        City="Buenos Aires",
        Address="Cerrito 333",
        PostalCode="1010",
    ),
]

ORDERS = [
    Order(
        CustomerID="ALFKI",
        OrderDate="2024-01-15",
        Freight=32.38,
        ShipName="Alfreds Futterkiste",
        ShipAddress="Obere Str. 57",
        ShipCity="Berlin",
        ShipCountry="Germany",
    ),
    Order(
        CustomerID="ALFKI",
        OrderDate="2024-02-20",
        Freight=11.61,
        ShipName="Alfreds Futterkiste",
        ShipAddress="Obere Str. 57",
        ShipCity="Berlin",
        ShipCountry="Germany",
    ),
    Order(
        CustomerID="ANATR",
        OrderDate="2024-01-10",
        Freight=65.83,
        ShipName="Ana Trujillo Emparedados",
        ShipAddress="Avda. de la Constitución 2222",
        ShipCity="Mexico D.F.",
        ShipCountry="Mexico",
    ),
    Order(
        CustomerID="ANTON",
        OrderDate="2024-03-05",
        Freight=41.34,
        ShipName="Antonio Moreno Taquería",
        ShipAddress="Mataderos 2312",
        ShipCity="Mexico D.F.",
        ShipCountry="Mexico",
    ),
    Order(
        CustomerID="AROUT",
        OrderDate="2024-02-14",
        Freight=13.75,
        ShipName="Around the Horn",
        ShipAddress="Brook Farm, Stratford St. Mary",
        ShipCity="Colchester",
        ShipCountry="UK",
    ),
    Order(
        CustomerID="BERGS",
        OrderDate="2024-03-20",
        Freight=58.17,
        ShipName="Berglunds snabbköp",
        ShipAddress="Berguvsvägen 8",
        ShipCity="Luleå",
        ShipCountry="Sweden",
    ),
    Order(
        CustomerID="BONAP",
        OrderDate="2024-01-25",
        Freight=22.98,
        ShipName="Bon app'",
        ShipAddress="12, rue des Bouchers",
        ShipCity="Marseille",
        ShipCountry="France",
    ),
    Order(
        CustomerID="BOTTM",
        OrderDate="2024-04-01",
        Freight=148.33,
        ShipName="Bottom-Dollar Markets",
        ShipAddress="23 Tsawassen Blvd.",
        ShipCity="Tsawassen",
        ShipCountry="Canada",
    ),
]

PRODUCTS = [
    Product(
        ProductName="Chai", Category="Beverages", UnitPrice=18.00, UnitsInStock=39, ReorderLevel=10
    ),
    Product(
        ProductName="Chang", Category="Beverages", UnitPrice=19.00, UnitsInStock=17, ReorderLevel=25
    ),
    Product(
        ProductName="Aniseed Syrup",
        Category="Condiments",
        UnitPrice=10.00,
        UnitsInStock=13,
        ReorderLevel=25,
    ),
    Product(
        ProductName="Chef Anton's Cajun Seasoning",
        Category="Condiments",
        UnitPrice=22.00,
        UnitsInStock=53,
        ReorderLevel=0,
    ),
    Product(
        ProductName="Grandma's Boysenberry Spread",
        Category="Condiments",
        UnitPrice=25.00,
        UnitsInStock=120,
        ReorderLevel=25,
    ),
    Product(
        ProductName="Uncle Bob's Organic Dried Pears",
        Category="Produce",
        UnitPrice=30.00,
        UnitsInStock=15,
        ReorderLevel=10,
    ),
    Product(
        ProductName="Northwoods Cranberry Sauce",
        Category="Condiments",
        UnitPrice=40.00,
        UnitsInStock=6,
        ReorderLevel=0,
        Discontinued=1,
    ),
    Product(
        ProductName="Mishi Kobe Niku",
        Category="Meat/Poultry",
        UnitPrice=97.00,
        UnitsInStock=29,
        ReorderLevel=0,
        Discontinued=1,
    ),
    Product(
        ProductName="Tofu", Category="Produce", UnitPrice=23.25, UnitsInStock=35, ReorderLevel=0
    ),
    Product(
        ProductName="Ikura", Category="Seafood", UnitPrice=31.00, UnitsInStock=31, ReorderLevel=0
    ),
    Product(
        ProductName="Queso Cabrales",
        Category="Dairy Products",
        UnitPrice=21.00,
        UnitsInStock=22,
        ReorderLevel=30,
    ),
    Product(
        ProductName="Konbu", Category="Seafood", UnitPrice=6.00, UnitsInStock=24, ReorderLevel=5
    ),
    Product(
        ProductName="Tourtière",
        Category="Meat/Poultry",
        UnitPrice=7.45,
        UnitsInStock=21,
        ReorderLevel=10,
    ),
    Product(
        ProductName="Pâté chinois",
        Category="Meat/Poultry",
        UnitPrice=24.00,
        UnitsInStock=115,
        ReorderLevel=20,
    ),
    Product(
        ProductName="Gnocchi di nonna Alice",
        Category="Grains/Cereals",
        UnitPrice=38.00,
        UnitsInStock=21,
        ReorderLevel=10,
    ),
]


def load_mock_data(db):
    """
    Carrega todos os dados de exemplo no banco.

    Chamada automaticamente por main.py quando o ambiente é DEV e o banco está vazio.
    """
    print(f"   Inserindo {len(CUSTOMERS)} clientes...")
    db.add_all(CUSTOMERS)

    print(f"   Inserindo {len(PRODUCTS)} produtos...")
    db.add_all(PRODUCTS)

    db.flush()  # Garante IDs antes dos pedidos (autoincrement)

    print(f"   Inserindo {len(ORDERS)} pedidos...")
    db.add_all(ORDERS)

    db.commit()
    print(
        f"   Dados mock carregados: {len(CUSTOMERS)} clientes, "
        f"{len(ORDERS)} pedidos, {len(PRODUCTS)} produtos."
    )
