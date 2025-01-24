from models import db, Category


class CategoryService:
    # Allowed fields for sorting
    SORTABLE_FIELDS = ['name']

    # ---------------------------
    # Create a category
    # ---------------------------
    @staticmethod
    def create_category(name):
        """
        Creates a new category.

        Args:
            name (str): Name of the category.

        Returns:
            Category: Created category object.

        Raises:
            ValueError: If validation fails or creation error occurs.
        """
        try:
            # Validate required fields
            if not name or not isinstance(name, str):
                raise ValueError("Invalid category data. Name is required.")

            # Ensure the category name is unique
            existing_category = Category.query.filter_by(name=name).first()
            if existing_category:
                raise ValueError("Category with the same name already exists.")

            # Create a new category
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            return new_category
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating category: {str(e)}")

    # ---------------------------
    # Get all categories
    # ---------------------------
    @staticmethod
    def get_all_categories(sort_by='name', sort_order='asc'):
        """
        Retrieves all categories with optional sorting.

        Args:
            sort_by (str): Field to sort by (default: 'name').
            sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc').

        Returns:
            list: List of categories.

        Raises:
            ValueError: If sorting parameters are invalid.
        """
        try:
            # Validate sorting field
            if sort_by not in CategoryService.SORTABLE_FIELDS:
                raise ValueError(f"Invalid sort_by field. Allowed: {CategoryService.SORTABLE_FIELDS}")

            # Determine sort order
            sort_column = getattr(Category, sort_by)
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()

            # Query sorted categories
            return Category.query.order_by(sort_column).all()
        except Exception as e:
            raise ValueError(f"Error retrieving categories: {str(e)}")

    # ---------------------------
    # Get category by ID
    # ---------------------------
    @staticmethod
    def get_category_by_id(category_id):
        """
        Fetches a category by ID.

        Args:
            category_id (int): ID of the category.

        Returns:
            Category: The category object.

        Raises:
            ValueError: If category not found or query fails.
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                raise ValueError("Category not found.")
            return category
        except Exception as e:
            raise ValueError(f"Error retrieving category: {str(e)}")

    # ---------------------------
    # Update a category
    # ---------------------------
    @staticmethod
    def update_category(category_id, name=None):
        """
        Updates an existing category.

        Args:
            category_id (int): ID of the category.
            name (str, optional): Updated name.

        Returns:
            Category: The updated category object.

        Raises:
            ValueError: If update fails.
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                raise ValueError("Category not found.")

            # Update fields if provided
            if name:
                # Ensure the new category name is unique
                existing_category = Category.query.filter_by(name=name).first()
                if existing_category and existing_category.id != category_id:
                    raise ValueError("Another category with the same name already exists.")
                category.name = name

            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating category: {str(e)}")

    # ---------------------------
    # Delete a category
    # ---------------------------
    @staticmethod
    def delete_category(category_id):
        """
        Deletes a category by ID.

        Args:
            category_id (int): ID of the category.

        Returns:
            bool: True if deletion is successful.

        Raises:
            ValueError: If category not found or delete fails.
        """
        try:
            category = Category.query.get(category_id)
            if not category:
                raise ValueError("Category not found.")
            db.session.delete(category)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting category: {str(e)}")
