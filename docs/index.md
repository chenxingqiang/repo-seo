# GitHub Repository SEO Optimizer Documentation

Welcome to the documentation for the GitHub Repository SEO Optimizer. This tool helps optimize GitHub repositories for better discoverability through improved descriptions, topics, and documentation.

## Table of Contents

1. [Main Script](main_script.md)
2. [LLM Providers](llm_providers.md)
3. [Topic Validation](topic_validation.md)
4. [Target Goals](target.md)

## Overview

The GitHub Repository SEO Optimizer is a tool that analyzes GitHub repositories and optimizes them for search engine visibility by improving descriptions, keywords, and documentation.

### Key Features

1. **Repository Analysis**: Analyzes GitHub repositories to identify optimization opportunities
2. **Content Analysis**: Analyzes repository languages, topics, and README content
3. **SEO Generation**: Creates optimized descriptions and topics based on analysis
4. **README Generation**: Generates comprehensive README files for repositories that lack them
5. **Multiple LLM Providers**: Supports various language models for content generation:
   - Local rule-based processing (no API key required)
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude)
   - Ollama (local LLMs)

## Installation

```bash
# Clone the repository
git clone https://github.com/chenxingqiang/repo-seo.git
cd repo-seo

# Install dependencies
pip install -r requirements.txt

# Ensure GitHub CLI is installed
# https://cli.github.com/manual/installation
```

## Quick Start

```bash
# Basic usage - optimize all repositories for a user
./run_seo.sh --username <github_username>

# Optimize a specific repository
python repo_seo.py <github_username> --repo <repository_name>

# Show changes without applying them (dry run)
python repo_seo.py <github_username> --dry-run

# Use a specific LLM provider
python repo_seo.py <github_username> --provider openai
```

## Examples

The `examples` directory contains example scripts demonstrating how to use the GitHub Repository SEO Optimizer:

```bash
# Run the LLM provider example
python examples/use_providers.py
```

## Testing

```bash
# Run all tests with coverage report
./run_tests.sh

# Test specific LLM providers
python test_providers.py local
python test_providers.py openai
python test_providers.py ollama
python test_providers.py anthropic
python test_providers.py all
```

## Project Structure

```
repo-seo/
├── repo_seo.py          # Main script
├── run_seo.sh           # Shell script runner
├── test_providers.py    # Script to test LLM providers
├── run_tests.sh         # Script to run all tests
├── requirements.txt     # Dependencies
├── src/                 # Source code
│   ├── llm_providers/   # LLM provider implementations
│   ├── github_client/   # GitHub API client
│   ├── content_analyzer/ # Content analysis tools
│   └── seo_generator/   # SEO content generation
├── tests/               # Test suite
├── examples/            # Example scripts
└── docs/                # Documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 