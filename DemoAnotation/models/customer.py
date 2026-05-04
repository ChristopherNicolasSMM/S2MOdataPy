"""
Modelo de Cliente com anotações de UI declarativas.

Author: Christopher N. S. M. Mauricio
"""

from sqlalchemy import Column, String
from database import Base
from annotations.decorators import UI, Common, Validation


@Common.Label("Clientes")
@UI.ListView(
    columns=[
        UI.Field("CustomerID",   label="Código",   width="80px"),
        UI.Field("CompanyName",  label="Empresa",  sortable=True,  filterable=True),
        UI.Field("ContactName",  label="Contato"),
        UI.Field("Country",      label="País",     sortable=True,  filterable=True),
        UI.Field("City",         label="Cidade",   filterable=True),
    ],
    default_sort="CompanyName asc",
)
@UI.FieldGroup("BasicInfo", label="Informações Básicas",
               fields=["CustomerID", "CompanyName", "ContactName", "ContactTitle"])
@UI.FieldGroup("Address", label="Endereço",
               fields=["Country", "City", "Address", "PostalCode"])
@Validation.Required("CustomerID", "Código do cliente é obrigatório")
@Validation.MaxLength("CustomerID", 5, "Código deve ter no máximo 5 caracteres")
@Validation.Required("CompanyName", "Nome da empresa é obrigatório")
@Validation.MaxLength("CompanyName", 80)
class Customer(Base):
    __tablename__ = "customers"

    CustomerID    = Column(String(5),   primary_key=True, nullable=False)
    CompanyName   = Column(String(80),  nullable=False)
    ContactName   = Column(String(60),  nullable=True)
    ContactTitle  = Column(String(60),  nullable=True)
    Country       = Column(String(40),  nullable=True)
    City          = Column(String(40),  nullable=True)
    Address       = Column(String(120), nullable=True)
    PostalCode    = Column(String(20),  nullable=True)
