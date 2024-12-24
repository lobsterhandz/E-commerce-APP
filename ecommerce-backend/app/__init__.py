from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password$@127.0.0.1:3306/ecommerce_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    # Import and register blueprints
    from app.routes.customer_routes import customer_routes
    from app.routes.customer_account_routes import customer_account_routes
    from app.routes.product_routes import product_routes
    from app.routes.order_routes import order_routes

    app.register_blueprint(customer_routes, url_prefix="/customers")
    app.register_blueprint(customer_account_routes, url_prefix="/customer_accounts")
    app.register_blueprint(product_routes, url_prefix="/products")
    app.register_blueprint(order_routes, url_prefix="/orders")

    return app