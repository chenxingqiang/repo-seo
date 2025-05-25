#!/usr/bin/env python3
"""
Example script demonstrating how to use different LLM providers.
"""

import sys
import os
import argparse

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.llm_providers import get_provider
except ImportError:
    print("Error: Could not import the LLM providers module.")
    print("Make sure you're running this script from the repository root or examples directory.")
    sys.exit(1)

def test_provider(provider_name):
    """Test a specific LLM provider."""
    print(f"\nTesting {provider_name} provider...")

    # Sample repository data
    repo_name = "repo-seo"
    languages = ["Python", "Shell"]
    topics = ["github", "seo", "repository"]
    readme = """# GitHub Repository SEO Optimizer

A tool to optimize GitHub repositories for better discoverability through improved descriptions, topics, and documentation.

## Features

1. **Repository Analysis**: Analyzes GitHub repositories to identify optimization opportunities
2. **Content Analysis**: Analyzes repository languages, topics, and README content
3. **SEO Generation**: Creates optimized descriptions and topics based on analysis
4. **README Generation**: Generates comprehensive README files for repositories that lack them
"""

    try:
        # Initialize the provider
        provider = get_provider(provider_name)

        # Generate description
        print("\nGenerating description...")
        description = provider.generate_description(
            repo_name=repo_name,
            languages=languages,
            topics=topics,
            readme=readme
        )
        print(f"Description: {description}")

        # Generate topics
        print("\nGenerating topics...")
        new_topics = provider.generate_topics(
            repo_name=repo_name,
            languages=languages,
            current_topics=topics,
            readme=readme
        )
        print(f"Topics: {', '.join(new_topics)}")

        # Analyze README
        print("\nAnalyzing README...")
        analysis = provider.analyze_readme(readme)
        print(f"Summary: {analysis.get('summary', '')}")
        print(f"Extracted topics: {', '.join(analysis.get('topics', []))}")
        print(f"Named entities: {', '.join(analysis.get('entities', []))}")

        print(f"\n{provider_name} provider test completed!")

    except Exception as e:
        print(f"Error testing {provider_name} provider: {str(e)}")
        print("Make sure you have the necessary API keys and dependencies installed.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test LLM providers for GitHub Repository SEO Optimizer")
    parser.add_argument("provider", nargs="?", default="local",
                        choices=["local", "openai", "ollama", "anthropic", "deepseek", "gemini", "zhipu", "qianwen", "all"],
                        help="Provider to test (default: local)")

    args = parser.parse_args()

    if args.provider == "all":
        # Test all providers
        providers = ["local", "openai", "ollama", "anthropic", "deepseek", "gemini", "zhipu", "qianwen"]
        for provider in providers:
            try:
                test_provider(provider)
            except Exception as e:
                print(f"Error testing {provider} provider: {str(e)}")
    else:
        # Test a specific provider
        test_provider(args.provider)

if __name__ == "__main__":
    main()