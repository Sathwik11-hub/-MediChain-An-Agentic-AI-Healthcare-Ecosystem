"""
Unit tests for LLM Service.
"""
import pytest
from unittest.mock import Mock, patch
from services.llm_service import LLMService


class TestLLMService:
    """Test cases for LLM Service."""
    
    @patch('services.llm_service.openai')
    def test_initialization(self, mock_openai):
        """Test LLM service initialization."""
        with patch('services.llm_service.settings') as mock_settings:
            mock_settings.llm_provider = "openai"
            mock_settings.llm_model = "gpt-4"
            mock_settings.llm_temperature = 0.7
            mock_settings.llm_max_tokens = 2000
            mock_settings.openai_api_key = "test-key"
            
            service = LLMService()
            
            assert service.provider == "openai"
            assert service.model == "gpt-4"
            assert service.temperature == 0.7
            assert service.max_tokens == 2000
    
    def test_usage_tracking(self):
        """Test usage statistics tracking."""
        with patch('services.llm_service.settings') as mock_settings:
            mock_settings.llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"
            
            service = LLMService()
            service.total_tokens = 1000
            service.total_cost = 0.05
            
            stats = service.get_usage_stats()
            
            assert stats['total_tokens'] == 1000
            assert stats['estimated_cost'] == 0.05
    
    def test_reset_usage_stats(self):
        """Test resetting usage statistics."""
        with patch('services.llm_service.settings') as mock_settings:
            mock_settings.llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"
            
            service = LLMService()
            service.total_tokens = 1000
            service.total_cost = 0.05
            
            service.reset_usage_stats()
            
            assert service.total_tokens == 0
            assert service.total_cost == 0.0
