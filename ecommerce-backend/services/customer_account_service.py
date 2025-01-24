from models import db, CustomerAccount, Customer
from sqlalchemy.exc import IntegrityError


class CustomerAccountService:
    # Allowed sortable fields
    SORTABLE_FIELDS = ['username', 'created_at']

    # ---------------------------
    # Create Customer Account
    # ---------------------------
    @staticmethod
    def create_customer_account(username, password, customer_id):
        """
        Creates a new customer account.

        Args:
            username (str): Unique username for the account.
            password (str): Secure password for the account.
            customer_id (int): ID of the associated customer.

        Returns:
            CustomerAccount: Newly created customer account object.

        Raises:
            ValueError: If validation fails or customer does not exist.
        """
        try:
            # Validate customer existence
            customer = Customer.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found.")

            # Create a new customer account
            new_account = CustomerAccount(username=username, customer_id=customer_id)
            new_account.set_password(password)  # Hash and store password
            db.session.add(new_account)
            db.session.commit()

            return new_account
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Username already exists or customer ID is invalid.")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating customer account: {str(e)}")

    # ---------------------------
    # Get Customer Account by ID
    # ---------------------------
    @staticmethod
    def get_customer_account_by_id(account_id):
        """
        Retrieves a customer account by ID.

        Args:
            account_id (int): ID of the account.

        Returns:
            CustomerAccount: Customer account object if found.

        Raises:
            ValueError: If account is not found.
        """
        try:
            account = CustomerAccount.query.get(account_id)
            if not account:
                raise ValueError("CustomerAccount not found.")
            return account
        except Exception as e:
            raise ValueError(f"Error retrieving customer account: {str(e)}")

    # ---------------------------
    # Update Customer Account
    # ---------------------------
    @staticmethod
    def update_customer_account(account_id, username=None, password=None):
        """
        Updates customer account details.

        Args:
            account_id (int): ID of the account.
            username (str): Updated username.
            password (str): Updated password.

        Returns:
            CustomerAccount: Updated customer account object.

        Raises:
            ValueError: If account is not found or validation fails.
        """
        try:
            account = CustomerAccount.query.get(account_id)
            if not account:
                raise ValueError("CustomerAccount not found.")

            # Update fields
            if username:
                if CustomerAccount.query.filter(CustomerAccount.username == username, CustomerAccount.id != account_id).first():
                    raise ValueError("Another account with this username already exists.")
                account.username = username
            if password:
                account.set_password(password)  # Hash new password

            db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error updating customer account: {str(e)}")

    # ---------------------------
    # Delete Customer Account
    # ---------------------------
    @staticmethod
    def delete_customer_account(account_id):
        """
        Deletes a customer account by ID.

        Args:
            account_id (int): ID of the account.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ValueError: If account is not found.
        """
        try:
            account = CustomerAccount.query.get(account_id)
            if not account:
                raise ValueError("CustomerAccount not found.")
            db.session.delete(account)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error deleting customer account: {str(e)}")

    # ---------------------------
    # List Customer Accounts
    # ---------------------------
    @staticmethod
    def list_customer_accounts(customer_id=None):
        """
        Lists all customer accounts, optionally filtered by customer ID.

        Args:
            customer_id (int, optional): ID of the customer to filter by.

        Returns:
            list: List of customer accounts.
        """
        try:
            query = CustomerAccount.query
            if customer_id:
                query = query.filter_by(customer_id=customer_id)
            accounts = query.all()
            return accounts
        except Exception as e:
            raise ValueError(f"Error listing customer accounts: {str(e)}")

    # ---------------------------
    # Get Paginated Customer Accounts
    # ---------------------------
    @staticmethod
    def get_paginated_accounts(page=1, per_page=10, sort_by="id", sort_order="asc", include_meta=True):
        """
        Retrieves a paginated list of customer accounts.

        Args:
            page (int): The page number to retrieve (default: 1).
            per_page (int): The number of accounts per page (default: 10).
            sort_by (str): The field to sort by (default: "id").
            sort_order (str): Sort order, "asc" or "desc" (default: "asc").

        Returns:
            dict: Paginated customer account results, including total, pages, and accounts.

        Raises:
            ValueError: If there is an error during pagination.
        """
        try:
            if sort_order not in ["asc", "desc"]:
                raise ValueError("Invalid sort order. Must be 'asc' or 'desc'.")

            if not hasattr(CustomerAccount, sort_by):
                raise ValueError(f"Invalid sort_by field. Field '{sort_by}' does not exist.")

            query = CustomerAccount.query
            if sort_order == "asc":
                query = query.order_by(getattr(CustomerAccount, sort_by).asc())
            else:
                query = query.order_by(getattr(CustomerAccount, sort_by).desc())

            paginated = query.paginate(page=page, per_page=per_page, error_out=False)

            result = {
                "total": paginated.total,
                "pages": paginated.pages,
                "page": paginated.page,
                "per_page": paginated.per_page,
                "items": [account for account in paginated.items],
            }

            return result
        except Exception as e:
            raise ValueError(f"Error retrieving paginated customer accounts: {str(e)}")
