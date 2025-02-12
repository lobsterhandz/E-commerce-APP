# services/shopping_cart_service.py
from models import db, ShoppingCart, ShoppingCartItem, Product, Order_Item
from sqlalchemy.exc import SQLAlchemyError

class ShoppingCartService:
    """
    Service class to handle shopping cart operations.
    """

    @staticmethod
    def get_cart_by_customer(customer_id):
        """
        Retrieve an existing shopping cart for a customer or create a new one if none exists.
        
        Args:
            customer_id (int): The customer's ID.
        
        Returns:
            ShoppingCart: The customer's shopping cart.
        """
        try:
            cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()
            if not cart:
                cart = ShoppingCart(customer_id=customer_id)
                db.session.add(cart)
                db.session.commit()
            return cart
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while retrieving cart: {str(e)}")

    @staticmethod
    def add_item_to_cart(customer_id, product_id, quantity):
        """
        Add a new item to the customer's cart or update an existing one.
        
        Args:
            customer_id (int): The customer's ID.
            product_id (int): The product's ID.
            quantity (int): The quantity to add.
        
        Returns:
            ShoppingCartItem: The new or updated cart item.
        
        Raises:
            ValueError: If validation fails.
        """
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")

            item = ShoppingCartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if not item:
                subtotal = product.price * quantity
                item = ShoppingCartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    subtotal=subtotal
                )
                db.session.add(item)
            else:
                item.quantity += quantity
                item.subtotal = item.quantity * product.price

            db.session.commit()
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while adding item to cart: {str(e)}")

    @staticmethod
    def remove_item_from_cart(customer_id, product_id):
        """
        Remove a specific item from the shopping cart.
        
        Args:
            customer_id (int): The customer's ID.
            product_id (int): The product's ID.
        
        Returns:
            bool: True if the item was removed.
        
        Raises:
            ValueError: If the item is not found.
        """
        try:
            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            item = ShoppingCartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if not item:
                raise ValueError("Item not found in cart.")
            db.session.delete(item)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while removing item from cart: {str(e)}")

    @staticmethod
    def clear_cart(customer_id):
        """
        Clear all items from the customer's shopping cart.
        
        Args:
            customer_id (int): The customer's ID.
        
        Returns:
            bool: True if the cart was cleared.
        """
        try:
            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            if cart:
                # Remove all items in the cart
                db.session.query(ShoppingCartItem).filter_by(cart_id=cart.id).delete()
                db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while clearing cart: {str(e)}")

    @staticmethod
    def checkout_cart(customer_id):
        """
        Converts the customer's shopping cart into an order.
        
        It transforms each cart item into a dictionary representing an order item,
        then calls OrderService.create_order() to create the order,
        and finally clears the cart.
        
        Args:
            customer_id (int): The customer's ID.
        
        Returns:
            dict: A summary of the created order including order_id, total_price, and order items.
        
        Raises:
            ValueError: If the cart is empty or a processing error occurs.
        """
        cart = ShoppingCartService.get_cart_by_customer(customer_id)
        if not cart or not cart.items:
            raise ValueError("Cannot checkout. Shopping cart is empty.")

        # Prepare order_items as a list of dictionaries
        order_items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_order": item.subtotal / item.quantity  # Calculate unit price
            }
            for item in cart.items
        ]

        # Import OrderService locally to avoid circular imports
        from services.order_service import OrderService

        # Create the order using OrderService; it must accept 'order_items' as a keyword argument
        new_order = OrderService.create_order(
            customer_id=customer_id,
            order_items=order_items
        )

        # Clear the shopping cart after successful order creation
        ShoppingCartService.clear_cart(customer_id)

        return {
            "order_id": new_order.id,
            "total_price": new_order.total_price,
            "order_items": order_items
        }
