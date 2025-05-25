#!/usr/bin/env python3
"""
GitHub Repository SEO Optimizer - Main Entry Point

This script provides a unified interface for running the various commands
of the GitHub Repository SEO Optimizer.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def ensure_src_in_path():
    """Ensure the src directory is in the Python path."""
    src_dir = Path(__file__).parent / "src"
    if str(src_dir.absolute()) not in sys.path:
        sys.path.insert(0, str(src_dir.absolute()))

def run_optimization(args):
    """Run the repository optimization."""
    ensure_src_in_path()
    from src.run_optimization import main as run_optimization_main
    
    # Convert args to the format expected by run_optimization.py
    sys.argv = ["run_optimization.py"]
    if args.username:
        sys.argv.append(args.username)
    if args.apply:
        sys.argv.append("--apply")
    if args.provider:
        sys.argv.extend(["--provider", args.provider])
    if args.no_sync:
        sys.argv.append("--no-sync")
    
    # Run the optimization
    run_optimization_main()

def setup_commit_hook(args):
    """Set up the commit message hook."""
    ensure_src_in_path()
    from src.setup_commit_hook import main as setup_hook_main
    
    # Run the setup
    setup_hook_main()

def run_tests(args):
    """Run the tests."""
    # Check if run_tests.sh exists and is executable
    run_tests_script = Path(__file__).parent / "run_tests.sh"
    if run_tests_script.exists():
        try:
            # Make the script executable if it's not already
            if not os.access(run_tests_script, os.X_OK):
                os.chmod(run_tests_script, 0o755)
            
            # Run the script
            subprocess.run([str(run_tests_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running tests: {e}")
            sys.exit(1)
    else:
        # Fall back to running pytest directly
        try:
            subprocess.run(["pytest", "--cov=src"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running tests: {e}")
            sys.exit(1)

def check_api_keys(args):
    """Check the API keys."""
    # Check if check_api_keys.sh exists and is executable
    check_keys_script = Path(__file__).parent / "check_api_keys.sh"
    if check_keys_script.exists():
        try:
            # Make the script executable if it's not already
            if not os.access(check_keys_script, os.X_OK):
                os.chmod(check_keys_script, 0o755)
            
            # Run the script
            subprocess.run([str(check_keys_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error checking API keys: {e}")
            sys.exit(1)
    else:
        print("Error: check_api_keys.sh script not found.")
        sys.exit(1)

def install_dependencies(args):
    """Install dependencies."""
    # Check if install_dependencies.sh exists and is executable
    install_script = Path(__file__).parent / "install_dependencies.sh"
    if install_script.exists():
        try:
            # Make the script executable if it's not already
            if not os.access(install_script, os.X_OK):
                os.chmod(install_script, 0o755)
            
            # Run the script
            subprocess.run([str(install_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("Error: install_dependencies.sh script not found.")
        sys.exit(1)

def cleanup_repo(args):
    """Clean up the repository."""
    # Check if cleanup.py exists and is executable
    cleanup_script = Path(__file__).parent / "cleanup.py"
    if cleanup_script.exists():
        try:
            # Make the script executable if it's not already
            if not os.access(cleanup_script, os.X_OK):
                os.chmod(cleanup_script, 0o755)
            
            # Run the script
            subprocess.run([sys.executable, str(cleanup_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cleaning up repository: {e}")
            sys.exit(1)
    else:
        print("Error: cleanup.py script not found.")
        sys.exit(1)

def make_executable(args):
    """Make scripts executable."""
    # Check if make_executable.py exists
    make_executable_script = Path(__file__).parent / "make_executable.py"
    if make_executable_script.exists():
        try:
            # Run the script
            subprocess.run([sys.executable, str(make_executable_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error making scripts executable: {e}")
            sys.exit(1)
    else:
        print("Error: make_executable.py script not found.")
        sys.exit(1)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="GitHub Repository SEO Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize repositories for a user
  python repo-seo.py optimize chenxingqiang
  
  # Set up the commit message hook
  python repo-seo.py setup-hook
  
  # Run tests
  python repo-seo.py test
  
  # Check API keys
  python repo-seo.py check-keys
  
  # Install dependencies
  python repo-seo.py install
  
  # Clean up repository
  python repo-seo.py cleanup
  
  # Make scripts executable
  python repo-seo.py make-executable
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Optimize GitHub repositories")
    optimize_parser.add_argument("username", nargs="?", help="GitHub username")
    optimize_parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    optimize_parser.add_argument("--provider", help="Specify LLM provider (default: local)")
    optimize_parser.add_argument("--no-sync", action="store_true", help="Don't sync forked repositories")
    optimize_parser.set_defaults(func=run_optimization)
    
    # Setup hook command
    setup_hook_parser = subparsers.add_parser("setup-hook", help="Set up commit message hook")
    setup_hook_parser.set_defaults(func=setup_commit_hook)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.set_defaults(func=run_tests)
    
    # Check keys command
    check_keys_parser = subparsers.add_parser("check-keys", help="Check API keys")
    check_keys_parser.set_defaults(func=check_api_keys)
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.set_defaults(func=install_dependencies)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up repository")
    cleanup_parser.set_defaults(func=cleanup_repo)
    
    # Make executable command
    make_executable_parser = subparsers.add_parser("make-executable", help="Make scripts executable")
    make_executable_parser.set_defaults(func=make_executable)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main() 