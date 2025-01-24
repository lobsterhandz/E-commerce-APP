from models import db, OrderItem, Product, Order


class OrderItemService:
    """
    Service class to handle operations related to OrderItems.
    """

    # ---------------------------
    # Add Item to Order
    # ---------------------------
    @staticmethod
    def add_item_to_order(order_id, product_id, quantity):
        """
        Adds an item to an existing order.

        Args:
            order_id (int): ID of the order.
            product_id (int): ID of the product to add.
            quantity (int): Quantity of the product.

        Returns:
            OrderItem: Newly created or updated order item.

        Raises:
            ValueError: If the order or product is invalid, or if quantity is less than 1.
        """
        try:
            # Validate order
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found.")

            # Validate product
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")

            # Validate quantity
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            # Check if item already exists in order
            item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()

            if not item:
                # Create new item
                item = OrderItem(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_order=product.price,
                    subtotal=product.price * quantity
                )
                db.session.add(item)
            else:
                # Update existing item
                item.quantity += quantity
                item.subtotal = item.quantity * product.price

            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error adding item to order: {str(e)}")

    # ---------------------------
    # Remove Item from Order
    # ---------------------------
    @staticmethod
    def remove_item_from_order(order_id, product_id):
        """
        Removes an item from an order.

        Args:
            order_id (int): ID of the order.
            product_id (int): ID of the product to remove.

        Returns:
            bool: True if the item was removed successfully.

        Raises:
            ValueError: If the item is not found in the order.
        """
        try:
            item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()
            if not item:
                raise ValueError("Item not found in order.")

            db.session.delete(item)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error removing item from order: {str(e)}")

    # ---------------------------
    # Get Items for Order
    # ---------------------------
    @staticmethod
    def get_items_by_order_id(order_id):
        """
        Retrieves all items for a specific order.

        Args:
            order_id (int): ID of the order.

        Returns:
            list[OrderItem]: List of items in the order.

        Raises:
            ValueError: If the order is invalid or retrieval fails.
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found.")

            return order.items
        except Exception as e:
            raise ValueError(f"Error retrieving items for order: {str(e)}")

    # ---------------------------
    # Update Item in Order
    # ---------------------------
    @staticmethod
    def update_item_in_order(order_id, product_id, quantity):
        """
        Updates the quantity of an item in an order.

        Args:
            order_id (int): ID of the order.
            product_id (int): ID of the product.
            quantity (int): New quantity of the product.

        Returns:
            OrderItem: Updated order item.

        Raises:
            ValueError: If the order or product is invalid, or if the item is not found.
        """
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()
            if not item:
                raise ValueError("Item not found in order.")

            # Update quantity and subtotal
            item.quantity = quantity
            item.subtotal = item.quantity * item.price_at_order

            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating item in order: {str(e)}")

    # ---------------------------
    # Clear Items from Order
    # ---------------------------
    @staticmethod
    def clear_items_from_order(order_id):
        """
        Removes all items from an order.

        Args:
            order_id (int): ID of the order.

        Returns:
            bool: True if all items were successfully removed.

        Raises:
            ValueError: If the order is invalid or clearing fails.
        """
        try:
            items = OrderItem.query.filter_by(order_id=order_id).all()
            if not items:
                raise ValueError("No items found in order.")

            for item in items:
                db.session.delete(item)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error clearing items from order: {str(e)}")
