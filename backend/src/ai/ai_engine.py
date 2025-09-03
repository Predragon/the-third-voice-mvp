"""
AI Engine Module - Content-Filter Resistant
The Third Voice - Works around AI model limitations
Built to handle real human communication
Updated for Peewee ORM and new structure
Added Deep Analysis functionality
Optimized prewarming removed - handled by main.py lifespan
"""

import hashlib
import json
import httpx
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import asyncio

# Update imports
from ..core.config import settings
from ..data.schemas import MessageType, ContextType, SentimentType
from ..data.crud import MessageCRUD, CacheCRUD


class AnalysisDepth(Enum):
    QUICK = "quick"
    DEEP = "deep"


class AIResponse:
    """AI Response data structure"""
    def __init__(self, 
                 transformed_message: str,
                 healing_score: int = 5,
                 sentiment: str = "neutral",
                 emotional_state: str = "understanding",
                 explanation: str = "",
                 subtext: str = "",
                 needs: List[str] = None,
                 warnings: List[str] = None,
                 model_used: str = "",
                 model_id: str = "",
                 analysis_depth: str = AnalysisDepth.QUICK.value,
                 suggested_responses: List[str] = None,
                 communication_patterns: List[str] = None,
                 relationship_dynamics: List[str] = None):
        self.transformed_message = transformed_message
        self.healing_score = healing_score
        self.sentiment = sentiment
        self.emotional_state = emotional_state
        self.explanation = explanation
        self.subtext = subtext
        self.needs = needs or []
        self.warnings = warnings or []
        self.model_used = model_used
        self.model_id = model_id
        self.analysis_depth = analysis_depth
        self.suggested_responses = suggested_responses or []
        self.communication_patterns = communication_patterns or []
        self.relationship_dynamics = relationship_dynamics or []


