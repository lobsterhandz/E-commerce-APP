# routes/product_routes.py
from flask import Blueprint, request, jsonify
from app.models import Product, db
from app.validation import validate_required_fields
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

product_routes = Blueprint('product_routes', __name__)

@product_routes.route('/product', methods=['POST'])
@product_routes.route('/product', methods=['POST'])
def create_product():
    try:
        data = request.json

        # Ensure numeric fields are converted to numbers
        validate_required_fields(data, ['name', 'price'])
        price = float(data['price'])  # Convert price to float
        stock_level = int(data.get('stock_level', 0))  # Convert stock_level to int, default to 0

        if price < 0:
            return jsonify({'error': 'Price must be positive'}), 400
        if stock_level < 0:
            return jsonify({'error': 'Stock level must be non-negative'}), 400

        # Create new product
        product = Product(name=data['name'], price=price, stock_level=stock_level)
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'product_id': product.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Product with the same name already exists or data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_routes.route('/product/<int:id>', methods=['GET'])
def read_product(id):
    try:
        # Retrieve product details by ID
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'stock_level': product.stock_level})
    except SQLAlchemyError:
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_routes.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        # Retrieve the product to be updated
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Update product fields based on user input
        data = request.json
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            if data['price'] < 0:
                return jsonify({'error': 'Price must be positive'}), 400
            product.price = data['price']
        if 'stock_level' in data:
            if data['stock_level'] < 0:
                return jsonify({'error': 'Stock level must be non-negative'}), 400
            product.stock_level = data['stock_level']
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Product with the same name already exists or data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_routes.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        # Retrieve the product to be deleted
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_routes.route('/products', methods=['GET'])
def list_products():
    try:
        # Retrieve all products
        products = Product.query.all()
        product_list = [{'id': p.id, 'name': p.name, 'price': p.price, 'stock_level': p.stock_level} for p in products]
        return jsonify(product_list)
    except SQLAlchemyError:
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_routes.route('/product/<int:id>/stock', methods=['PUT'])
def update_stock(id):
    """
    Updates the stock level of a product.
    """
    try:
        data = request.json
        new_stock_level = data.get('stock_level')

        if new_stock_level is None or new_stock_level < 0:
            return jsonify({'error': 'Invalid stock level'}), 400

        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        product.stock_level = new_stock_level
        db.session.commit()

        return jsonify({'message': 'Stock updated successfully', 'product_id': product.id, 'stock_level': product.stock_level})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
