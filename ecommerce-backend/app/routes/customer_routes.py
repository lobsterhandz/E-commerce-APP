# routes/customer_routes.py
from flask import Blueprint, request, jsonify
from app.models import Customer, db
from app.validation import validate_email, validate_phone_number, validate_required_fields
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

customer_routes = Blueprint('customer_routes', __name__)

@customer_routes.route('/customer', methods=['POST'])
def create_customer():
    try:
        data = request.json
        validate_required_fields(data, ['name', 'email', 'phone_number'])
        validate_email(data['email'])
        validate_phone_number(data['phone_number'])
        
        # Create a new customer
        customer = Customer(name=data['name'], email=data['email'], phone_number=data['phone_number'])
        db.session.add(customer)
        db.session.commit()
        return jsonify({'message': 'Customer created successfully', 'customer_id': customer.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists or data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_routes.route('/customer/<int:id>', methods=['GET'])
def read_customer(id):
    try:
        # Retrieve customer details by ID
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({'id': customer.id, 'name': customer.name, 'email': customer.email, 'phone_number': customer.phone_number})
    except SQLAlchemyError:
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_routes.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        # Retrieve the customer to be updated
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Update customer fields based on user input
        data = request.json
        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            validate_email(data['email'])
            customer.email = data['email']
        if 'phone_number' in data:
            validate_phone_number(data['phone_number'])
            customer.phone_number = data['phone_number']
        
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists or data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_routes.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    try:
        # Retrieve the customer to be deleted
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_routes.route('/customers', methods=['GET'])
def get_all_customers():
    try:
        # Retrieve all customers from the database
        customers = Customer.query.all()
        customer_list = [{'id': c.id, 'name': c.name, 'email': c.email, 'phone_number': c.phone_number} for c in customers]
        return jsonify(customer_list), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
