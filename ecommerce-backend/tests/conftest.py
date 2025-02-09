import pytest
from app import create_app
from models import db
from tests.db_seed import seed_all

@pytest.fixture(scope="session")
def app():
    """Create an app instance for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        seed_all()  # Populate database with test users, products, etc.
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide a test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a database session."""
    with app.app_context():
        yield db.session
        db.session.rollback()
