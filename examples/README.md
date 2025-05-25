# Examples for GitHub Repository SEO Optimizer

This directory contains example scripts demonstrating how to use the GitHub Repository SEO Optimizer with different LLM providers and for various use cases.

## Available Examples

### `use_providers.py`

This script demonstrates how to use different LLM providers to generate SEO content for GitHub repositories.

#### Usage

```bash
# Test the local provider (no API key needed)
python examples/use_providers.py local

# Test a specific provider
python examples/use_providers.py openai    # Requires OPENAI_API_KEY
python examples/use_providers.py anthropic # Requires ANTHROPIC_API_KEY
python examples/use_providers.py gemini    # Requires GEMINI_API_KEY or GOOGLE_API_KEY
python examples/use_providers.py ollama    # Requires Ollama running locally
python examples/use_providers.py deepseek  # Requires DEEPSEEK_API_KEY
python examples/use_providers.py zhipu     # Requires ZHIPU_API_KEY
python examples/use_providers.py qianwen   # Requires QIANWEN_API_KEY

# Test all available providers
python examples/use_providers.py all
```

#### Example Output

```
Testing local provider...

Generating description...
Description: A Python tool to optimize GitHub repositories for better discoverability through improved descriptions, topics, and documentation.

Generating topics...
Topics: github, seo, repository, optimization, python, automation, metadata, description, topics, readme

Analyzing README...
Summary: A tool that analyzes and optimizes GitHub repositories for better discoverability
Extracted topics: repository, analysis, seo, documentation, optimization
Named entities: GitHub, Repository, SEO, Optimizer

local provider test completed!
```

## Running the Examples

Before running the examples, make sure you have:

1. Installed all required dependencies:
   ```bash
   ./install_dependencies.sh
   ```

2. Set up the necessary API keys for the providers you want to test:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   export ANTHROPIC_API_KEY=your_api_key_here
   # etc.
   ```

3. Made the example scripts executable:
   ```bash
   python make_executable.py
   # or
   chmod +x examples/*.py
   ```

## Creating Your Own Examples

You can create your own examples by:

1. Creating a new Python script in this directory
2. Importing the necessary modules from the main package:
   ```python
   import sys
   import os
   
   # Add the parent directory to the path
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   
   # Import the modules you need
   from src.llm_providers import get_provider
   ```

3. Using the API to interact with the SEO optimizer

## API Usage Example

```python
# Initialize a provider
provider = get_provider("openai")  # or any other supported provider

# Generate a description
description = provider.generate_description(
    repo_name="my-awesome-repo",
    languages=["Python", "JavaScript"],
    topics=["web", "api"],
    readme="# My Awesome Repo\n\nThis is a web API built with Python and JavaScript."
)

# Generate topics
topics = provider.generate_topics(
    repo_name="my-awesome-repo",
    languages=["Python", "JavaScript"],
    current_topics=["web", "api"],
    readme="# My Awesome Repo\n\nThis is a web API built with Python and JavaScript."
)

# Analyze a README
analysis = provider.analyze_readme(
    "# My Awesome Repo\n\nThis is a web API built with Python and JavaScript."
)
```

## Additional Resources

For more information on using the GitHub Repository SEO Optimizer, see:

- [Main README](../README.md)
- [LLM Providers Documentation](../docs/llm_providers.md)
- [API Documentation](../docs/index.md) 