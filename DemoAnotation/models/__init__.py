"""
Modelos de dados da aplicação.

Author: Christopher N. S. M. Mauricio
"""

from database import Base        # Base único — vem de database.py
from .customer import Customer
from .order    import Order
from .product  import Product

__all__ = ["Base", "Customer", "Order", "Product"]
