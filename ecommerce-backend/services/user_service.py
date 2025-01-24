from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    # Allowed fields for sorting
    SORTABLE_FIELDS = ['username', 'email']

    # ---------------------------
    # Create a user
    # ---------------------------
    @staticmethod
    def create_user(username, email, password, role):
        """
        Creates a new user.

        Args:
            username (str): Username of the user.
            email (str): Email of the user.
            password (str): Password for the user.

        Returns:
            User: Created user object.

        Raises:
            ValueError: If validation fails or creation error occurs.
        """
        try:
            # Validate required fields
            if not username or not email or not password:
                raise ValueError("Username, email, and password are required.")

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                raise ValueError("Username already exists.")
            if User.query.filter_by(email=email).first():
                raise ValueError("Email already exists.")

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Create a new user
            new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating user: {str(e)}")

    # ---------------------------
    # Get paginated users
    # ---------------------------
    @staticmethod
    def get_paginated_users(page=1, per_page=10, sort_by='username', sort_order='asc', include_meta=True):
        """
        Retrieves a paginated list of users with sorting and optional metadata.

        Args:
            page (int): Page number (default: 1).
            per_page (int): Records per page (default: 10, max: 100).
            sort_by (str): Column to sort by ('username', 'email') (default: 'username').
            sort_order (str): Sorting order ('asc' or 'desc') (default: 'asc').
            include_meta (bool): Include metadata in the response (default: True).

        Returns:
            dict: Paginated user data with metadata if requested.

        Raises:
            ValueError: If query or input validation fails.
        """
        try:
            # Input validation
            page = max(1, int(page))  # Ensure page >= 1
            per_page = min(max(1, int(per_page)), 100)  # Limit 1 <= per_page <= 100

            # Validate sorting field
            if sort_by not in UserService.SORTABLE_FIELDS:
                raise ValueError(f"Invalid sort_by field. Allowed: {UserService.SORTABLE_FIELDS}")

            # Determine sort order
            sort_column = getattr(User, sort_by)
            if sort_order.lower() == 'desc':
                sort_column = sort_column.desc()

            # Query with pagination and sorting
            pagination = User.query.order_by(sort_column).paginate(
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
            raise ValueError(f"Error retrieving paginated users: {str(e)}")

    # ---------------------------
    # Get user by ID
    # ---------------------------
    @staticmethod
    def get_user_by_id(user_id):
        """
        Fetches a user by ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            User: The user object.

        Raises:
            ValueError: If user not found or query fails.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found.")
            return user
        except Exception as e:
            raise ValueError(f"Error retrieving user: {str(e)}")

    # ---------------------------
    # Update a user
    # ---------------------------
    @staticmethod
    def update_user(user_id, username=None, email=None, password=None):
        """
        Updates an existing user.

        Args:
            user_id (int): ID of the user.
            username (str, optional): Updated username.
            email (str, optional): Updated email.
            password (str, optional): Updated password.

        Returns:
            User: The updated user object.

        Raises:
            ValueError: If update fails.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found.")

            # Update fields if provided
            if username:
                if User.query.filter(User.username == username, User.id != user_id).first():
                    raise ValueError("Username already exists.")
                user.username = username

            if email:
                if User.query.filter(User.email == email, User.id != user_id).first():
                    raise ValueError("Email already exists.")
                user.email = email

            if password:
                user.password = generate_password_hash(password)

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating user: {str(e)}")

    # ---------------------------
    # Delete a user
    # ---------------------------
    @staticmethod
    def delete_user(user_id):
        """
        Deletes a user by ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            bool: True if deletion is successful.

        Raises:
            ValueError: If user not found or delete fails.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found.")
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting user: {str(e)}")

    # ---------------------------
    # Authenticate a user
    # ---------------------------
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate a user by username and password.
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            User: The authenticated user object if successful.
        Raises:
            ValueError: If the username or password is invalid.
        """
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):  # Use password_hash
            return user
        raise ValueError("Invalid username or password")
