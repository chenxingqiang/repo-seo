"""
Commit Message Fixer

This module provides a class to fix commit messages according to the Conventional Commits specification.
"""

import re
from typing import List, Dict, Any, Optional


class CommitMessageFixer:
    """Fix commit messages according to the Conventional Commits specification."""
    
    def __init__(self):
        """Initialize the commit message fixer."""
        self.types = [
            "feat",     # A new feature
            "fix",      # A bug fix
            "docs",     # Documentation only changes
            "style",    # Changes that do not affect the meaning of the code
            "refactor", # A code change that neither fixes a bug nor adds a feature
            "test",     # Adding missing tests or correcting existing tests
            "chore",    # Changes to the build process or auxiliary tools
            "perf",     # A code change that improves performance
            "ci",       # Changes to CI configuration files and scripts
            "build",    # Changes that affect the build system or external dependencies
            "revert",   # Reverts a previous commit
        ]
    
    def print_commit_guide(self):
        """Print a guide for writing commit messages."""
        print("Conventional Commits Guide")
        print("=========================")
        print("")
        print("Format: <type>[optional scope]: <description>")
        print("")
        print("Types:")
        for type_name in self.types:
            print(f"  - {type_name}")
        print("")
        print("Examples:")
        print("  - feat: add new feature")
        print("  - fix: resolve issue with login")
        print("  - docs: update README")
        print("  - style: format code")
        print("  - refactor: restructure authentication")
        print("  - test: add tests for user service")
        print("  - chore: update dependencies")
        print("")
        print("For more information, see https://www.conventionalcommits.org/")
    
    def fix_commit_message(self, message: str) -> str:
        """
        Fix a commit message according to the Conventional Commits specification.
        
        Args:
            message: The commit message to fix.
            
        Returns:
            The fixed commit message.
        """
        # Check if the message already follows the conventional format
        if re.match(r'^[a-z]+(\([a-z0-9-]+\))?: .+', message):
            return message
        
        # Check if the message has a type but no description
        type_match = re.match(r'^([a-z]+)(\([a-z0-9-]+\))?$', message)
        if type_match:
            type_name = type_match.group(1)
            scope = type_match.group(2) or ""
            if type_name in self.types:
                return f"{type_name}{scope}: "
        
        # If the message doesn't have a type, add "feat: " as the default
        return f"feat: {message}"
    
    def validate_commit_message(self, message: str) -> bool:
        """
        Validate a commit message according to the Conventional Commits specification.
        
        Args:
            message: The commit message to validate.
            
        Returns:
            True if the message is valid, False otherwise.
        """
        # Check if the message follows the conventional format
        match = re.match(r'^([a-z]+)(\([a-z0-9-]+\))?: .+', message)
        if not match:
            return False
        
        # Check if the type is valid
        type_name = match.group(1)
        return type_name in self.types 