class AIEngine:
    """AI engine that works around content filtering with deep analysis capabilities"""
    
    def __init__(self):
        # Try models in order of preference - some are less restrictive
        self.models = [
            {"id": "deepseek/deepseek-chat-v3.1:free", "name": "DeepSeek Chat v3.1", "note": "Usually less restrictive"},
            {"id": "deepseek/deepseek-r1-distill-llama-70b:free", "name": "DeepSeek R1 Distill", "note": "Alternative option"},
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B", "note": "Meta's instruction model"},
            {"id": "qwen/qwen-2.5-72b-instruct:free", "name": "Qwen 2.5 72B", "note": "Massive 72B model - excellent for analysis"}
        ]
        
        # HTTP client for better async performance
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Prewarming flag for lazy initialization
        self._prewarmed = False

    def _get_model_display_name(self, model_id: str) -> str:
        """Get user-friendly model name"""
        for model in self.models:
            if model["id"] == model_id:
                return model["name"]
        return model_id.split("/")[-1].replace(":free", "")
    
    def _sanitize_message(self, message: str) -> str:
        """Lightly sanitize message to avoid content filtering while preserving meaning"""
        replacements = {
            "bitch": "[expletive]",
            "vagina": "[inappropriate reference]",
            "deport": "remove from country",
            "fuck": "[strong expletive]",
            "shit": "[expletive]",
            "asshole": "[insult]",
            "bastard": "[insult]",
            "kill": "harm",
            "die": "pass away"
        }
        
        sanitized = message
        for original, replacement in replacements.items():
            sanitized = sanitized.replace(original, replacement)
        
        return sanitized
    
    def _create_message_hash(self, message: str, context: str, message_type: str, analysis_depth: str) -> str:
        """Create hash for caching with analysis depth"""
        content = f"{message}:{context}:{message_type}:{analysis_depth}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _try_model(self, model_info: dict, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> Optional[dict]:
        """Try a specific model and return the result"""
        model_id = model_info["id"]
        print(f"🤖 Trying model: {model_info['name']} ({model_id})")
        api_key = settings.OPENROUTER_API_KEY
        
        if not api_key:
            print("❌ ERROR: No OpenRouter API key found!")
            return None
            
        try:
            response = await self.client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": settings.TEMPERATURE
                }
            )
            
            print(f"📡 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result
            print(f"❌ Model {model_info['name']} failed: Status {response.status_code}")
            print(f"   Error details: {response.text[:300] if response.text else 'No response'}")
            return None
        except httpx.RequestError as e:
            print(f"❌ Network error with {model_info['name']}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error with {model_info['name']}: {str(e)}")
            return None

    async def lazy_prewarm(self):
        """Lazy prewarming - warm primary model on first use"""
        if self._prewarmed:
            return
            
        try:
            print("🔥 Lazy prewarming primary model...")
            primary_model = self.models[0]
            
            result = await self._try_model(
                model_info=primary_model,
                system_prompt="You are ready.",
                user_prompt="Ready",
                max_tokens=5
            )
            
            if result:
                self._prewarmed = True
                print("✅ Lazy prewarming complete")
            else:
                print("⚠️ Lazy prewarming failed, continuing anyway")
                
        except Exception as e:
            print(f"⚠️ Lazy prewarming error: {e}")

    def _get_quick_analysis_prompts(self, message: str, context: str) -> Tuple[str, List[str]]:
        """Get prompts for quick analysis"""
        system_prompt = """You are a communication helper. Interpret what someone really means beneath their words, even when they're upset or using strong language. Suggest compassionate responses. Handle all content professionally.

Respond with JSON:
{"explanation": "what they really mean", "suggested_responses": ["response1", "response2", "response3"], "healing_score": 6, "sentiment": "neutral", "emotional_state": "understanding", "subtext": "their deeper feelings", "needs": ["emotional needs"], "warnings": []}"""
        
        user_prompts = [
            f'Context: {context}. Help me understand what they really mean and suggest 3 compassionate responses: "{message}"',
            f'Context: {context}. Help me understand what they really mean and suggest 3 compassionate responses: "{self._sanitize_message(message)}"'
        ]
        
        return system_prompt, user_prompts

    def _get_deep_analysis_prompts(self, message: str, context: str) -> Tuple[str, List[str]]:
        """Get prompts for deep analysis"""
        system_prompt = """You are an expert communication analyst and relationship counselor. Provide deep psychological analysis of messages with comprehensive insights.

Respond with JSON containing:
- explanation: detailed psychological interpretation
- suggested_responses: 3-5 nuanced compassionate responses
- healing_score: 1-10 rating of healing potential
- sentiment: emotional tone
- emotional_state: inferred emotional state
- subtext: underlying meanings and unspoken feelings
- needs: core emotional needs being expressed
- warnings: any concerning patterns
- communication_patterns: observed communication styles
- relationship_dynamics: insights about the relationship dynamic

Be professional, compassionate, and avoid judgment while providing deep insights."""
        
        user_prompts = [
            f"""Context: {context}. Provide deep psychological analysis of this message. Analyze communication patterns, relationship dynamics, emotional subtext, and provide comprehensive insights:

"{message}"

Consider:
1. What emotional needs are being expressed?
2. What communication patterns are visible?
3. What does this reveal about the relationship dynamic?
4. What might be the historical context?
5. What are the best therapeutic responses?""",
            
            f"""Context: {context}. Provide deep psychological analysis of this sanitized message. Analyze communication patterns, relationship dynamics, emotional subtext, and provide comprehensive insights:

"{self._sanitize_message(message)}"

Consider:
1. What emotional needs are being expressed?
2. What communication patterns are visible?
3. What does this reveal about the relationship dynamic?
4. What might be the historical context?
5. What are the best therapeutic responses?"""
        ]
        
        return system_prompt, user_prompts

    def _get_transform_prompts(self, message: str, context: str) -> Tuple[str, List[str]]:
        """Get prompts for message transformation"""
        system_prompt = """You are a communication helper. Rewrite messages to be more constructive and healing while keeping the core meaning. Handle all content professionally.

Respond with JSON:
{"transformed_message": "rewritten message", "alternatives": ["alt1", "alt2"], "healing_score": 7, "sentiment": "positive", "emotional_state": "caring", "explanation": "why this helps"}"""
        
        user_prompts = [
            f'Context: {context}. Please rewrite this message to be more constructive: "{message}"',
            f'Context: {context}. Please rewrite this message to be more constructive: "{self._sanitize_message(message)}"'
        ]
        
        return system_prompt, user_prompts

    async def process_message(self, 
                            message: str, 
                            contact_context: str, 
                            message_type: str,
                            contact_id: str, 
                            user_id: str,
                            analysis_depth: str = AnalysisDepth.QUICK.value) -> AIResponse:
        """Process message with multiple model fallbacks and caching"""
        print(f"🎙️ Processing message ({analysis_depth}): {message[:50]}...")
        
        # Lazy prewarm on first use
        await self.lazy_prewarm()
        
        # Check cache first
        message_hash = self._create_message_hash(message, contact_context, message_type, analysis_depth)
        cached_response = CacheCRUD.get_cached_response(message_hash, contact_id)
        
        if cached_response:
            print("⚡ Using cached response")
            return AIResponse(
                transformed_message=cached_response.response,
                healing_score=cached_response.healing_score or 5,
                sentiment=cached_response.sentiment or "neutral",
                emotional_state=cached_response.emotional_state or "understanding",
                explanation="Cached response",
                model_used=cached_response.model,
                model_id=cached_response.model,
                analysis_depth=analysis_depth
            )

        # Prepare prompts based on message type and analysis depth
        if message_type == MessageType.TRANSFORM.value:
            system_prompt, user_prompts = self._get_transform_prompts(message, contact_context)
            max_tokens = 800
        else:
            if analysis_depth == AnalysisDepth.DEEP.value:
                system_prompt, user_prompts = self._get_deep_analysis_prompts(message, contact_context)
                max_tokens = 1500  # More tokens for deep analysis
            else:
                system_prompt, user_prompts = self._get_quick_analysis_prompts(message, contact_context)
                max_tokens = 1000

        # Try each model
        used_model_id = None
        used_model_name = None
        
        for model_info in self.models:
            for user_prompt in user_prompts:
                try:
                    result = await self._try_model(model_info, system_prompt, user_prompt, max_tokens)
                    if result:
                        ai_text = result["choices"][0]["message"]["content"]
                        print(f"✅ Got response from {model_info['name']}: {ai_text[:50]}...")
                        used_model_id = model_info["id"]
                        used_model_name = model_info["name"]
                        
                        try:
                            # Extract JSON from response
                            start = ai_text.find('{')
                            end = ai_text.rfind('}') + 1
                            if start >= 0 and end > start:
                                ai_data = json.loads(ai_text[start:end])
                            else:
                                ai_data = {"explanation": "Could not parse AI response"}
                        except json.JSONDecodeError:
                            print(f"⚠️ Failed to parse JSON from {model_info['name']}")
                            continue
                        
                        # Create AI response object
                        ai_response = AIResponse(
                            transformed_message=ai_data.get("transformed_message", ""),
                            healing_score=int(ai_data.get("healing_score", 5)),
                            sentiment=ai_data.get("sentiment", "neutral"),
                            emotional_state=ai_data.get("emotional_state", "understanding"),
                            explanation=ai_data.get("explanation", "Providing support"),
                            subtext=ai_data.get("subtext", ""),
                            needs=ai_data.get("needs", []),
                            warnings=ai_data.get("warnings", []),
                            model_used=used_model_name,
                            model_id=used_model_id,
                            analysis_depth=analysis_depth,
                            suggested_responses=ai_data.get("suggested_responses", []),
                            communication_patterns=ai_data.get("communication_patterns", []),
                            relationship_dynamics=ai_data.get("relationship_dynamics", [])
                        )
                        
                        # For transform responses, ensure we have the main message
                        if message_type == MessageType.TRANSFORM.value and not ai_response.transformed_message:
                            alternatives = ai_data.get("alternatives", [])
                            if alternatives:
                                ai_response.transformed_message = alternatives[0]
                        
                        # Cache the response
                        try:
                            CacheCRUD.cache_response(
                                contact_id=contact_id,
                                user_id=user_id,
                                message_hash=message_hash,
                                context=contact_context,
                                response=ai_response.transformed_message or ai_response.explanation,
                                model=used_model_name,
                                healing_score=ai_response.healing_score,
                                sentiment=SentimentType(ai_response.sentiment) if ai_response.sentiment in [s.value for s in SentimentType] else None,
                                emotional_state=ai_response.emotional_state
                            )
                        except Exception as cache_error:
                            print(f"⚠️ Failed to cache response: {cache_error}")
                        
                        return ai_response
                        
                except Exception as e:
                    print(f"⚠️ Error with {model_info['name']}: {str(e)}")
                    continue

        # Fallback responses
        print("💥 All models failed, using intelligent fallback")
        return self._get_fallback_response(message, message_type, analysis_depth)

    def _get_fallback_response(self, message: str, message_type: str, analysis_depth: str) -> AIResponse:
        """Provide intelligent fallback responses with depth consideration"""
        message_lower = message.lower()
        
        if message_type == MessageType.INTERPRET.value:
            base_response = self._get_interpret_fallback(message_lower)
            if analysis_depth == AnalysisDepth.DEEP.value:
                # Enhance with deeper insights for deep analysis
                base_response.communication_patterns = [
                    "Emotional flooding", 
                    "Crisis communication", 
                    "Seeking validation"
                ]
                base_response.relationship_dynamics = [
                    "High-stress relationship context",
                    "Trust and safety concerns",
                    "Emotional dependency patterns"
                ]
                base_response.suggested_responses = [
                    "I hear the depth of your pain and I want you to know I'm here with you through this.",
                    "Thank you for trusting me with these heavy feelings. How can I best support you right now?",
                    "I can feel how overwhelming this must be. Let's take this one step at a time together."
                ]
            return base_response
        else:
            return self._get_transform_fallback(message_lower)

    def _get_interpret_fallback(self, message_lower: str) -> AIResponse:
        """Fallback for interpretation"""
        if "deport" in message_lower or "immigration" in message_lower:
            return AIResponse(
                transformed_message="I can hear how scared and angry you are about the immigration situation. You're dealing with so much uncertainty and betrayal. I'm here for you through all of this - you don't have to face it alone.",
                healing_score=7, 
                sentiment="neutral", 
                emotional_state="understanding",
                explanation="Your friend is expressing deep fear about deportation, anger about betrayal, and the stress of legal troubles. They're using dark humor to cope but really need support and understanding.",
                subtext="Feeling scared, betrayed, and overwhelmed by legal/immigration issues",
                needs=["safety", "support", "loyalty", "someone who understands", "emotional validation"],
                model_used="Fallback System",
                model_id="fallback",
                suggested_responses=[
                    "I'm so sorry you're going through this. You must be terrified.",
                    "I can't imagine how stressful this is. What do you need most right now?",
                    "You're not alone in this. I'm here to support you however I can."
                ]
            )
        elif "family" in message_lower and "torn apart" in message_lower:
            return AIResponse(
                transformed_message="I hear the pain in your words about your family being torn apart. You're right that we've both been through hell in different ways. I see you, I understand your struggle, and I'm grateful you're sharing this with me.",
                healing_score=6, 
                sentiment="neutral", 
                emotional_state="understanding",
                explanation="They're sharing deep pain about family separation and life's unfairness, looking for connection with someone who understands similar struggles.",
                subtext="Feeling isolated and hurt by family separation, seeking understanding from someone who relates",
                needs=["empathy", "validation", "connection", "shared understanding"],
                model_used="Fallback System",
                model_id="fallback",
                suggested_responses=[
                    "Family pain cuts so deep. I'm here to listen whenever you need.",
                    "It's heartbreaking when family relationships fracture. How are you holding up?",
                    "Thank you for sharing this with me. Your strength in facing this is incredible."
                ]
            )
        else:
            return AIResponse(
                transformed_message="I can see you're dealing with so much pain and anger right now. Thank you for trusting me with these heavy feelings. I'm here to listen and support you however I can.",
                healing_score=6, 
                sentiment="neutral", 
                emotional_state="understanding",
                explanation="They're sharing intense emotions and difficult circumstances, needing someone to witness their pain without judgment.",
                subtext="Overwhelmed by multiple life challenges and needing emotional support",
                needs=["validation", "emotional support", "someone to listen"],
                model_used="Fallback System",
                model_id="fallback",
                suggested_responses=[
                    "I hear how much you're struggling. Thank you for telling me.",
                    "This sounds incredibly difficult. How can I help you through it?",
                    "Your feelings are completely valid. I'm here with you in this."
                ]
            )

    def _get_transform_fallback(self, message_lower: str) -> AIResponse:
        """Fallback for transformation"""
        return AIResponse(
            transformed_message="I'm going through a really tough time and feeling overwhelmed by everything happening. I value our relationship and wanted to share what's on my mind. Can we talk?",
            healing_score=5, 
            sentiment="neutral", 
            emotional_state="caring",
            explanation="Transformed the raw emotions into a request for connection and support",
            model_used="Fallback System",
            model_id="fallback",
            alternatives=[
                "I'm struggling with some heavy feelings and would appreciate your support if you have space to talk.",
                "There's a lot on my mind right now and I could really use a listening ear if you're available."
            ]
        )

    async def quick_analyze(self, message: str, contact_context: str, contact_id: str, user_id: str) -> AIResponse:
        """Quick analysis shortcut"""
        return await self.process_message(
            message, contact_context, MessageType.INTERPRET.value, 
            contact_id, user_id, AnalysisDepth.QUICK.value
        )

    async def deep_analyze(self, message: str, contact_context: str, contact_id: str, user_id: str) -> AIResponse:
        """Deep analysis shortcut"""
        return await self.process_message(
            message, contact_context, MessageType.INTERPRET.value, 
            contact_id, user_id, AnalysisDepth.DEEP.value
        )

    async def transform(self, message: str, contact_context: str, contact_id: str, user_id: str) -> AIResponse:
        """Transform message shortcut"""
        return await self.process_message(
            message, contact_context, MessageType.TRANSFORM.value, 
            contact_id, user_id, AnalysisDepth.QUICK.value
        )

    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()

# Global AI engine instance
ai_engine = AIEngine()
