"""Test database connection and basic operations"""
import pytest
from src.data.database import get_db, init_db

def test_database_connection():
    """Test that database connection can be established"""
    try:
        db = get_db()
        assert db is not None
        print("✅ Database connection successful")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_database_initialization():
    """Test that database can be initialized"""
    try:
        init_db()
        print("✅ Database initialization successful")
        assert True
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")
