"""
Google Gemini AI service integration.
"""
import os
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GeminiConfig(BaseModel):
    """Configuration for Gemini AI service."""
    api_key: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_output_tokens: Optional[int] = None


class GeminiService:
    """Service for interacting with Google Gemini AI."""
    
    def __init__(self, config: GeminiConfig):
        self.config = config
        self._model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Gemini client."""
        try:
            genai.configure(api_key=self.config.api_key)
            self._model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                )
            )
            logger.info(f"Gemini service initialized with model: {self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini AI."""
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            raise
    
    async def chat(self, messages: list[Dict[str, str]]) -> str:
        """Start a chat session with Gemini."""
        try:
            chat = self._model.start_chat()
            
            # Send all messages except the last one as history
            for message in messages[:-1]:
                chat.send_message(message.get("content", ""))
            
            # Send the last message and get response
            response = chat.send_message(messages[-1].get("content", ""))
            return response.text
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            raise


def create_gemini_service(api_key: Optional[str] = None) -> Optional[GeminiService]:
    """Create and configure Gemini service from API key."""
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("GEMINI_API_KEY not found")
        return None
    
    config = GeminiConfig(api_key=api_key)
    return GeminiService(config)


# Global instance
gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> Optional[GeminiService]:
    """Get the global Gemini service instance."""
    global gemini_service
    if gemini_service is None:
        gemini_service = create_gemini_service()
    return gemini_service