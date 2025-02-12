import pytest
from app import create_app  # Adjust this import as needed for your project structure
from models import db
from tests.db_seed import seed_all

@pytest.fixture(scope="session")
def app():
    """
    Create an application instance for testing.
    Seeds the database with test data and tears it down after the session.
    """
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_all()  # Populate database with test users, products, etc.
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module")
def client(app):
    """
    Provides a test client for making HTTP requests to the application.
    """
    return app.test_client()

@pytest.fixture
def db_session(app):
    """
    Provide a database session for tests.
    Rolls back any changes after each test.
    """
    with app.app_context():
        yield db.session
        db.session.rollback()
