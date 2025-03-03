#!/usr/bin/env python3
"""
Example script for using the GitHub Repository SEO Optimizer programmatically.

This script demonstrates how to use the GitHub Repository SEO Optimizer
to optimize a single repository or all repositories for a user.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any

# Add the parent directory to the path to import the repo_seo package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import RepositoryOptimizer
from src.llm_providers import list_available_providers, check_provider_api_key


def setup_logging(verbose: bool = False):
    """Set up logging with the specified verbosity.
    
    Args:
        verbose: Whether to enable verbose logging.
    """
    log_level = "DEBUG" if verbose else "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def optimize_single_repository(owner: str, repo: str, provider: str = "local",
                              apply_changes: bool = False, github_token: str = None):
    """Optimize a single repository.
    
    Args:
        owner: The repository owner.
        repo: The repository name.
        provider: The name of the LLM provider to use.
        apply_changes: Whether to apply changes to the repository.
        github_token: The GitHub API token, or None to use the GitHub CLI.
    """
    print(f"Optimizing repository: {owner}/{repo}")
    
    # Initialize the optimizer
    optimizer = RepositoryOptimizer(
        provider_name=provider,
        apply_changes=apply_changes,
        sync_forks=True,
        github_token=github_token
    )
    
    # Optimize the repository
    try:
        result = optimizer.optimize_repository(owner, repo)
        
        # Print the optimization results
        print("\nOptimization Results:")
        print(f"Repository: {owner}/{repo}")
        print(f"Success: {result.get('success', False)}")
        
        changes = result.get("changes", {})
        if any(changes.values()):
            print("\nChanges:")
            for key, value in changes.items():
                if value:
                    print(f"- {key}: {value}")
        else:
            print("\nNo changes needed")
        
        # Print the new description and topics
        if changes.get("description"):
            print(f"\nNew Description: {result.get('new_description')}")
        
        if changes.get("topics"):
            print(f"\nNew Topics: {', '.join(result.get('new_topics', []))}")
        
        # Save the results to a file
        output_file = f"{repo}_optimization.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nResults saved to {output_file}")
        
    except Exception as e:
        print(f"Error optimizing repository: {e}")
        sys.exit(1)


def optimize_user_repositories(username: str, provider: str = "local",
                              apply_changes: bool = False, max_repos: int = 10,
                              github_token: str = None):
    """Optimize all repositories for a user.
    
    Args:
        username: The GitHub username.
        provider: The name of the LLM provider to use.
        apply_changes: Whether to apply changes to repositories.
        max_repos: The maximum number of repositories to optimize.
        github_token: The GitHub API token, or None to use the GitHub CLI.
    """
    print(f"Optimizing repositories for user: {username}")
    
    # Initialize the optimizer
    optimizer = RepositoryOptimizer(
        provider_name=provider,
        apply_changes=apply_changes,
        sync_forks=True,
        github_token=github_token
    )
    
    # Optimize the repositories
    try:
        results = optimizer.optimize_user_repositories(
            username=username,
            max_repos=max_repos
        )
        
        # Print summary
        print("\nOptimization Summary:")
        print(f"Processed {len(results)} repositories")
        
        success_count = sum(1 for r in results if r.get("success", False))
        print(f"Successfully optimized: {success_count}")
        
        error_count = sum(1 for r in results if not r.get("success", False))
        print(f"Errors: {error_count}")
        
        changes_count = sum(1 for r in results if any(r.get("changes", {}).values()))
        print(f"Repositories with changes: {changes_count}")
        
        if apply_changes:
            print("\nChanges have been applied to the repositories.")
        else:
            print("\nThis was a dry run. Use --apply to apply changes.")
        
    except Exception as e:
        print(f"Error optimizing repositories: {e}")
        sys.exit(1)


def main():
    """Main function for the example script."""
    parser = argparse.ArgumentParser(description="GitHub Repository SEO Optimizer Example")
    parser.add_argument("--owner", help="Repository owner (required for single repository)")
    parser.add_argument("--repo", help="Repository name (required for single repository)")
    parser.add_argument("--username", help="GitHub username (required for user repositories)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--provider", default="local", help="LLM provider to use (default: local)")
    parser.add_argument("--max-repos", type=int, default=10, help="Maximum number of repositories to optimize")
    parser.add_argument("--token", help="GitHub API token (default: use GitHub CLI)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Check if the provider is available
    if args.provider != "local" and not check_provider_api_key(args.provider):
        print(f"Error: API key for provider '{args.provider}' is not set.")
        print(f"Please set the appropriate environment variable.")
        sys.exit(1)
    
    # Check if we're optimizing a single repository or all repositories for a user
    if args.owner and args.repo:
        optimize_single_repository(
            owner=args.owner,
            repo=args.repo,
            provider=args.provider,
            apply_changes=args.apply,
            github_token=args.token
        )
    elif args.username:
        optimize_user_repositories(
            username=args.username,
            provider=args.provider,
            apply_changes=args.apply,
            max_repos=args.max_repos,
            github_token=args.token
        )
    else:
        print("Error: Either --owner and --repo, or --username must be provided.")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 