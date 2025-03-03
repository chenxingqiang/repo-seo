"""
Language Model Providers for GitHub SEO Optimizer

This module contains providers for different language models that can be used
for generating SEO content, descriptions, and topics.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import logging

from .base_provider import BaseProvider
from .local_provider import LocalProvider

# Configure logging
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Base class for language model providers."""

    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the provider with API key and other parameters."""
        pass

    @abstractmethod
    def generate_description(self, repo_name: str, languages: List[str],
                            topics: List[str], readme: str) -> str:
        """Generate an SEO-friendly description for a repository."""
        pass

    @abstractmethod
    def generate_topics(self, repo_name: str, languages: List[str],
                       current_topics: List[str], readme: str) -> List[str]:
        """Generate SEO-friendly topics for a repository."""
        pass

    @abstractmethod
    def analyze_readme(self, content: str) -> Dict[str, Any]:
        """Analyze README content to extract summary, topics, and named entities."""
        pass

# Provider registry
_PROVIDERS = {
    "local": LocalProvider,
}

# Try to import optional providers
try:
    from .openai_provider import OpenAIProvider
    _PROVIDERS["openai"] = OpenAIProvider
except ImportError:
    logger.debug("OpenAI provider not available")

try:
    from .anthropic_provider import AnthropicProvider
    _PROVIDERS["anthropic"] = AnthropicProvider
except ImportError:
    logger.debug("Anthropic provider not available")

try:
    from .gemini_provider import GeminiProvider
    _PROVIDERS["gemini"] = GeminiProvider
except ImportError:
    logger.debug("Gemini provider not available")

try:
    from .ollama_provider import OllamaProvider
    _PROVIDERS["ollama"] = OllamaProvider
except ImportError:
    logger.debug("Ollama provider not available")

try:
    from .deepseek_provider import DeepSeekProvider
    _PROVIDERS["deepseek"] = DeepSeekProvider
except ImportError:
    logger.debug("DeepSeek provider not available")

try:
    from .zhipu_provider import ZhiPuProvider
    _PROVIDERS["zhipu"] = ZhiPuProvider
except ImportError:
    logger.debug("ZhiPu provider not available")

try:
    from .qianwen_provider import QianWenProvider
    _PROVIDERS["qianwen"] = QianWenProvider
except ImportError:
    logger.debug("QianWen provider not available")


def get_provider(provider_name: str, **kwargs) -> BaseProvider:
    """Get a provider instance by name.

    Args:
        provider_name: The name of the provider.
        **kwargs: Additional arguments to pass to the provider constructor.

    Returns:
        A provider instance.

    Raises:
        ValueError: If the provider is not supported.
    """
    provider_name = provider_name.lower()

    if provider_name not in _PROVIDERS:
        available_providers = ", ".join(_PROVIDERS.keys())
        raise ValueError(
            f"Provider '{provider_name}' is not supported. "
            f"Available providers: {available_providers}"
        )

    provider_class = _PROVIDERS[provider_name]

    try:
        return provider_class(**kwargs)
    except Exception as e:
        logger.error(f"Error initializing provider '{provider_name}': {e}")
        raise


def list_available_providers() -> Dict[str, Any]:
    """List all available providers.

    Returns:
        A dictionary mapping provider names to information about the provider.
    """
    providers = {}

    for name, provider_class in _PROVIDERS.items():
        try:
            # Try to instantiate the provider to get its information
            provider = provider_class()
            providers[name] = {
                "name": name,
                "available": True,
                "info": provider.get_model_info()
            }
        except Exception as e:
            # If the provider cannot be instantiated, mark it as unavailable
            providers[name] = {
                "name": name,
                "available": False,
                "error": str(e)
            }

    return providers


def check_provider_api_key(provider_name: str) -> bool:
    """Check if the API key for a provider is set.

    Args:
        provider_name: The name of the provider.

    Returns:
        True if the API key is set, False otherwise.
    """
    provider_name = provider_name.lower()

    # Local provider doesn't need an API key
    if provider_name == "local":
        return True

    # Ollama provider doesn't need an API key
    if provider_name == "ollama":
        return True

    # Check for API keys based on provider name
    api_key_env_vars = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "deepseek": "DEEPSEEK_API_KEY",
        "zhipu": "ZHIPU_API_KEY",
        "qianwen": "QIANWEN_API_KEY",
    }

    if provider_name not in api_key_env_vars:
        return False

    env_vars = api_key_env_vars[provider_name]

    if isinstance(env_vars, list):
        # Check if any of the environment variables are set
        return any(os.environ.get(env_var) for env_var in env_vars)
    else:
        # Check if the environment variable is set
        return bool(os.environ.get(env_vars))


__all__ = [
    "BaseProvider",
    "LocalProvider",
    "get_provider",
    "list_available_providers",
    "check_provider_api_key",
]