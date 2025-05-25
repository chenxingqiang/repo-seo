"""
Tests for the LLM providers module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_providers import get_provider, LLMProvider
from src.llm_providers.local_provider import LocalProvider
from src.llm_providers.openai_provider import OpenAIProvider
from src.llm_providers.ollama_provider import OllamaProvider
from src.llm_providers.anthropic_provider import AnthropicProvider


class TestLLMProviders(unittest.TestCase):
    """Test the LLM providers module."""
    
    def test_get_provider(self):
        """Test the get_provider function."""
        # Test getting the local provider
        provider = get_provider("local")
        self.assertIsInstance(provider, LocalProvider)
        
        # Test getting an invalid provider
        with self.assertRaises(ValueError):
            get_provider("invalid_provider")
    
    def test_local_provider(self):
        """Test the local provider."""
        provider = LocalProvider()
        
        # Test generate_description
        description = provider.generate_description(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            topics=["test", "repo"],
            readme="# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
        
        # Test generate_topics
        topics = provider.generate_topics(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            current_topics=["test", "repo"],
            readme="# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        self.assertTrue("test" in topics)
        self.assertTrue("repo" in topics)
        
        # Test analyze_readme
        result = provider.analyze_readme(
            "# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertIsInstance(result, dict)
        self.assertTrue("summary" in result)
        self.assertTrue("topics" in result)
        self.assertTrue("entities" in result)
    
    @patch('openai.OpenAI')
    def test_openai_provider(self, mock_openai):
        """Test the OpenAI provider."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock the completion response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create the provider with a mock API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            
            # Test generate_description
            description = provider.generate_description(
                repo_name="test-repo",
                languages=["Python", "JavaScript"],
                topics=["test", "repo"],
                readme="# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertEqual(description, "Test response")
            
            # Test generate_topics with a JSON response
            mock_message.content = '["topic1", "topic2"]'
            topics = provider.generate_topics(
                repo_name="test-repo",
                languages=["Python", "JavaScript"],
                current_topics=["test", "repo"],
                readme="# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertIsInstance(topics, list)
            self.assertTrue("topic1" in topics)
            self.assertTrue("topic2" in topics)
            
            # Test analyze_readme with a JSON response
            mock_message.content = '{"summary": "Test summary", "topics": ["topic1"], "entities": ["entity1"]}'
            result = provider.analyze_readme(
                "# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertIsInstance(result, dict)
            self.assertEqual(result["summary"], "Test summary")
            self.assertEqual(result["topics"], ["topic1"])
            self.assertEqual(result["entities"], ["entity1"])
    
    @patch('requests.post')
    def test_ollama_provider(self, mock_post):
        """Test the Ollama provider."""
        # Mock the requests.post response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response
        
        # Create the provider
        provider = OllamaProvider()
        
        # Test generate_description
        description = provider.generate_description(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            topics=["test", "repo"],
            readme="# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertEqual(description, "Test response")
        
        # Test generate_topics with a JSON response
        mock_response.json.return_value = {"response": '["topic1", "topic2"]'}
        topics = provider.generate_topics(
            repo_name="test-repo",
            languages=["Python", "JavaScript"],
            current_topics=["test", "repo"],
            readme="# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertIsInstance(topics, list)
        self.assertTrue("topic1" in topics)
        self.assertTrue("topic2" in topics)
        
        # Test analyze_readme with a JSON response
        mock_response.json.return_value = {"response": '{"summary": "Test summary", "topics": ["topic1"], "entities": ["entity1"]}'}
        result = provider.analyze_readme(
            "# Test Repo\n\nThis is a test repository for testing purposes."
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["summary"], "Test summary")
        self.assertEqual(result["topics"], ["topic1"])
        self.assertEqual(result["entities"], ["entity1"])
    
    @patch('anthropic.Anthropic')
    def test_anthropic_provider(self, mock_anthropic):
        """Test the Anthropic provider."""
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        
        # Mock the completion response
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Test response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        
        # Create the provider with a mock API key
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            
            # Test generate_description
            description = provider.generate_description(
                repo_name="test-repo",
                languages=["Python", "JavaScript"],
                topics=["test", "repo"],
                readme="# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertEqual(description, "Test response")
            
            # Test generate_topics with a JSON response
            mock_content.text = '["topic1", "topic2"]'
            topics = provider.generate_topics(
                repo_name="test-repo",
                languages=["Python", "JavaScript"],
                current_topics=["test", "repo"],
                readme="# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertIsInstance(topics, list)
            self.assertTrue("topic1" in topics)
            self.assertTrue("topic2" in topics)
            
            # Test analyze_readme with a JSON response
            mock_content.text = '{"summary": "Test summary", "topics": ["topic1"], "entities": ["entity1"]}'
            result = provider.analyze_readme(
                "# Test Repo\n\nThis is a test repository for testing purposes."
            )
            self.assertIsInstance(result, dict)
            self.assertEqual(result["summary"], "Test summary")
            self.assertEqual(result["topics"], ["topic1"])
            self.assertEqual(result["entities"], ["entity1"])


if __name__ == "__main__":
    unittest.main() 