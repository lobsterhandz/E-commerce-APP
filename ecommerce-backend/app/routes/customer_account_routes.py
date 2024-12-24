# routes/customer_account_routes.py
from flask import Blueprint, request, jsonify
from app.models import CustomerAccount, Customer, db
from app.validation import validate_required_fields
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

customer_account_routes = Blueprint('customer_account_routes', __name__)

@customer_account_routes.route('/customer_account', methods=['POST'])
def create_customer_account():
    try:
        data = request.json
        validate_required_fields(data, ['username', 'password', 'customer_id'])
        
        # Verify that customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create new customer account
        account = CustomerAccount(username=data['username'], password=data['password'], customer_id=data['customer_id'])
        db.session.add(account)
        db.session.commit()
        return jsonify({'message': 'Customer account created successfully', 'account_id': account.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already exists or customer ID is invalid'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_account_routes.route('/customer_account/<int:id>', methods=['GET'])
def read_customer_account(id):
    try:
        # Retrieve account details by ID
        account = CustomerAccount.query.get(id)
        if not account:
            return jsonify({'error': 'Customer account not found'}), 404
        
        # Retrieve the associated customer's information
        customer = Customer.query.get(account.customer_id)
        return jsonify({'account_id': account.id, 'username': account.username, 'customer': {'name': customer.name, 'email': customer.email, 'phone_number': customer.phone_number}})
    except SQLAlchemyError:
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_account_routes.route('/customer_account/<int:id>', methods=['PUT'])
def update_customer_account(id):
    try:
        # Retrieve the customer account to be updated
        account = CustomerAccount.query.get(id)
        if not account:
            return jsonify({'error': 'Customer account not found'}), 404
        
        # Update account fields based on user input
        data = request.json
        if 'username' in data:
            account.username = data['username']
        if 'password' in data:
            account.password = data['password']  # Note: Hash the password in production for security purposes
        
        db.session.commit()
        return jsonify({'message': 'Customer account updated successfully'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username already exists or customer ID is invalid'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_account_routes.route('/customer_account/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    try:
        # Retrieve the customer account to be deleted
        account = CustomerAccount.query.get(id)
        if not account:
            return jsonify({'error': 'Customer account not found'}), 404
        
        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Customer account deleted successfully'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
