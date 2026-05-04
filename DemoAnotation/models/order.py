"""
Modelo de Pedido com anotações de UI declarativas.

Author: Christopher N. S. M. Mauricio
"""

from sqlalchemy import Column, Integer, String, Date, Float
from database import Base
from annotations.decorators import UI, Common, Validation


@Common.Label("Pedidos")
@UI.ListView(
    columns=[
        UI.Field("OrderID",     label="Nº Pedido",  width="100px", sortable=True),
        UI.Field("CustomerID",  label="Cliente",    filterable=True),
        UI.Field("OrderDate",   label="Data",       sortable=True),
        UI.Field("Freight",     label="Frete",      sortable=True),
        UI.Field("ShipCountry", label="País Destino", filterable=True),
    ],
    default_sort="OrderID asc",
)
@UI.FieldGroup("OrderInfo", label="Informações do Pedido",
               fields=["OrderID", "CustomerID", "OrderDate", "Freight"])
@UI.FieldGroup("ShipInfo", label="Entrega",
               fields=["ShipName", "ShipAddress", "ShipCity", "ShipCountry"])
@Validation.Required("CustomerID", "Código do cliente é obrigatório")
class Order(Base):
    __tablename__ = "orders"

    OrderID     = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID  = Column(String(5),   nullable=True)
    OrderDate   = Column(String(10),  nullable=True)   # ISO date string: YYYY-MM-DD
    Freight     = Column(Float,       nullable=True, default=0.0)
    ShipName    = Column(String(80),  nullable=True)
    ShipAddress = Column(String(120), nullable=True)
    ShipCity    = Column(String(40),  nullable=True)
    ShipCountry = Column(String(40),  nullable=True)
