# seeding intial data for testing purposes


from app.database import db
from app.models import Customer, Product

# Add seed data
customer1 = Customer(name="John Doe", email="john.doe@example.com", phone_number="+1234567890")
customer2 = Customer(name="Jane Smith", email="jane.smith@example.com", phone_number="+9876543210")

product1 = Product(name="Product A", price=10.99, stock_level=100)
product2 = Product(name="Product B", price=5.99, stock_level=200)

db.session.add_all([customer1, customer2, product1, product2])
db.session.commit()

print("Database seeded successfully!")
py