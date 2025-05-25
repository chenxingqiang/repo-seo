#!/usr/bin/env python3
"""
Cleanup script to organize the repository structure by removing duplicate files
and ensuring consistent file naming and organization.
"""

import os
import shutil
import sys

def print_colored(message, color_code):
    """Print a message with color."""
    print(f"\033[{color_code}m{message}\033[0m")

def print_success(message):
    """Print a success message in green."""
    print_colored(message, "32")

def print_warning(message):
    """Print a warning message in yellow."""
    print_colored(message, "33")

def print_error(message):
    """Print an error message in red."""
    print_colored(message, "31")

def print_info(message):
    """Print an info message in blue."""
    print_colored(message, "34")

def confirm_action(message):
    """Ask for confirmation before proceeding with an action."""
    response = input(f"{message} (y/n): ").lower()
    return response == 'y' or response == 'yes'

def remove_duplicate_files():
    """Remove duplicate files from the repository."""
    duplicates = [
        # List of duplicate files to remove
        ("run_optimization.py", "src/run_optimization.py"),
        ("setup_commit_hook.py", "src/setup_commit_hook.py"),
        ("repo_seo.py", "repo-seo.py"),  # Keep the hyphenated version
        ("README_COMMIT_FIXER.md", "docs/README_COMMIT_FIXER.md"),
    ]
    
    for original, duplicate in duplicates:
        if os.path.exists(original) and os.path.exists(duplicate):
            print_info(f"Found duplicate: {original} and {duplicate}")
            if confirm_action(f"Remove {original} (duplicate of {duplicate})?"):
                try:
                    os.remove(original)
                    print_success(f"Removed {original}")
                except Exception as e:
                    print_error(f"Error removing {original}: {str(e)}")
        elif os.path.exists(original) and not os.path.exists(duplicate):
            print_info(f"Found file to move: {original} -> {duplicate}")
            if confirm_action(f"Move {original} to {duplicate}?"):
                try:
                    os.makedirs(os.path.dirname(duplicate), exist_ok=True)
                    shutil.move(original, duplicate)
                    print_success(f"Moved {original} to {duplicate}")
                except Exception as e:
                    print_error(f"Error moving {original} to {duplicate}: {str(e)}")

def ensure_directory_structure():
    """Ensure the repository has the correct directory structure."""
    directories = [
        "src",
        "src/llm_providers",
        "src/github_client",
        "src/content_analyzer",
        "src/seo_generator",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "examples",
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            print_info(f"Creating directory: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                # Create __init__.py in Python package directories
                if directory.startswith("src") or directory.startswith("tests"):
                    init_file = os.path.join(directory, "__init__.py")
                    if not os.path.exists(init_file):
                        with open(init_file, "w") as f:
                            f.write("# This file is required to make Python treat this directory as a package\n")
                        print_success(f"Created {init_file}")
                print_success(f"Created directory: {directory}")
            except Exception as e:
                print_error(f"Error creating directory {directory}: {str(e)}")

def ensure_consistent_naming():
    """Ensure consistent file naming throughout the repository."""
    # Files to rename (old_name, new_name)
    files_to_rename = [
        # Add files that need to be renamed for consistency
    ]
    
    for old_name, new_name in files_to_rename:
        if os.path.exists(old_name) and not os.path.exists(new_name):
            print_info(f"Renaming: {old_name} -> {new_name}")
            if confirm_action(f"Rename {old_name} to {new_name}?"):
                try:
                    os.makedirs(os.path.dirname(new_name), exist_ok=True)
                    shutil.move(old_name, new_name)
                    print_success(f"Renamed {old_name} to {new_name}")
                except Exception as e:
                    print_error(f"Error renaming {old_name} to {new_name}: {str(e)}")

def main():
    """Main function to run the cleanup script."""
    print_info("GitHub Repository SEO Optimizer - Repository Cleanup")
    print_info("==================================================")
    
    if not confirm_action("This script will clean up the repository structure. Continue?"):
        print_warning("Cleanup aborted.")
        return
    
    # Ensure the directory structure is correct
    ensure_directory_structure()
    
    # Remove duplicate files
    remove_duplicate_files()
    
    # Ensure consistent naming
    ensure_consistent_naming()
    
    print_success("Repository cleanup completed!")
    print_info("You may want to run the following commands to verify the changes:")
    print_info("  git status")
    print_info("  git diff")
    print_info("  git add .")
    print_info("  git commit -m 'Cleaned up repository structure'")

if __name__ == "__main__":
    main() 