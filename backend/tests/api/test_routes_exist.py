"""Test that API routes can be imported and initialized"""
import pytest

def test_auth_route_import():
    """Test auth route import"""
    try:
        from src.api.routes.auth import router
        assert router is not None
        print("✅ Auth route import successful")
    except ImportError as e:
        pytest.fail(f"Auth route import failed: {e}")

def test_messages_route_import():
    """Test messages route import"""
    try:
        from src.api.routes.messages import router
        assert router is not None
        print("✅ Messages route import successful")
    except ImportError as e:
        pytest.fail(f"Messages route import failed: {e}")

def test_health_route_import():
    """Test health route import"""
    try:
        from src.api.routes.health import router
        assert router is not None
        print("✅ Health route import successful")
    except ImportError as e:
        pytest.fail(f"Health route import failed: {e}")
