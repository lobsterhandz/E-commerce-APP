checks tables and forien key maps

import os
import sys

# Dynamically add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Order, OrderItem, Product, Customer  # Now Python can find models

from models import db

def print_metadata():
    """Print metadata information about all tables and relationships."""
    for table in db.metadata.tables.values():
        print(f"Table: {table.name}")
        print("Columns:")
        for column in table.columns:
            print(f"  - {column.name} ({column.type})")
        print("Foreign Keys:")
        for fk in column.foreign_keys:
            print(f"  - {fk.target_fullname}")
        print("=" * 40)

print_metadata()
