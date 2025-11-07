"""
AI Character Integration
Support for LLM-powered characters that respond in chat
"""
import os
import logging
from typing import List, Optional, Dict
import httpx
from sqlalchemy.orm import Session

from . import models

logger = logging.getLogger(__name__)


class AICharacterManager:
    """Manage AI-powered character responses"""

    def __init__(self):
        self.providers = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "claude": ClaudeProvider(),
            "ollama": OllamaProvider(),
        }

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message] = None,
        db: Session = None
    ) -> Optional[str]:
        """Get AI response for a character"""
        if not member.is_ai or not member.ai_enabled:
            return None

        provider = self.providers.get(member.ai_provider)
        if not provider:
            logger.error(f"Unknown AI provider: {member.ai_provider}")
            return None

        try:
            response = await provider.get_response(
                member=member,
                message=message,
                conversation_history=conversation_history or [],
                db=db
            )
            return response
        except Exception as e:
            logger.error(f"AI response error for {member.name}: {e}")
            return f"*{member.name} seems confused and doesn't respond*"


class BaseProvider:
    """Base class for AI providers"""

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message],
        db: Session
    ) -> str:
        """Get response from AI"""
        raise NotImplementedError

    def build_conversation_context(
        self,
        member: models.Member,
        conversation_history: List[models.Message],
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """Build conversation context from recent messages"""
        messages = []

        # System prompt with personality
        system_prompt = member.ai_personality or f"You are {member.name}."
        if member.description:
            system_prompt += f"\n\n{member.description}"
        if member.pronouns:
            system_prompt += f"\n\nPronouns: {member.pronouns}"

        # Add recent conversation history
        for msg in conversation_history[-max_messages:]:
            role = "assistant" if msg.member_id == member.id else "user"
            messages.append({
                "role": role,
                "content": f"{msg.member.name}: {msg.content}"
            })

        return messages


class GeminiProvider(BaseProvider):
    """Google Gemini API provider"""

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message],
        db: Session
    ) -> str:
        """Get response from Gemini"""
        api_key = member.get_ai_api_key() or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "*AI character needs API key configured*"

        model = member.ai_model or "gemini-pro"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        # Build prompt
        system_prompt = member.ai_personality or f"You are {member.name}."
        if member.description:
            system_prompt += f"\n\n{member.description}"

        # Recent context
        context = ""
        for msg in conversation_history[-5:]:
            context += f"{msg.member.name}: {msg.content}\n"

        full_prompt = f"{system_prompt}\n\nRecent conversation:\n{context}\n\nUser: {message}\n\n{member.name}:"

        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 500,
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if "candidates" in data and len(data["candidates"]) > 0:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()

        return "*AI character failed to respond*"


class OpenAIProvider(BaseProvider):
    """OpenAI / GPT provider"""

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message],
        db: Session
    ) -> str:
        """Get response from OpenAI"""
        api_key = member.get_ai_api_key() or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "*AI character needs API key configured*"

        model = member.ai_model or "gpt-3.5-turbo"
        url = "https://api.openai.com/v1/chat/completions"

        # Build messages
        messages = []

        # System message
        system_prompt = member.ai_personality or f"You are {member.name}, responding in character."
        if member.description:
            system_prompt += f"\n\nCharacter description: {member.description}"
        messages.append({"role": "system", "content": system_prompt})

        # Conversation history
        for msg in conversation_history[-5:]:
            role = "assistant" if msg.member_id == member.id else "user"
            messages.append({
                "role": role,
                "content": msg.content
            })

        # Current message
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.9
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()

        return "*AI character failed to respond*"


class ClaudeProvider(BaseProvider):
    """Anthropic Claude provider"""

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message],
        db: Session
    ) -> str:
        """Get response from Claude"""
        api_key = member.get_ai_api_key() or os.getenv("CLAUDE_API_KEY")
        if not api_key:
            return "*AI character needs API key configured*"

        model = member.ai_model or "claude-3-haiku-20240307"
        url = "https://api.anthropic.com/v1/messages"

        # Build messages (Claude uses different format)
        messages = []

        # Conversation history
        for msg in conversation_history[-5:]:
            role = "assistant" if msg.member_id == member.id else "user"
            messages.append({
                "role": role,
                "content": msg.content
            })

        # Current message
        messages.append({"role": "user", "content": message})

        # System prompt
        system_prompt = member.ai_personality or f"You are {member.name}, responding in character."
        if member.description:
            system_prompt += f"\n\n{member.description}"

        payload = {
            "model": model,
            "max_tokens": 500,
            "system": system_prompt,
            "messages": messages
        }

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "content" in data and len(data["content"]) > 0:
                return data["content"][0]["text"].strip()

        return "*AI character failed to respond*"


class OllamaProvider(BaseProvider):
    """Local Ollama provider (free, runs locally!)"""

    async def get_response(
        self,
        member: models.Member,
        message: str,
        conversation_history: List[models.Message],
        db: Session
    ) -> str:
        """Get response from Ollama (local)"""
        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        model = member.ai_model or "llama2"
        url = f"{base_url}/api/generate"

        # Build prompt
        system_prompt = member.ai_personality or f"You are {member.name}."
        if member.description:
            system_prompt += f"\n\n{member.description}"

        # Recent context
        context = ""
        for msg in conversation_history[-5:]:
            context += f"{msg.member.name}: {msg.content}\n"

        full_prompt = f"{system_prompt}\n\nRecent conversation:\n{context}\n\nUser: {message}\n\n{member.name}:"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.9,
                "num_predict": 500
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                if "response" in data:
                    return data["response"].strip()
        except httpx.ConnectError:
            return "*Ollama is not running. Start it with: `ollama serve`*"
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return "*AI character failed to respond (Ollama error)*"

        return "*AI character failed to respond*"


# Global instance
ai_manager = AICharacterManager()
