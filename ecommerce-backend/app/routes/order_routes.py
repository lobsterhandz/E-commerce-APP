# routes/order_routes.py
from flask import Blueprint, request, jsonify
from app.models import Order, OrderItem, Product, Customer, db
from app.validation import validate_required_fields
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

order_routes = Blueprint('order_routes', __name__)

@order_routes.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        validate_required_fields(data, ['customer_id', 'order_items'])
        
        # Verify that customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create new order
        order = Order(order_date=datetime.utcnow(), customer_id=data['customer_id'])
        db.session.add(order)
        db.session.flush()  # Get order ID for order items
        
        # Add order items
        for item in data['order_items']:
            validate_required_fields(item, ['product_id', 'quantity'])
            product = Product.query.get(item['product_id'])
            if not product:
                db.session.rollback()
                return jsonify({'error': f'Product with ID {item["product_id"]} not found'}), 404
            if product.stock_level < item['quantity']:
                db.session.rollback()
                return jsonify({'error': f'Insufficient stock for product ID {item["product_id"]}'}), 400
            
            # Update product stock level
            product.stock_level -= item['quantity']
            order_item = OrderItem(order_id=order.id, product_id=item['product_id'], quantity=item['quantity'])
            db.session.add(order_item)
        
        db.session.commit()
        return jsonify({'message': 'Order created successfully', 'order_id': order.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/order/<int:id>', methods=['GET'])
def read_order(id):
    try:
        # Retrieve order details by ID
        order = Order.query.get(id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get order items
        order_items = [
            {
                'product_id': item.product_id,
                'quantity': item.quantity
            } for item in order.order_items
        ]
        
        return jsonify({
            'order_id': order.id,
            'order_date': order.order_date,
            'customer_id': order.customer_id,
            'order_items': order_items
        })
    except SQLAlchemyError:
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/order/<int:id>', methods=['PUT'])
def update_order(id):
    try:
        # Retrieve the order to be updated
        order = Order.query.get(id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Update order fields based on user input
        data = request.json
        if 'order_items' in data:
            # Remove existing order items
            OrderItem.query.filter_by(order_id=order.id).delete()
            
            # Add new order items
            for item in data['order_items']:
                validate_required_fields(item, ['product_id', 'quantity'])
                product = Product.query.get(item['product_id'])
                if not product:
                    db.session.rollback()
                    return jsonify({'error': f'Product with ID {item["product_id"]} not found'}), 404
                if product.stock_level < item['quantity']:
                    db.session.rollback()
                    return jsonify({'error': f'Insufficient stock for product ID {item["product_id"]}'}), 400
                
                # Update product stock level
                product.stock_level -= item['quantity']
                order_item = OrderItem(order_id=order.id, product_id=item['product_id'], quantity=item['quantity'])
                db.session.add(order_item)
        
        db.session.commit()
        return jsonify({'message': 'Order updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Data integrity issue occurred'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/order/<int:id>', methods=['DELETE'])
def delete_order(id):
    try:
        # Retrieve the order to be deleted
        order = Order.query.get(id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Restock the products from the deleted order
        for item in order.order_items:
            product = Product.query.get(item.product_id)
            product.stock_level += item.quantity
        
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_routes.route('/orders', methods=['GET'])
def get_orders():
    try:
        # Retrieve all orders
        orders = Order.query.all()
        order_list = []
        for order in orders:
            # Ensure the relationship `order_items` is queried correctly
            order_items = [
                {
                    'product_id': item.product_id,
                    'quantity': item.quantity
                }
                for item in order.order_items
            ]

            # Include customer info and order items
            customer = Customer.query.get(order.customer_id)
            order_list.append({
                'order_id': order.id,
                'customer_name': customer.name if customer else None,
                'order_date': order.order_date,
                'order_items': order_items
            })

        return jsonify(order_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


