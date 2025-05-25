#!/usr/bin/env python3
"""
Script to run the GitHub Repository SEO Optimizer for a specific user's GitHub repositories.
"""

import sys
import json
import subprocess
import time
from typing import List, Dict, Any

def run_command(command: List[str]) -> tuple:
    """Run a command and return the output."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def get_user_repos(username: str) -> List[Dict[str, Any]]:
    """Get a list of repositories for a GitHub user."""
    stdout, stderr, returncode = run_command(["gh", "repo", "list", username, "--json", "name,description,url,isFork", "--limit", "100"])

    if returncode != 0:
        print(f"Error fetching repositories: {stderr}")
        return []

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print(f"Error parsing repository list: {stdout}")
        return []

def is_fork(username: str, repo_name: str) -> bool:
    """Check if a repository is a fork."""
    stdout, stderr, returncode = run_command(["gh", "repo", "view", f"{username}/{repo_name}", "--json", "isFork"])

    if returncode != 0:
        print(f"Error checking if repository is a fork: {stderr}")
        return False

    try:
        data = json.loads(stdout)
        return data.get("isFork", False)
    except json.JSONDecodeError:
        print(f"Error parsing repository data: {stdout}")
        return False

def get_fork_parent(username: str, repo_name: str) -> str:
    """Get the parent repository of a fork."""
    stdout, stderr, returncode = run_command(["gh", "repo", "view", f"{username}/{repo_name}", "--json", "parent"])

    if returncode != 0:
        print(f"Error getting fork parent: {stderr}")
        return ""

    try:
        data = json.loads(stdout)
        parent = data.get("parent", {})
        if parent:
            return f"{parent.get('owner', {}).get('login', '')}/{parent.get('name', '')}"
        return ""
    except json.JSONDecodeError:
        print(f"Error parsing repository data: {stdout}")
        return ""

def sync_fork(username: str, repo_name: str) -> bool:
    """Sync a forked repository with its upstream."""
    print(f"Syncing forked repository: {username}/{repo_name}")

    # Get the parent repository
    parent = get_fork_parent(username, repo_name)
    if not parent:
        print("Could not determine parent repository.")
        return False

    print(f"Parent repository: {parent}")

    # Sync the fork with its parent
    stdout, stderr, returncode = run_command(["gh", "repo", "sync", f"{username}/{repo_name}"])

    if returncode != 0:
        print(f"Error syncing fork: {stderr}")
        return False

    print(f"Successfully synced {username}/{repo_name} with {parent}")
    return True

def optimize_repo(username: str, repo_name: str, dry_run: bool = True, llm_provider: str = "local", sync_forks: bool = True):
    """Optimize a single repository."""
    from src.repo_seo import optimize_repository

    print(f"\nOptimizing repository: {username}/{repo_name}")
    print("=" * 50)

    # Check if the repository is a fork and sync it if requested
    if sync_forks and is_fork(username, repo_name):
        print(f"Repository {repo_name} is a fork.")
        if sync_fork(username, repo_name):
            print("Fork synced successfully.")
            # Give GitHub some time to update the repository data
            print("Waiting a moment for GitHub to update...")
            time.sleep(2)
        else:
            print("Failed to sync fork. Continuing with optimization anyway.")

    result = optimize_repository(username, repo_name, dry_run=dry_run, llm_provider=llm_provider)

    print("\nOptimization Results:")
    print(f"Repository: {result['repository']}")

    print("\nDescription:")
    print(f"Before: {result['description']['before']}")
    print(f"After: {result['description']['after']}")

    print("\nTopics:")
    print(f"Before: {', '.join(result['topics']['before'])}")
    print(f"After: {', '.join(result['topics']['after'])}")

    if result['readme']['updated']:
        print("\nREADME was updated.")
    else:
        print("\nREADME was not updated.")

    if dry_run:
        print("\nThis was a dry run. No changes were applied.")
    else:
        print("\nChanges have been applied to the repository.")

    return result

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python run_optimization.py <github_username> [--apply] [--provider <provider_name>] [--no-sync]")
        print("Options:")
        print("  --apply            Apply changes (default is dry run)")
        print("  --provider <name>  Specify LLM provider (default: local)")
        print("  --no-sync          Don't sync forked repositories")
        sys.exit(1)

    username = sys.argv[1]
    dry_run = True
    llm_provider = "local"
    sync_forks = True

    # Parse command line arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--apply":
            dry_run = False
        elif sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
            llm_provider = sys.argv[i + 1]
            i += 1
        elif sys.argv[i] == "--no-sync":
            sync_forks = False
        i += 1

    print(f"Fetching repositories for GitHub user: {username}")
    repos = get_user_repos(username)

    if not repos:
        print("No repositories found or error fetching repositories.")
        sys.exit(1)

    print(f"Found {len(repos)} repositories.")

    for i, repo in enumerate(repos):
        fork_status = " (fork)" if repo.get("isFork", False) else ""
        print(f"{i+1}. {repo['name']}{fork_status} - {repo['description']}")

    # Ask which repositories to optimize
    print("\nEnter repository numbers to optimize (comma-separated, or 'all' for all repositories):")
    selection = input("> ")

    selected_repos = []
    if selection.lower() == "all":
        selected_repos = repos
    else:
        try:
            indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
            selected_repos = [repos[idx] for idx in indices if 0 <= idx < len(repos)]
        except (ValueError, IndexError):
            print("Invalid selection. Please enter valid repository numbers.")
            sys.exit(1)

    print(f"\nOptimizing {len(selected_repos)} repositories with {llm_provider} provider.")
    print(f"Dry run: {dry_run}")
    print(f"Sync forks: {sync_forks}")

    results = []
    for repo in selected_repos:
        try:
            result = optimize_repo(username, repo["name"], dry_run, llm_provider, sync_forks)
            results.append(result)
        except Exception as e:
            print(f"Error optimizing {repo['name']}: {str(e)}")

    print("\nOptimization complete!")
    print(f"Optimized {len(results)} repositories.")

    if dry_run:
        print("\nThis was a dry run. To apply changes, run with --apply option.")

if __name__ == "__main__":
    main()