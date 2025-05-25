#!/usr/bin/env python3
"""
Configuration module for the GitHub Repository SEO Optimizer.

This module contains default settings and configuration options for the project.
"""

import os
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    # General settings
    "default_provider": "local",
    "apply_changes": False,
    "sync_forks": True,
    "max_repositories": 100,
    "output_format": "json",
    "verbose": False,
    
    # Provider settings
    "providers": {
        "local": {
            "enabled": True,
            "max_topics": 10,
            "min_description_length": 50,
            "max_description_length": 250,
        },
        "openai": {
            "enabled": True,
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "anthropic": {
            "enabled": True,
            "api_key_env": "ANTHROPIC_API_KEY",
            "model": "claude-instant-1",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "gemini": {
            "enabled": True,
            "api_key_env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
            "model": "gemini-pro",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "ollama": {
            "enabled": True,
            "host": "http://localhost:11434",
            "model": "mistral:latest",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "deepseek": {
            "enabled": True,
            "api_key_env": "DEEPSEEK_API_KEY",
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "zhipu": {
            "enabled": True,
            "api_key_env": "ZHIPU_API_KEY",
            "model": "chatglm-pro",
            "temperature": 0.7,
            "max_tokens": 500,
        },
        "qianwen": {
            "enabled": True,
            "api_key_env": "QIANWEN_API_KEY",
            "model": "qwen-plus",
            "temperature": 0.7,
            "max_tokens": 500,
        },
    },
    
    # GitHub settings
    "github": {
        "api_url": "https://api.github.com",
        "use_gh_cli": True,
        "token_env": "GITHUB_TOKEN",
    },
    
    # Content analysis settings
    "content_analysis": {
        "min_readme_length": 100,
        "max_topics": 20,
        "min_topics": 5,
        "topic_blacklist": ["test", "temp", "temporary", "wip", "work-in-progress"],
        "use_spacy": True,
        "use_keybert": True,
    },
    
    # Output settings
    "output": {
        "save_results": True,
        "results_dir": "results",
        "log_level": "INFO",
    },
}


class Config:
    """Configuration class for the GitHub Repository SEO Optimizer."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration.
        
        Args:
            config_file: Path to a JSON configuration file. If not provided,
                         the default configuration will be used.
        """
        self.config = DEFAULT_CONFIG.copy()
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from a JSON file.
        
        Args:
            config_file: Path to a JSON configuration file.
        """
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
            
            # Update the default configuration with user-provided values
            self._update_config(self.config, user_config)
        except Exception as e:
            print(f"Error loading configuration from {config_file}: {e}")
    
    def _update_config(self, default_config: Dict[str, Any], 
                      user_config: Dict[str, Any]) -> None:
        """Recursively update the default configuration with user-provided values.
        
        Args:
            default_config: The default configuration dictionary.
            user_config: The user-provided configuration dictionary.
        """
        for key, value in user_config.items():
            if key in default_config:
                if isinstance(value, dict) and isinstance(default_config[key], dict):
                    self._update_config(default_config[key], value)
                else:
                    default_config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: The configuration key, using dot notation for nested keys.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value, or the default value if the key is not found.
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: The configuration key, using dot notation for nested keys.
            value: The value to set.
        """
        keys = key.split('.')
        config = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_file: str) -> None:
        """Save the configuration to a JSON file.
        
        Args:
            config_file: Path to the output JSON file.
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration to {config_file}: {e}")
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get the configuration for a specific provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            The provider configuration dictionary.
        """
        return self.get(f"providers.{provider_name}", {})
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a provider is enabled.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            True if the provider is enabled, False otherwise.
        """
        return self.get(f"providers.{provider_name}.enabled", False)
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get the API key for a provider.
        
        Args:
            provider_name: The name of the provider.
            
        Returns:
            The API key, or None if not found.
        """
        api_key_env = self.get(f"providers.{provider_name}.api_key_env")
        
        if not api_key_env:
            return None
        
        if isinstance(api_key_env, list):
            # Try each environment variable in the list
            for env_var in api_key_env:
                api_key = os.environ.get(env_var)
                if api_key:
                    return api_key
            return None
        else:
            # Single environment variable
            return os.environ.get(api_key_env)


# Create a global configuration instance
config = Config()


def load_config(config_file: str) -> None:
    """Load configuration from a JSON file.
    
    Args:
        config_file: Path to a JSON configuration file.
    """
    global config
    config = Config(config_file)


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        The global configuration instance.
    """
    return config 