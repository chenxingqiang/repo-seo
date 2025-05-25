API Reference
=============

This section contains the API documentation for all modules in the GitHub Repository SEO Optimizer.

.. toctree::
   :maxdepth: 2
   :caption: Core Modules

   llm_providers
   github_client
   seo_generator
   content_analyzer

Module Overview
---------------

The GitHub Repository SEO Optimizer is organized into several key modules:

LLM Providers
~~~~~~~~~~~~~

The :doc:`llm_providers` module contains implementations for all supported language model providers:

* **Base Provider**: Abstract base class for all providers
* **Local Provider**: Rule-based SEO generation without external APIs
* **OpenAI Provider**: Integration with OpenAI's GPT models
* **Anthropic Provider**: Integration with Anthropic's Claude models
* **Gemini Provider**: Integration with Google's Gemini models
* **Ollama Provider**: Integration with local Ollama models
* **DeepSeek Provider**: Integration with DeepSeek's models
* **ZhiPu Provider**: Integration with ZhiPu AI's GLM models
* **QianWen Provider**: Integration with Alibaba's QianWen models

GitHub Client
~~~~~~~~~~~~~

The :doc:`github_client` module handles all interactions with GitHub:

* **Repository Management**: Fetch and update repository information
* **Topic Management**: Validate and update repository topics
* **README Operations**: Create and update README files
* **Authentication**: Handle GitHub CLI authentication

SEO Generator
~~~~~~~~~~~~~

The :doc:`seo_generator` module is responsible for generating SEO content:

* **Description Generation**: Create optimized repository descriptions
* **Topic Generation**: Generate relevant topics based on content
* **Keyword Extraction**: Extract important keywords from code and documentation

Content Analyzer
~~~~~~~~~~~~~~~~

The :doc:`content_analyzer` module analyzes repository content:

* **Language Detection**: Identify programming languages used
* **Code Analysis**: Analyze code structure and patterns
* **Documentation Analysis**: Extract information from existing documentation
* **Dependency Analysis**: Identify project dependencies

Quick Reference
---------------

Common Imports
~~~~~~~~~~~~~~

.. code-block:: python

   # Import LLM providers
   from src.llm_providers import get_provider
   from src.llm_providers.openai_provider import OpenAIProvider
   from src.llm_providers.local_provider import LocalProvider

   # Import GitHub client
   from src.github_client import GitHubClient
   from src.github_client.repository import Repository

   # Import SEO generator
   from src.seo_generator import SEOGenerator
   from src.seo_generator.description import DescriptionGenerator

   # Import content analyzer
   from src.content_analyzer import ContentAnalyzer
   from src.content_analyzer.language import LanguageDetector

Basic Usage Examples
~~~~~~~~~~~~~~~~~~~~

**Using LLM Providers:**

.. code-block:: python

   # Get a provider
   provider = get_provider("openai", model="gpt-4")
   
   # Generate description
   description = provider.generate_description(
       repo_name="my-repo",
       languages=["Python", "JavaScript"],
       topics=["web", "api"],
       readme="# My Repository\n\nThis is my project."
   )

**Using GitHub Client:**

.. code-block:: python

   # Initialize client
   client = GitHubClient(username="myusername")
   
   # Get repository
   repo = client.get_repository("my-repo")
   
   # Update topics
   client.update_topics("my-repo", ["python", "api", "web"])

**Using SEO Generator:**

.. code-block:: python

   # Initialize generator
   generator = SEOGenerator(provider="openai")
   
   # Generate SEO content
   seo_content = generator.generate(
       repository=repo,
       languages=["Python"],
       existing_topics=["api"]
   )

**Using Content Analyzer:**

.. code-block:: python

   # Initialize analyzer
   analyzer = ContentAnalyzer()
   
   # Analyze repository
   analysis = analyzer.analyze_repository(
       username="myusername",
       repo_name="my-repo"
   )
   
   print(f"Languages: {analysis['languages']}")
   print(f"Dependencies: {analysis['dependencies']}")

Error Handling
~~~~~~~~~~~~~~

All modules follow consistent error handling patterns:

.. code-block:: python

   from src.exceptions import (
       GitHubAPIError,
       LLMProviderError,
       ValidationError
   )
   
   try:
       # Your code here
       provider = get_provider("openai")
       description = provider.generate_description(...)
   except LLMProviderError as e:
       print(f"LLM Provider error: {e}")
   except GitHubAPIError as e:
       print(f"GitHub API error: {e}")
   except ValidationError as e:
       print(f"Validation error: {e}")

Configuration
~~~~~~~~~~~~~

Most modules can be configured through environment variables or initialization parameters:

.. code-block:: python

   import os
   
   # Set API keys
   os.environ["OPENAI_API_KEY"] = "your-key"
   os.environ["GITHUB_TOKEN"] = "your-token"
   
   # Configure provider with custom settings
   provider = get_provider(
       "openai",
       model="gpt-4",
       temperature=0.7,
       max_tokens=1000
   )

See individual module documentation for detailed API references. 