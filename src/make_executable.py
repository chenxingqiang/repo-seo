#!/usr/bin/env python3
"""
Script to make all Python and shell scripts executable.
"""

import os
import stat
import sys

def make_executable(file_path):
    """Make a file executable by adding the execute permission."""
    current_permissions = os.stat(file_path).st_mode
    os.chmod(file_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return os.access(file_path, os.X_OK)

def find_scripts(directory="."):
    """Find all Python and shell scripts in the given directory and its subdirectories."""
    scripts = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".sh"):
                scripts.append(os.path.join(root, file))
    return scripts

def main():
    """Make all Python and shell scripts executable."""
    print("Making scripts executable...")
    
    # Find all scripts
    scripts = find_scripts()
    
    # Make each script executable
    success_count = 0
    for script in scripts:
        try:
            if make_executable(script):
                print(f"✓ Made executable: {script}")
                success_count += 1
            else:
                print(f"✗ Failed to make executable: {script}")
        except Exception as e:
            print(f"✗ Error processing {script}: {str(e)}")
    
    print(f"\nMade {success_count} of {len(scripts)} scripts executable.")
    
    # Special handling for important scripts
    important_scripts = [
        "repo-seo.py",
        "install_dependencies.sh",
        "check_api_keys.sh",
        "run_tests.sh",
        "cleanup.py"
    ]
    
    print("\nChecking important scripts...")
    for script in important_scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✓ {script} is executable")
            else:
                try:
                    make_executable(script)
                    print(f"✓ Made executable: {script}")
                except Exception as e:
                    print(f"✗ Error making {script} executable: {str(e)}")
        else:
            print(f"✗ {script} not found")
    
    print("\nDone!")

if __name__ == "__main__":
    main() 