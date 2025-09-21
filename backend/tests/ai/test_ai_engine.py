# tests/ai/test_ai_engine.py - Updated with proper mocking

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from src.ai.ai_engine import AIEngine, AIResponse, AnalysisDepth
from src.data.schemas import MessageType

# Mock OpenRouter API response
MOCK_OPENROUTER_RESPONSE = {
    "choices": [{
        "message": {
            "content": '{"explanation": "Mock AI analysis", "suggested_responses": ["Response 1", "Response 2", "Response 3"], "healing_score": 7, "sentiment": "neutral", "emotional_state": "understanding", "subtext": "Mock subtext", "needs": ["validation"], "warnings": [], "transformed_message": "Mock transformed message", "alternatives": ["Alt 1", "Alt 2"], "communication_patterns": ["Pattern 1"], "relationship_dynamics": ["Dynamic 1"]}',
            "role": "assistant"
        }
    }],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "total_tokens": 150
    }
}

class MockResponse:
    """Mock httpx response object"""
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or MOCK_OPENROUTER_RESPONSE
        self.text = text
    
    def json(self):
        return self._json_data

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient to avoid real API calls"""
    with patch('src.ai.ai_engine.httpx.AsyncClient') as mock_client_class:
        # Create mock client instance
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock the post method to return successful response
        mock_response = MockResponse()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()  # Mock cleanup method
        
        yield mock_client

@pytest.fixture
def mock_cache_crud():
    """Mock database cache operations"""
    with patch('src.ai.ai_engine.CacheCRUD') as mock_cache:
        mock_cache.get_cached_response.return_value = None  # No cached response
        mock_cache.cache_response.return_value = None  # Successful cache
        yield mock_cache

@pytest.fixture
def ai_engine_with_mocks(mock_httpx_client, mock_cache_crud):
    """AI Engine with all external dependencies mocked"""
    engine = AIEngine()
    return engine

class TestAIEngine:
    """AI Engine tests with proper mocking"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "test message",
        "I'm feeling really overwhelmed with work lately", 
        "Hello there!",
        "Can you help with something?",
        "I'm having trouble sleeping",
        "What a beautiful day!",
        "I don't know what to do"
    ])
    async def test_process_message_contract(self, ai_engine_with_mocks, message):
        """Test message processing contract - should be FAST now"""
        result = await ai_engine_with_mocks.process_message(
            message=message,
            contact_context="friend",
            message_type=MessageType.INTERPRET.value,
            contact_id="test_contact",
            user_id="test_user"
        )
        
        # Test the contract
        assert isinstance(result, AIResponse)
        assert result.explanation is not None
        assert result.healing_score >= 1
        assert result.sentiment is not None
        assert result.backend_id is not None
        assert isinstance(result.suggested_responses, list)

    @pytest.mark.asyncio
    async def test_shortcut_methods(self, ai_engine_with_mocks):
        """Test shortcut methods - should be FAST now"""
        # These were taking 87+ seconds before!
        result1 = await ai_engine_with_mocks.quick_analyze(
            "test message", "friend", "contact_id", "user_id"
        )
        result2 = await ai_engine_with_mocks.deep_analyze(
            "test message", "friend", "contact_id", "user_id"
        )
        result3 = await ai_engine_with_mocks.transform(
            "test message", "friend", "contact_id", "user_id"
        )
        
        assert isinstance(result1, AIResponse)
        assert isinstance(result2, AIResponse)
        assert isinstance(result3, AIResponse)
        
        # Verify deep analysis has enhanced fields
        assert result2.analysis_depth == AnalysisDepth.DEEP.value

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, ai_engine_with_mocks):
        """Test concurrent processing - should be FAST now"""
        import asyncio
        
        # This was taking 21+ seconds before!
        tasks = [
            ai_engine_with_mocks.process_message(
                f"message {i}", "friend", MessageType.INTERPRET.value,
                "contact_id", "user_id"
            ) for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 3
        for result in results:
            assert isinstance(result, AIResponse)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_input", [
        "",
        " ", 
        "a",
        "a" * 1000,  # Long string that was taking 26+ seconds
        "Hello\n\nworld",
        "émojis 🎉 and ñoñó",  # This was taking 39+ seconds!
        "12345 !@#$% test"
    ])
    async def test_edge_case_messages(self, ai_engine_with_mocks, test_input):
        """Test edge cases - should be FAST now"""
        result = await ai_engine_with_mocks.process_message(
            message=test_input,
            contact_context="friend", 
            message_type=MessageType.INTERPRET.value,
            contact_id="contact_id",
            user_id="user_id"
        )
        
        assert isinstance(result, AIResponse)
        # Should handle edge cases gracefully

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message_type", ["interpret", "transform"])
    async def test_different_message_types(self, ai_engine_with_mocks, message_type):
        """Test different message types - should be FAST now"""
        result = await ai_engine_with_mocks.process_message(
            message="test message",
            contact_context="friend",
            message_type=message_type,
            contact_id="contact_id", 
            user_id="user_id"
        )
        
        assert isinstance(result, AIResponse)
        if message_type == MessageType.TRANSFORM.value:
            # Transform should have transformed_message or alternatives
            assert result.transformed_message or result.alternatives

    @pytest.mark.asyncio
    async def test_fallback_response_when_api_fails(self, mock_cache_crud):
        """Test fallback when all API calls fail"""
        with patch('src.ai.ai_engine.httpx.AsyncClient') as mock_client_class:
            # Mock client that always fails
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.post = AsyncMock(side_effect=Exception("API Error"))
            mock_client.aclose = AsyncMock()
            
            engine = AIEngine()
            result = await engine.process_message(
                message="test message",
                contact_context="friend",
                message_type=MessageType.INTERPRET.value,
                contact_id="contact_id",
                user_id="user_id"
            )
            
            # Should get fallback response
            assert isinstance(result, AIResponse)
            assert result.model_used == "Fallback System"

# Integration tests (run these separately or mark as slow)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_call():
    """Test with real API - only run when needed"""
    # This test would actually call OpenRouter - use sparingly
    pass

# Performance benchmark (optional)
@pytest.mark.asyncio 
async def test_performance_benchmark(ai_engine_with_mocks):
    """Benchmark test performance"""
    import time
    
    start_time = time.time()
    
    # Run multiple operations
    tasks = []
    for i in range(10):
        task = ai_engine_with_mocks.process_message(
            f"test message {i}", "friend", MessageType.INTERPRET.value,
            f"contact_{i}", "user_id"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert len(results) == 10
    assert duration < 5.0  # Should complete in under 5 seconds
    print(f"✅ 10 AI operations completed in {duration:.2f} seconds")