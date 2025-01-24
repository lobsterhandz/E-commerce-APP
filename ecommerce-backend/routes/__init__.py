from .customer_bp import create_customer_bp
from .customer_account_bp import create_customer_account_bp
from .product_bp import create_product_bp
from .category_bp import create_category_bp
from .order_bp import create_order_bp
from .order_item_bp import create_order_item_bp
from .shopping_cart_bp import create_shopping_cart_bp
from .shopping_cart_item_bp import create_shopping_cart_item_bp
from .user_bp import create_user_bp

# Explicit exports for proper IDE autocompletion and avoiding circular imports
__all__ = [
    "create_customer_bp",
    "create_customer_account_bp",
    "create_product_bp",
    "create_order_bp",
    "create_order_item_bp",
    "create_shopping_cart_bp",
    "create_shopping_cart_item_bp",
    "create_user_bp",
    "create_category_bp",    
]
