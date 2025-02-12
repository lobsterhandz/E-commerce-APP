from models import db, Order, Order_Item, Product, Customer
from datetime import datetime 


class OrderService:
    # Allowed sortable fields
    SORTABLE_FIELDS = ['created_at', 'quantity', 'total_price']

    # ---------------------------
    # Create Order
    # ---------------------------
    @staticmethod
    def create_order(customer_id, order_items):
        """
        Creates a new order with a list of order items.

        Args:
            customer_id (int): ID of the customer.
            order_items (list): List of order item dictionaries, each must include:
                - product_id (int)
                - quantity (int)
                - price_at_order (float)

        Returns:
            Order: The newly created order object with its items attached.

        Raises:
            ValueError: If validations fail.
        """
        # Validate customer exists
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ValueError("Customer not found.")

        if not order_items or not isinstance(order_items, list):
            raise ValueError("Order items must be provided as a list.")

        total_price = 0.0

        # Create the order record first (without items)
        new_order = Order(
            customer_id=customer_id,
            total_price=0.0,  # Will update later
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.flush()  # Assign an ID to new_order

        # Process each order item
        for item in order_items:
            # Validate required fields in each order item
            if "product_id" not in item or "quantity" not in item or "price_at_order" not in item:
                raise ValueError("Each order item must include product_id, quantity, and price_at_order.")
            if item["quantity"] <= 0:
                raise ValueError("Quantity must be greater than zero.")

            product = Product.query.get(item["product_id"])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found.")

            subtotal = item["quantity"] * item["price_at_order"]
            total_price += subtotal

            # Create an OrderItem record (assuming your OrderItem model exists)
            new_order_item = OrderItem(
                order_id=new_order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price_at_order=item["price_at_order"],
                subtotal=subtotal,
                created_at=datetime.utcnow()
            )
            db.session.add(new_order_item)

        # Update the order with the total price and commit
        new_order.total_price = total_price
        new_order.updated_at = datetime.utcnow()
        db.session.commit()

        return new_order

    # ---------------------------
    # Get Order by ID
    # ---------------------------
    @staticmethod
    def get_order_by_id(order_id):
        """
        Fetches an order by ID.

        Args:
            order_id (int): ID of the order.

        Returns:
            Order: Retrieved order object.

        Raises:
            ValueError: If order is not found or query fails.
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found.")
            return order
        except Exception as e:
            raise ValueError(f"Error retrieving order: {str(e)}")

    # ---------------------------
    # Delete Order
    # ---------------------------
    @staticmethod
    def delete_order(order_id):
        """
        Deletes an order by ID.

        Args:
            order_id (int): ID of the order.

        Returns:
            bool: True if the order was deleted.

        Raises:
            ValueError: If order is not found or delete fails.
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                raise ValueError("Order not found.")
            db.session.delete(order)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting order: {str(e)}")

    # ---------------------------
    # Get Paginated Orders (Enhanced)
    # ---------------------------
    @staticmethod
    def get_paginated_orders(page=1, per_page=10, sort_by='created_at', sort_order='asc', include_meta=True):
        """
        Retrieves a paginated list of orders with sorting and optional metadata.

        Args:
            page (int): Page number (default: 1).
            per_page (int): Records per page (default: 10, max: 100).
            sort_by (str): Column to sort by ('created_at', 'quantity', 'total_price') (default: 'created_at').
            sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc').
            include_meta (bool): Whether to include metadata (default: True).

        Returns:
            dict: Paginated order data with metadata if requested.

        Raises:
            ValueError: If query or input validation fails.
        """
        try:
            page = max(1, int(page))
            per_page = min(max(1, int(per_page)), 100)
            if sort_by not in OrderService.SORTABLE_FIELDS:
                raise ValueError(f"Invalid sort_by field. Allowed: {OrderService.SORTABLE_FIELDS}")
            sort_column = getattr(Order, sort_by)
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()
            pagination = Order.query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)
            response = {"items": pagination.items}
            if include_meta:
                response.update({
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "page": pagination.page,
                    "per_page": pagination.per_page
                })
            return response
        except Exception as e:
            raise ValueError(f"Error retrieving paginated orders: {str(e)}")