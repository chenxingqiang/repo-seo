# LLM Providers for GitHub Repository SEO Optimizer

This document provides detailed information about the Language Model (LLM) providers available in the GitHub Repository SEO Optimizer.

## Overview

The GitHub Repository SEO Optimizer supports multiple LLM providers for generating SEO content:

1. **Local Provider**: Rule-based approach without external API dependencies
2. **OpenAI Provider**: Uses OpenAI's GPT models
3. **Anthropic Provider**: Uses Anthropic's Claude models
4. **Ollama Provider**: Uses local language models through Ollama

Each provider implements the same interface, making them interchangeable in the application.

## Provider Interface

All providers implement the following interface:

```python
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
```

## Local Provider

The Local Provider uses rule-based approaches to generate SEO content without external API dependencies. This is the default provider and requires no API keys.

### Features

- No external API dependencies
- Fast execution
- Deterministic results
- No cost

### Usage

```python
from src.llm_providers import get_provider

provider = get_provider("local")

description = provider.generate_description(
    repo_name="example-repo",
    languages=["Python", "JavaScript"],
    topics=["example", "demo"],
    readme="# Example Repository\n\nThis is an example repository."
)

print(f"Generated description: {description}")
```

## OpenAI Provider

The OpenAI Provider uses OpenAI's GPT models to generate high-quality SEO content.

### Features

- High-quality content generation
- Advanced language understanding
- Customizable model selection

### Requirements

- OpenAI API key
- `openai` Python package installed

### Usage

```python
import os
os.environ["OPENAI_API_KEY"] = "your_api_key_here"

from src.llm_providers import get_provider

provider = get_provider("openai", model="gpt-4")  # or "gpt-3.5-turbo"

description = provider.generate_description(
    repo_name="example-repo",
    languages=["Python", "JavaScript"],
    topics=["example", "demo"],
    readme="# Example Repository\n\nThis is an example repository."
)

print(f"Generated description: {description}")
```

## Anthropic Provider

The Anthropic Provider uses Anthropic's Claude models for content generation.

### Features

- High-quality content generation
- Advanced reasoning capabilities
- Customizable model selection

### Requirements

- Anthropic API key
- `anthropic` Python package installed

### Usage

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "your_api_key_here"

from src.llm_providers import get_provider

provider = get_provider("anthropic", model="claude-3-sonnet-20240229")

description = provider.generate_description(
    repo_name="example-repo",
    languages=["Python", "JavaScript"],
    topics=["example", "demo"],
    readme="# Example Repository\n\nThis is an example repository."
)

print(f"Generated description: {description}")
```

## Ollama Provider

The Ollama Provider uses local language models through Ollama for content generation.

### Features

- Local execution (no data sent to external APIs)
- No API key required
- Customizable model selection
- Privacy-focused

### Requirements

- Ollama installed and running locally
- `requests` Python package installed

### Usage

```python
from src.llm_providers import get_provider

provider = get_provider("ollama", model="llama3")  # or any other model available in Ollama

description = provider.generate_description(
    repo_name="example-repo",
    languages=["Python", "JavaScript"],
    topics=["example", "demo"],
    readme="# Example Repository\n\nThis is an example repository."
)

print(f"Generated description: {description}")
```

## Factory Function

The `get_provider` factory function is used to create instances of the appropriate provider:

```python
from src.llm_providers import get_provider

# Get the local provider (default)
local_provider = get_provider("local")

# Get the OpenAI provider
openai_provider = get_provider("openai", model="gpt-4")

# Get the Anthropic provider
anthropic_provider = get_provider("anthropic", model="claude-3-sonnet-20240229")

# Get the Ollama provider
ollama_provider = get_provider("ollama", model="llama3")
```

## Extending with New Providers

To add a new provider:

1. Create a new file in the `src/llm_providers` directory (e.g., `new_provider.py`)
2. Implement the `LLMProvider` interface
3. Update the `get_provider` function in `src/llm_providers/__init__.py` to include your new provider

Example:

```python
# src/llm_providers/new_provider.py
from typing import List, Dict, Any, Optional
from . import LLMProvider

class NewProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        # Implementation
        pass
    
    def generate_description(self, repo_name: str, languages: List[str], 
                           topics: List[str], readme: str) -> str:
        # Implementation
        pass
    
    def generate_topics(self, repo_name: str, languages: List[str],
                      current_topics: List[str], readme: str) -> List[str]:
        # Implementation
        pass
    
    def analyze_readme(self, content: str) -> Dict[str, Any]:
        # Implementation
        pass
```

Then update the `get_provider` function:

```python
# src/llm_providers/__init__.py
def get_provider(provider_name: str, **kwargs) -> LLMProvider:
    from .openai_provider import OpenAIProvider
    from .ollama_provider import OllamaProvider
    from .anthropic_provider import AnthropicProvider
    from .local_provider import LocalProvider
    from .new_provider import NewProvider  # Import your new provider
    
    providers = {
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
        'anthropic': AnthropicProvider,
        'local': LocalProvider,
        'new': NewProvider,  # Add your new provider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Provider '{provider_name}' not supported. Available providers: {', '.join(providers.keys())}")
    
    return providers[provider_name](**kwargs)
``` 