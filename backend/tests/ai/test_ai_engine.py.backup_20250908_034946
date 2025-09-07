"""Test AI engine functionality"""
import pytest
from src.ai.ai_engine import AIEngine

def test_ai_engine_import():
    """Test that AI engine can be imported"""
    try:
        from src.ai.ai_engine import AIEngine
        assert True
        print("✅ AI Engine import successful")
    except ImportError as e:
        pytest.fail(f"AI Engine import failed: {e}")

def test_ai_engine_initialization():
    """Test that AI engine can be initialized"""
    try:
        engine = AIEngine()
        assert engine is not None
        print("✅ AI Engine initialization successful")
    except Exception as e:
        pytest.fail(f"AI Engine initialization failed: {e}")

def test_ai_engine_methods():
    """Test that AI engine has required methods"""
    engine = AIEngine()
    assert hasattr(engine, 'generate_response'), "AIEngine should have generate_response method"
    assert hasattr(engine, 'process_message'), "AIEngine should have process_message method"
    print("✅ AI Engine has required methods")
