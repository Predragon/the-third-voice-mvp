def test_api_imports():
    """Test that all API routes can be imported"""
    try:
        from src.api.routes import auth, contacts, feedback, health, messages
        assert True
    except ImportError as e:
        assert False, f"API import failed: {e}"

def test_auth_route_import():
    """Test auth route specific import"""
    try:
        from src.api.routes.auth import router
        assert True
    except ImportError as e:
        assert False, f"Auth route import failed: {e}"

def test_messages_route_import():
    """Test messages route specific import"""
    try:
        from src.api.routes.messages import router
        assert True
    except ImportError as e:
        assert False, f"Messages route import failed: {e}"
