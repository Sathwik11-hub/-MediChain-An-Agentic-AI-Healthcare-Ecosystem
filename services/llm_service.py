"""
LLM Service for interfacing with OpenAI and Anthropic APIs.
"""
import time
from typing import Dict, Any, Optional
from loguru import logger
import openai
from anthropic import Anthropic

from config.settings import settings


class LLMService:
    """Service for LLM operations with retry logic and cost tracking."""
    
    def __init__(self):
        """Initialize LLM clients."""
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        
        # Initialize clients
        if self.provider == "openai":
            openai.api_key = settings.openai_api_key
            self.client = openai
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        # Cost tracking
        self.total_tokens = 0
        self.total_cost = 0.0
        
        logger.info(f"LLM Service initialized with provider: {self.provider}")
    
    def generate_response(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            json_mode: Whether to request JSON output
            
        Returns:
            Generated text response
        """
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        try:
            if self.provider == "openai":
                return self._generate_openai(
                    prompt, temperature, max_tokens, system_prompt, json_mode
                )
            elif self.provider == "anthropic":
                return self._generate_anthropic(
                    prompt, temperature, max_tokens, system_prompt
                )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._retry_generate(
                prompt, temperature, max_tokens, system_prompt, json_mode
            )
    
    def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str],
        json_mode: bool
    ) -> str:
        """Generate response using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if json_mode and "gpt-4" in self.model or "gpt-3.5" in self.model:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        
        # Track usage
        self.total_tokens += response.usage.total_tokens
        self._estimate_cost(response.usage.total_tokens)
        
        logger.info(f"Generated response. Tokens: {response.usage.total_tokens}")
        
        return response.choices[0].message.content
    
    def _generate_anthropic(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Generate response using Anthropic."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        # Track usage
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        self.total_tokens += total_tokens
        self._estimate_cost(total_tokens)
        
        logger.info(f"Generated response. Tokens: {total_tokens}")
        
        return response.content[0].text
    
    def _retry_generate(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str],
        json_mode: bool,
        max_retries: int = 3
    ) -> str:
        """Retry generation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                wait_time = 2 ** attempt
                logger.info(f"Retrying after {wait_time} seconds (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                
                if self.provider == "openai":
                    return self._generate_openai(
                        prompt, temperature, max_tokens, system_prompt, json_mode
                    )
                elif self.provider == "anthropic":
                    return self._generate_anthropic(
                        prompt, temperature, max_tokens, system_prompt
                    )
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise Exception("Failed to generate response after all retries")
    
    def _estimate_cost(self, tokens: int) -> None:
        """Estimate and track API costs."""
        # Rough cost estimates (update based on current pricing)
        cost_per_1k_tokens = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3": 0.025
        }
        
        model_key = next((k for k in cost_per_1k_tokens if k in self.model), "gpt-3.5-turbo")
        cost = (tokens / 1000) * cost_per_1k_tokens[model_key]
        self.total_cost += cost
        
        logger.debug(f"Estimated cost: ${cost:.4f} | Total: ${self.total_cost:.4f}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_tokens": self.total_tokens,
            "estimated_cost": round(self.total_cost, 4),
            "provider": self.provider,
            "model": self.model
        }
    
    def reset_usage_stats(self) -> None:
        """Reset usage tracking."""
        self.total_tokens = 0
        self.total_cost = 0.0
        logger.info("Usage stats reset")


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
