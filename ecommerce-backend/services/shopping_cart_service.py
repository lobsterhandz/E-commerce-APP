from models import db, ShoppingCart, ShoppingCartItem, Product
from sqlalchemy.exc import SQLAlchemyError


class ShoppingCartService:
    """
    Service class to handle shopping cart operations.
    """

    # ---------------------------
    # Get Shopping Cart
    # ---------------------------
    @staticmethod
    def get_cart_by_customer(customer_id):
        """
        Retrieve or create a shopping cart for a customer.

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
    # Add Item to Cart
    # ---------------------------
    @staticmethod
    def add_item_to_cart(customer_id, product_id, quantity):
        """
        Add or update an item in the shopping cart.

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
                # Add new item
                subtotal = product.price * quantity
                item = ShoppingCartItem(
                    cart_id=cart.id, product_id=product_id, quantity=quantity, subtotal=subtotal
                )
                db.session.add(item)
            else:
                # Update quantity and subtotal
                item.quantity += quantity
                item.subtotal = item.quantity * product.price

            db.session.commit()
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while adding item to cart: {str(e)}")

    # ---------------------------
    # Remove Item from Cart
    # ---------------------------
    @staticmethod
    def remove_item_from_cart(customer_id, product_id):
        """
        Remove an item from the shopping cart.

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
    # Clear Shopping Cart
    # ---------------------------
    @staticmethod
    def clear_cart(customer_id):
        """
        Clear all items from the shopping cart.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            bool: True if the cart was cleared successfully.
        """
        try:
            cart = ShoppingCartService.get_cart_by_customer(customer_id)
            db.session.query(ShoppingCartItem).filter_by(cart_id=cart.id).delete()
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
        """Converts the shopping cart into an order."""
        cart = ShoppingCartService.get_cart_by_customer(customer_id)
        if not cart or not cart.items:
            raise ValueError("Cannot checkout. Shopping cart is empty.")

        # Convert cart items to order items
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
        # Create an order from cart
        new_order = OrderService.create_order(customer_id=customer_id, order_items=order_items)

        # Clear the shopping cart after successful checkout
        ShoppingCartService.clear_cart(customer_id)

        return {
            "order_id": new_order.id,
            "total_price": new_order.total_price,
            "items": order_items
        }
    
    @staticmethod
    def clear_cart(customer_id):
        """Clears the shopping cart after checkout."""
        cart = ShoppingCartService.get_cart_by_customer(customer_id)
        if cart:
            cart.items.clear()
            cart.save()