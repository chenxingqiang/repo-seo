#!/usr/bin/env python3
"""
Setup commit hook module for the GitHub Repository SEO Optimizer.

This module provides functionality for setting up a Git commit hook
that automatically optimizes repository content when committing changes.
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Commit hook script template
COMMIT_HOOK_TEMPLATE = """#!/bin/sh
#
# pre-commit hook for GitHub Repository SEO Optimizer
# This hook automatically optimizes repository content when committing changes.

# Get the repository name from the remote URL
REPO_NAME=$(basename -s .git $(git config --get remote.origin.url))
REPO_OWNER=$(git config --get remote.origin.url | sed -n 's/.*github.com[:/]\\([^/]*\\).*/\\1/p')

# Run the optimizer
echo "Running GitHub Repository SEO Optimizer..."
python -m repo_seo optimize $REPO_OWNER --provider {provider} {apply_flag} --max-repos 1

# Continue with the commit
exit 0
"""


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


def is_git_repository() -> bool:
    """Check if the current directory is a Git repository.
    
    Returns:
        True if the current directory is a Git repository, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_git_hooks_dir() -> Optional[Path]:
    """Get the Git hooks directory for the current repository.
    
    Returns:
        The path to the Git hooks directory, or None if not found.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        git_dir = result.stdout.strip()
        hooks_dir = Path(git_dir) / "hooks"
        return hooks_dir
    except subprocess.CalledProcessError:
        return None


def setup_commit_hook(provider: str = "local", apply_changes: bool = False) -> bool:
    """Set up a Git commit hook for repository optimization.
    
    Args:
        provider: The name of the LLM provider to use.
        apply_changes: Whether to apply changes to repositories.
        
    Returns:
        True if the hook was set up successfully, False otherwise.
    """
    # Check if the current directory is a Git repository
    if not is_git_repository():
        logger.error("Not a Git repository")
        return False
    
    # Get the Git hooks directory
    hooks_dir = get_git_hooks_dir()
    if not hooks_dir:
        logger.error("Could not find Git hooks directory")
        return False
    
    # Create the hooks directory if it doesn't exist
    hooks_dir.mkdir(exist_ok=True)
    
    # Create the pre-commit hook file
    pre_commit_hook_path = hooks_dir / "pre-commit"
    
    # Generate the hook script
    apply_flag = "--apply" if apply_changes else ""
    hook_script = COMMIT_HOOK_TEMPLATE.format(
        provider=provider,
        apply_flag=apply_flag
    )
    
    # Write the hook script to the file
    try:
        with open(pre_commit_hook_path, "w") as f:
            f.write(hook_script)
        
        # Make the hook executable
        os.chmod(pre_commit_hook_path, 0o755)
        
        logger.info(f"Commit hook set up at {pre_commit_hook_path}")
        return True
    except Exception as e:
        logger.error(f"Error setting up commit hook: {e}")
        return False


def main():
    """Main function for the setup commit hook module."""
    parser = argparse.ArgumentParser(description="Set up a Git commit hook for repository optimization")
    parser.add_argument("--provider", default="local", help="LLM provider to use (default: local)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Set up the commit hook
    success = setup_commit_hook(
        provider=args.provider,
        apply_changes=args.apply
    )
    
    if success:
        print("Commit hook set up successfully")
        print("The hook will run automatically when you commit changes")
        
        if args.apply:
            print("Changes will be applied automatically")
        else:
            print("Changes will NOT be applied automatically (dry run)")
            print("Use --apply to apply changes")
    else:
        print("Failed to set up commit hook")
        sys.exit(1)


if __name__ == "__main__":
    main() 