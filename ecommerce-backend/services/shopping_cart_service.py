# services/shopping_cart_service.py
from models import db, ShoppingCart, ShoppingCartItem, Product
from sqlalchemy.exc import SQLAlchemyError

class ShoppingCartService:
    """
    Service class to handle shopping cart operations.
    """

    # ---------------------------
    # Retrieve or Create Shopping Cart
    # ---------------------------
    @staticmethod
    def get_cart_by_customer(customer_id):
        """
        Retrieve an existing shopping cart for a customer or create a new one if none exists.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            ShoppingCart: The customer's shopping cart object.
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

    # ---------------------------
    # Add or Update Item in Cart
    # ---------------------------
    @staticmethod
    def add_item_to_cart(customer_id, product_id, quantity):
        """
        Adds a new item or updates an existing item in the shopping cart.

        Args:
            customer_id (int): ID of the customer.
            product_id (int): ID of the product.
            quantity (int): Quantity of the product to add.

        Returns:
            ShoppingCartItem: The updated or newly added cart item.

        Raises:
            ValueError: If validation fails or the product does not exist.
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

    # ---------------------------
    # Remove an Item from the Cart
    # ---------------------------
    @staticmethod
    def remove_item_from_cart(customer_id, product_id):
        """
        Removes a specific item from the shopping cart.

        Args:
            customer_id (int): ID of the customer.
            product_id (int): ID of the product to remove.

        Returns:
            bool: True if the item was removed successfully.

        Raises:
            ValueError: If the item is not found in the cart.
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

    # ---------------------------
    # Clear the Shopping Cart
    # ---------------------------
    @staticmethod
    def clear_cart(customer_id):
        """
        Clears all items from the shopping cart.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            bool: True if the cart was cleared successfully.
        """
        try:
            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            if cart:
                # Remove each item individually
                for item in cart.items:
                    db.session.delete(item)
                db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while clearing cart: {str(e)}")

    # ---------------------------
    # Checkout Cart
    # ---------------------------
    @staticmethod
    def checkout_cart(customer_id):
        """
        Converts the current shopping cart into an order.
        It transforms the cart items into a list of order item dictionaries,
        calls the OrderService to create a new order, and then clears the cart.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            dict: A summary containing order_id, total_price, and the order items.

        Raises:
            ValueError: If the cart is empty or any processing error occurs.
        """
        cart = ShoppingCartService.get_cart_by_customer(customer_id)
        if not cart or not cart.items:
            raise ValueError("Cannot checkout. Shopping cart is empty.")

        # Transform cart items into order item dictionaries
        order_items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_order": item.subtotal / item.quantity  # Calculate unit price
            }
            for item in cart.items
        ]

        # Import OrderService locally to avoid circular dependencies
        from services.order_service import OrderService

        # Create an order using the list of order items
        new_order = OrderService.create_order(
            customer_id=customer_id,
            order_items=order_items
        )

        # Clear the shopping cart after successful checkout
        ShoppingCartService.clear_cart(customer_id)

        return {
            "order_id": new_order.id,
            "total_price": new_order.total_price,
            "items": order_items
        }
