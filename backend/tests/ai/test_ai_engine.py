"""Enhanced Test Suite for AI Engine Functionality"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.ai.ai_engine import AIEngine, AIResponse, AnalysisDepth

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
        assert hasattr(engine, 'models')
        assert hasattr(engine, 'client')
        assert len(engine.models) > 0
        print("✅ AI Engine initialization successful")
    except Exception as e:
        pytest.fail(f"AI Engine initialization failed: {e}")

def test_ai_engine_methods():
    """Test that AI engine has required methods"""
    engine = AIEngine()
    
    # Check for core methods
    assert hasattr(engine, 'process_message'), "AIEngine should have process_message method"
    assert hasattr(engine, 'quick_analyze'), "AIEngine should have quick_analyze method"
    assert hasattr(engine, 'deep_analyze'), "AIEngine should have deep_analyze method"
    assert hasattr(engine, 'transform'), "AIEngine should have transform method"
    assert hasattr(engine, 'lazy_prewarm'), "AIEngine should have lazy_prewarm method"
    assert hasattr(engine, 'cleanup'), "AIEngine should have cleanup method"
    
    # Check for helper methods
    assert hasattr(engine, '_get_model_display_name'), "AIEngine should have _get_model_display_name method"
    assert hasattr(engine, '_sanitize_message'), "AIEngine should have _sanitize_message method"
    assert hasattr(engine, '_create_message_hash'), "AIEngine should have _create_message_hash method"
    
    print("✅ AI Engine has required methods")

def test_ai_response_creation():
    """Test AIResponse object creation and attributes"""
    response = AIResponse(
        transformed_message="Test message",
        healing_score=7,
        sentiment="positive",
        emotional_state="understanding"
    )
    
    assert response.transformed_message == "Test message"
    assert response.healing_score == 7
    assert response.sentiment == "positive"
    assert response.emotional_state == "understanding"
    assert isinstance(response.needs, list)
    assert isinstance(response.warnings, list)
    assert isinstance(response.suggested_responses, list)
    
    print("✅ AIResponse creation successful")

def test_message_sanitization():
    """Test message sanitization functionality"""
    engine = AIEngine()
    
    # Test basic sanitization
    original = "This is fucking bullshit, you bitch!"
    sanitized = engine._sanitize_message(original)
    
    assert "[strong expletive]" in sanitized
    assert "[expletive]" in sanitized
    assert "fucking" not in sanitized
    assert "bitch" not in sanitized
    
    print("✅ Message sanitization working correctly")

def test_model_display_name():
    """Test model display name extraction"""
    engine = AIEngine()
    
    # Test known model
    display_name = engine._get_model_display_name("deepseek/deepseek-chat-v3.1:free")
    assert display_name == "DeepSeek Chat v3.1"
    
    # Test unknown model
    display_name = engine._get_model_display_name("unknown/model:free")
    assert display_name == "model"
    
    print("✅ Model display name extraction working")

def test_message_hash_creation():
    """Test message hash creation for caching"""
    engine = AIEngine()
    
    hash1 = engine._create_message_hash("test", "context", "interpret", "quick")
    hash2 = engine._create_message_hash("test", "context", "interpret", "quick")
    hash3 = engine._create_message_hash("test", "context", "interpret", "deep")
    
    # Same inputs should produce same hash
    assert hash1 == hash2
    
    # Different analysis depth should produce different hash
    assert hash1 != hash3
    
    print("✅ Message hash creation working correctly")

def test_analysis_depth_enum():
    """Test AnalysisDepth enum"""
    assert AnalysisDepth.QUICK.value == "quick"
    assert AnalysisDepth.DEEP.value == "deep"
    
    print("✅ AnalysisDepth enum working correctly")

def test_fallback_response_generation():
    """Test fallback response generation"""
    engine = AIEngine()
    
    # Test interpretation fallback
    response = engine._get_interpret_fallback("i'm feeling really upset about family issues")
    assert isinstance(response, AIResponse)
    assert response.model_used == "Fallback System"
    assert len(response.suggested_responses) > 0
    
    # Test transform fallback
    response = engine._get_transform_fallback("this is a difficult message")
    assert isinstance(response, AIResponse)
    assert response.transformed_message != ""
    assert response.model_used == "Fallback System"
    
    print("✅ Fallback response generation working")

@pytest.mark.asyncio
async def test_lazy_prewarm():
    """Test lazy prewarming functionality"""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Ready"}}]
        }
        mock_post.return_value = mock_response
        
        engine = AIEngine()
        assert not engine._prewarmed
        
        await engine.lazy_prewarm()
        assert engine._prewarmed
        
    print("✅ Lazy prewarming test passed")

def test_prompt_generation():
    """Test prompt generation for different analysis types"""
    engine = AIEngine()
    
    # Test quick analysis prompts
    system_prompt, user_prompts = engine._get_quick_analysis_prompts("test message", "test context")
    assert "JSON" in system_prompt
    assert len(user_prompts) == 2
    assert all("test message" in prompt or "[expletive]" in prompt for prompt in user_prompts)
    
    # Test deep analysis prompts
    system_prompt, user_prompts = engine._get_deep_analysis_prompts("test message", "test context")
    assert "deep psychological analysis" in system_prompt.lower()
    assert len(user_prompts) == 2
    
    # Test transform prompts
    system_prompt, user_prompts = engine._get_transform_prompts("test message", "test context")
    assert "rewrite" in system_prompt.lower()
    assert len(user_prompts) == 2
    
    print("✅ Prompt generation working correctly")

@pytest.mark.asyncio
async def test_process_message_with_mock():
    """Test process_message with mocked HTTP responses"""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Mock successful AI response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"explanation": "test explanation", "healing_score": 8, "sentiment": "positive", "suggested_responses": ["response1", "response2", "response3"]}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Mock database operations
        with patch('src.data.crud.CacheCRUD.get_cached_response', return_value=None), \
             patch('src.data.crud.CacheCRUD.cache_response'):
            
            engine = AIEngine()
            response = await engine.process_message(
                message="test message",
                contact_context="test context", 
                message_type="interpret",
                contact_id="test_contact",
                user_id="test_user"
            )
            
            assert isinstance(response, AIResponse)
            assert response.explanation == "test explanation"
            assert response.healing_score == 8
            assert response.sentiment == "positive"
            assert len(response.suggested_responses) == 3
    
    print("✅ Process message with mock test passed")

def test_model_configuration():
    """Test that models are properly configured"""
    engine = AIEngine()
    
    # Check that we have multiple models configured
    assert len(engine.models) >= 4
    
    # Check each model has required fields
    for model in engine.models:
        assert "id" in model
        assert "name" in model
        assert "note" in model
        assert ":free" in model["id"]  # All should be free models
    
    print("✅ Model configuration test passed")

@pytest.mark.asyncio
async def test_shortcut_methods():
    """Test shortcut methods with mocks"""
    with patch.object(AIEngine, 'process_message') as mock_process:
        mock_process.return_value = AIResponse(
            transformed_message="test response",
            analysis_depth=AnalysisDepth.QUICK.value
        )
        
        engine = AIEngine()
        
        # Test quick_analyze
        response = await engine.quick_analyze("test", "context", "contact", "user")
        mock_process.assert_called_with("test", "context", "interpret", "contact", "user", "quick")
        
        # Test deep_analyze
        await engine.deep_analyze("test", "context", "contact", "user")
        mock_process.assert_called_with("test", "context", "interpret", "contact", "user", "deep")
        
        # Test transform
        await engine.transform("test", "context", "contact", "user")
        mock_process.assert_called_with("test", "context", "transform", "contact", "user", "quick")
    
    print("✅ Shortcut methods test passed")

@pytest.mark.asyncio
async def test_cleanup():
    """Test cleanup functionality"""
    with patch('httpx.AsyncClient.aclose') as mock_close:
        engine = AIEngine()
        await engine.cleanup()
        mock_close.assert_called_once()
    
    print("✅ Cleanup test passed")

# Integration test helper
def run_integration_tests():
    """Run integration tests that don't require external APIs"""
    print("🧪 Running AI Engine Integration Tests...")
    
    # Test full initialization cycle
    engine = AIEngine()
    assert engine is not None
    
    # Test all core components exist
    assert hasattr(engine, 'models')
    assert hasattr(engine, 'client')
    assert hasattr(engine, '_prewarmed')
    
    # Test utility methods
    sanitized = engine._sanitize_message("This is a test fucking message")
    assert "fucking" not in sanitized
    
    hash_val = engine._create_message_hash("test", "context", "type", "depth")
    assert len(hash_val) == 32  # MD5 hash length
    
    # Test fallback responses
    fallback = engine._get_interpret_fallback("i'm upset")
    assert isinstance(fallback, AIResponse)
    assert fallback.model_used == "Fallback System"
    
    print("✅ All integration tests passed!")

if __name__ == "__main__":
    # Run integration tests directly
    run_integration_tests()