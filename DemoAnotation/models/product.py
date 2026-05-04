"""
Modelo de Produto com anotações de UI declarativas.

Author: Christopher N. S. M. Mauricio
"""

from sqlalchemy import Column, Integer, String, Float
from database import Base
from annotations.decorators import UI, Common, Validation


@Common.Label("Produtos")
@UI.ListView(
    columns=[
        UI.Field("ProductID",    label="ID",         width="60px",  sortable=True),
        UI.Field("ProductName",  label="Produto",    sortable=True,  filterable=True),
        UI.Field("UnitPrice",    label="Preço Unit.", sortable=True),
        UI.Field("UnitsInStock", label="Estoque",    sortable=True),
        UI.Field("Category",     label="Categoria",  filterable=True),
    ],
    default_sort="ProductName asc",
)
@UI.FieldGroup("ProductInfo", label="Informações do Produto",
               fields=["ProductID", "ProductName", "Category", "UnitPrice"])
@UI.FieldGroup("StockInfo", label="Estoque",
               fields=["UnitsInStock", "UnitsOnOrder", "ReorderLevel", "Discontinued"])
@Validation.Required("ProductName", "Nome do produto é obrigatório")
@Validation.MaxLength("ProductName", 40)
class Product(Base):
    __tablename__ = "products"

    ProductID      = Column(Integer, primary_key=True, autoincrement=True)
    ProductName    = Column(String(40),  nullable=False)
    Category       = Column(String(40),  nullable=True)
    UnitPrice      = Column(Float,       nullable=True, default=0.0)
    UnitsInStock   = Column(Integer,     nullable=True, default=0)
    UnitsOnOrder   = Column(Integer,     nullable=True, default=0)
    ReorderLevel   = Column(Integer,     nullable=True, default=0)
    Discontinued   = Column(Integer,     nullable=True, default=0)  # 0=não, 1=sim
