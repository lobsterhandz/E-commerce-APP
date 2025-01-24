from models import db, ShoppingCartItem, Product
from sqlalchemy.exc import SQLAlchemyError


class ShoppingCartItemService:
    """
    Service class to handle shopping cart item operations.
    """

    # ---------------------------
    # Get Item by ID
    # ---------------------------
    @staticmethod
    def list_items_by_cart(cart_id):
        """
        List all items in a specific shopping cart.

        Args:
            cart_id (int): ID of the shopping cart.

        Returns:
            list: A list of shopping cart items.
        """
        try:
            # Ensure you're using `.all()` to fetch multiple items
            items = ShoppingCartItem.query.filter_by(cart_id=cart_id).all()
            return items
        except SQLAlchemyError as e:
            raise ValueError(f"Database error while listing items: {str(e)}")


    # ---------------------------
    # Update Item Quantity
    # ---------------------------
    @staticmethod
    def update_item_quantity(item_id, quantity):
        """
        Update the quantity of a shopping cart item.

        Args:
            item_id (int): ID of the shopping cart item.
            quantity (int): New quantity for the item.

        Returns:
            ShoppingCartItem: The updated cart item.

        Raises:
            ValueError: If validation fails or the item is not found.
        """
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            item = ShoppingCartItemService.get_item_by_id(item_id)
            product = item.product  # Fetch the associated product
            item.quantity = quantity
            item.subtotal = quantity * product.price
            db.session.commit()
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while updating item quantity: {str(e)}")

    # ---------------------------
    # Remove Item
    # ---------------------------
    @staticmethod
    def remove_item(item_id):
        """
        Remove a shopping cart item by its ID.

        Args:
            item_id (int): ID of the shopping cart item.

        Returns:
            bool: True if the item was removed successfully.

        Raises:
            ValueError: If the item is not found.
        """
        try:
            item = ShoppingCartItemService.get_item_by_id(item_id)
            db.session.delete(item)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while removing item: {str(e)}")

    # ---------------------------
    # Add Item
    # ---------------------------
    @staticmethod
    def add_item(cart_id, product_id, quantity):
        """
        Add a new item to the shopping cart.

        Args:
            cart_id (int): ID of the shopping cart.
            product_id (int): ID of the product to add.
            quantity (int): Quantity of the product.

        Returns:
            ShoppingCartItem: The newly created cart item.

        Raises:
            ValueError: If validation fails or the product does not exist.
        """
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")

            existing_item = ShoppingCartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()

            if existing_item:
                # Update existing item
                existing_item.quantity += quantity
                existing_item.subtotal = existing_item.quantity * product.price
                db.session.commit()
                return existing_item

            # Add new item
            subtotal = product.price * quantity
            new_item = ShoppingCartItem(cart_id=cart_id, product_id=product_id, quantity=quantity, subtotal=subtotal)
            db.session.add(new_item)
            db.session.commit()
            return new_item
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error while adding item: {str(e)}")

    # ---------------------------
    # List Items by Cart ID
    # ---------------------------
    @staticmethod
    def list_items_by_cart(cart_id):
        """
        List all items in a specific shopping cart.

        Args:
            cart_id (int): ID of the shopping cart.

        Returns:
            list: A list of shopping cart items.
        """
        try:
            items = ShoppingCartItem.query.filter_by(cart_id=cart_id).all()
            return items
        except SQLAlchemyError as e:
            raise ValueError(f"Database error while listing items: {str(e)}")
