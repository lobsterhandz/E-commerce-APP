from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models to register with SQLAlchemy
from .user import User
from .product import Product
from .category import Category
from .order import Order
from .order_item import OrderItem
from .customer import Customer
from .shopping_cart import ShoppingCart
from .shopping_cart_item import ShoppingCartItem
from .customer_account import CustomerAccount

# Explicit exports
__all__ = [
    "db",
    "Customer",
    "Product",
    "Order",
    "CustomerAccount",
    "ShoppingCart",
    "User",
    "Category",
    "OrderItem",
    "ShoppingCartItem",
]

# Logging setup
logger = logging.getLogger(__name__)
logger.info("Models module loaded")
