#!/usr/bin/env python3
"""
Command-line interface for the GitHub Repository SEO Optimizer.

This module provides a command-line interface for optimizing GitHub repositories,
including commands for optimizing repositories, setting up commit hooks, and more.
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any, Optional

from .main import RepositoryOptimizer
from .llm_providers import list_available_providers, check_provider_api_key
from .utils.common import is_github_cli_installed, is_github_cli_authenticated

# Configure logging
logger = logging.getLogger(__name__)


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


def check_prerequisites():
    """Check if all prerequisites are met.
    
    Returns:
        True if all prerequisites are met, False otherwise.
    """
    # Check if GitHub CLI is installed
    if not is_github_cli_installed():
        print("Error: GitHub CLI (gh) is not installed.")
        print("Please install it from: https://cli.github.com/manual/installation")
        return False
    
    # Check if GitHub CLI is authenticated
    if not is_github_cli_authenticated():
        print("Error: Not authenticated with GitHub CLI.")
        print("Please run: gh auth login")
        return False
    
    return True


def optimize_command(args):
    """Handle the optimize command.
    
    Args:
        args: The command-line arguments.
    """
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Check if the provider is available
    if args.provider != "local" and not check_provider_api_key(args.provider):
        print(f"Error: API key for provider '{args.provider}' is not set.")
        print(f"Please set the appropriate environment variable.")
        sys.exit(1)
    
    # Initialize the optimizer
    optimizer = RepositoryOptimizer(
        provider_name=args.provider,
        apply_changes=args.apply,
        sync_forks=not args.no_sync,
        github_token=args.token
    )
    
    # Optimize repositories
    try:
        results = optimizer.optimize_user_repositories(
            username=args.username,
            max_repos=args.max_repos
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
        
        if args.apply:
            print("\nChanges have been applied to the repositories.")
        else:
            print("\nThis was a dry run. Use --apply to apply changes.")
        
    except Exception as e:
        logger.error(f"Error optimizing repositories: {e}")
        sys.exit(1)


def setup_hook_command(args):
    """Handle the setup-hook command.
    
    Args:
        args: The command-line arguments.
    """
    # Import the setup_commit_hook module
    try:
        from .setup_commit_hook import main as setup_hook_main
    except ImportError:
        print("Error: Could not import setup_commit_hook module.")
        sys.exit(1)
    
    # Run the setup
    try:
        setup_hook_main()
    except Exception as e:
        logger.error(f"Error setting up commit hook: {e}")
        sys.exit(1)


def list_providers_command(args):
    """Handle the list-providers command.
    
    Args:
        args: The command-line arguments.
    """
    # Get available providers
    providers = list_available_providers()
    
    print("Available LLM Providers:")
    print("------------------------")
    
    for name, info in providers.items():
        available = info.get("available", False)
        status = "Available" if available else "Not available"
        
        if available:
            api_key = check_provider_api_key(name)
            if api_key:
                status += " (API key set)"
            else:
                status += " (API key not set)"
        else:
            error = info.get("error", "")
            status += f" ({error})"
        
        print(f"{name}: {status}")
    
    print("\nTo use a specific provider, set the appropriate API key and use:")
    print("  python -m repo_seo optimize <username> --provider <provider_name>")


def check_auth_command(args):
    """Handle the check-auth command.
    
    Args:
        args: The command-line arguments.
    """
    # Check if GitHub CLI is installed
    if not is_github_cli_installed():
        print("Error: GitHub CLI (gh) is not installed.")
        print("Please install it from: https://cli.github.com/manual/installation")
        sys.exit(1)
    
    # Check if GitHub CLI is authenticated
    if is_github_cli_authenticated():
        print("GitHub CLI is authenticated.")
    else:
        print("GitHub CLI is not authenticated.")
        print("Please run: gh auth login")
        sys.exit(1)


def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(description="GitHub Repository SEO Optimizer")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize GitHub repositories")
    optimize_parser.add_argument("username", help="GitHub username")
    optimize_parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    optimize_parser.add_argument("--provider", default="local", help="LLM provider to use (default: local)")
    optimize_parser.add_argument("--no-sync", action="store_true", help="Don't sync forked repositories")
    optimize_parser.add_argument("--max-repos", type=int, default=100, help="Maximum number of repositories to optimize")
    optimize_parser.add_argument("--token", help="GitHub API token (default: use GitHub CLI)")
    optimize_parser.set_defaults(func=optimize_command)
    
    # Setup hook command
    setup_hook_parser = subparsers.add_parser("setup-hook", help="Set up commit message hook")
    setup_hook_parser.set_defaults(func=setup_hook_command)
    
    # List providers command
    list_providers_parser = subparsers.add_parser("list-providers", help="List available LLM providers")
    list_providers_parser.set_defaults(func=list_providers_command)
    
    # Check auth command
    check_auth_parser = subparsers.add_parser("check-auth", help="Check GitHub CLI authentication")
    check_auth_parser.set_defaults(func=check_auth_command)
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Run the command
    args.func(args)


if __name__ == "__main__":
    main()
