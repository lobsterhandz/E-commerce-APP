from models import db, Product

class ProductService:
    # Allowed fields for sorting
    SORTABLE_FIELDS = ['name', 'price', 'stock_quantity']

    # ---------------------------
    # Create a product
    # ---------------------------
    @staticmethod
    def create_product(**kwargs):
        """
        Creates a new product.

        Expected keys in kwargs:
            - name (str): Name of the product (required).
            - price (float): Price of the product (required, non-negative).
            - stock_quantity (int): Available stock (required, non-negative).
            - category_id (int, optional): ID of the category.

        Returns:
            Product: The created product object.

        Raises:
            ValueError: If validation fails or creation error occurs.
        """
        try:
            # Validate required fields
            name = kwargs.get("name")
            price = kwargs.get("price")
            stock_quantity = kwargs.get("stock_quantity")

            if not name:
                raise ValueError("Product name is required.")
            if price is None or not isinstance(price, (int, float)) or price < 0:
                raise ValueError("Price must be a non-negative number.")
            if stock_quantity is None or not isinstance(stock_quantity, int) or stock_quantity < 0:
                raise ValueError("Stock quantity must be a non-negative integer.")

            # Create a new product using all provided keyword arguments
            new_product = Product(**kwargs)
            db.session.add(new_product)
            db.session.commit()
            return new_product
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating product: {str(e)}")

    # ---------------------------
    # Get paginated products
    # ---------------------------
    @staticmethod
    def get_paginated_products(page=1, per_page=10, sort_by='name', sort_order='asc', include_meta=True):
        """
        Retrieves a paginated list of products with sorting and optional metadata.

        Args:
            page (int): Page number (default: 1).
            per_page (int): Records per page (default: 10, max: 100).
            sort_by (str): Column to sort by ('name', 'price', 'stock_quantity') (default: 'name').
            sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc').
            include_meta (bool): Include metadata in the response (default: True).

        Returns:
            dict: Paginated product data with metadata if requested.

        Raises:
            ValueError: If query or input validation fails.
        """
        try:
            # Input validation
            page = max(1, int(page))
            per_page = min(max(1, int(per_page)), 100)

            # Validate sorting field
            if sort_by not in ProductService.SORTABLE_FIELDS:
                raise ValueError(f"Invalid sort_by field. Allowed: {ProductService.SORTABLE_FIELDS}")

            # Determine sort order
            sort_column = getattr(Product, sort_by)
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()

            # Query with pagination and sorting
            pagination = Product.query.order_by(sort_column).paginate(
                page=page, per_page=per_page, error_out=False
            )

            # Prepare response
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
            raise ValueError(f"Error retrieving paginated products: {str(e)}")

    # ---------------------------
    # Get product by ID
    # ---------------------------
    @staticmethod
    def get_product_by_id(product_id):
        """
        Fetches a product by ID.

        Args:
            product_id (int): ID of the product.

        Returns:
            Product: The product object.

        Raises:
            ValueError: If product not found or query fails.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")
            return product
        except Exception as e:
            raise ValueError(f"Error retrieving product: {str(e)}")

    # ---------------------------
    # Update a product
    # ---------------------------
    @staticmethod
    def update_product(product_id, **kwargs):
        """
        Updates an existing product.

        Args:
            product_id (int): ID of the product.
            kwargs: Fields to update (e.g., name, price, stock_quantity, category_id).

        Returns:
            Product: The updated product object.

        Raises:
            ValueError: If update fails.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")

            # Update provided fields
            for key, value in kwargs.items():
                if key == 'price':
                    if not isinstance(value, (int, float)) or value < 0:
                        raise ValueError("Price must be a non-negative number.")
                if key == 'stock_quantity':
                    if not isinstance(value, int) or value < 0:
                        raise ValueError("Stock quantity must be a non-negative integer.")
                setattr(product, key, value)

            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating product: {str(e)}")

    # ---------------------------
    # Delete a product
    # ---------------------------
    @staticmethod
    def delete_product(product_id):
        """
        Deletes a product by ID.

        Args:
            product_id (int): ID of the product.

        Returns:
            bool: True if deletion is successful.

        Raises:
            ValueError: If product not found or delete fails.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                raise ValueError("Product not found.")
            db.session.delete(product)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting product: {str(e)}")
