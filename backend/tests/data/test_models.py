def test_data_imports():
    """Test that data models can be imported"""
    try:
        from src.data.models import BaseModel, User, Message, Conversation
        assert True
    except ImportError as e:
        assert False, f"Data models import failed: {e}"

def test_database_connection():
    """Test database connection import"""
    try:
        from src.data.database import get_db, init_db
        assert True
    except ImportError as e:
        assert False, f"Database import failed: {e}"
