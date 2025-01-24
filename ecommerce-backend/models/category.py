from models import db
from sqlalchemy.orm import relationship

class Category(db.Model):
    __tablename__ = 'categories'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)  # Unique and indexed
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)  # Added index for soft-deleted queries

    # Relationships
    products = relationship('Product', back_populates='category')
    # ---------------------------
    # JSON Serialization
    # ---------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    # ---------------------------
    # String Representation
    # ---------------------------
    def __repr__(self):
        return f"<Category {self.name}>"

    # ---------------------------
    # Soft Deletion
    # ---------------------------
    def soft_delete(self):
        """Marks the category as deleted without removing it."""
        self.deleted_at = db.func.current_timestamp()
        db.session.commit()

    # ---------------------------
    # Restore Deleted Category
    # ---------------------------
    def restore(self):
        """Restores a soft-deleted category."""
        self.deleted_at = None
        db.session.commit()

    # ---------------------------
    # Active Categories Query
    # ---------------------------
    @staticmethod
    def active_categories():
        """Returns categories that are not soft-deleted."""
        return Category.query.filter_by(deleted_at=None).all()
