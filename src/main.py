#!/usr/bin/env python3
"""
Main application logic for the GitHub Repository SEO Optimizer.

This module provides the main functionality for optimizing GitHub repositories,
including fetching repository information, analyzing content, and applying changes.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime

from .config import config
from .github_client import GitHubCliClient, GitHubApiClient
from .content_analyzer import ContentAnalyzer
from .seo_generator import SEOGenerator
from .utils.common import save_json, generate_timestamp

# Configure logging
logger = logging.getLogger(__name__)


class RepositoryOptimizer:
    """Repository optimizer for GitHub repositories."""
    
    def __init__(self, provider_name: str = "local", apply_changes: bool = False, 
                sync_forks: bool = True, github_token: Optional[str] = None):
        """Initialize the repository optimizer.
        
        Args:
            provider_name: The name of the LLM provider to use.
            apply_changes: Whether to apply changes to repositories.
            sync_forks: Whether to sync forked repositories with their upstream.
            github_token: The GitHub API token, or None to use the GitHub CLI.
        """
        self.provider_name = provider_name
        self.apply_changes = apply_changes
        self.sync_forks = sync_forks
        
        # Initialize GitHub client
        if github_token:
            self.github = GitHubApiClient(token=github_token)
            logger.info("Using GitHub API client")
        else:
            self.github = GitHubCliClient()
            logger.info("Using GitHub CLI client")
        
        # Initialize content analyzer
        self.analyzer = ContentAnalyzer()
        
        # Initialize SEO generator
        self.generator = SEOGenerator(provider_name=provider_name)
        
        logger.info(f"Initialized repository optimizer with provider: {provider_name}")
        logger.info(f"Apply changes: {apply_changes}")
        logger.info(f"Sync forks: {sync_forks}")
    
    def optimize_user_repositories(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """Optimize all repositories for a user.
        
        Args:
            username: The GitHub username.
            max_repos: The maximum number of repositories to optimize.
            
        Returns:
            A list of optimization results.
        """
        logger.info(f"Optimizing repositories for user: {username}")
        
        # Get the user's repositories
        repositories = self.github.get_user_repositories(username)
        
        if not repositories:
            logger.warning(f"No repositories found for user: {username}")
            return []
        
        logger.info(f"Found {len(repositories)} repositories")
        
        # Limit the number of repositories
        if len(repositories) > max_repos:
            logger.info(f"Limiting to {max_repos} repositories")
            repositories = repositories[:max_repos]
        
        # Optimize each repository
        results = []
        for i, repo in enumerate(repositories):
            repo_name = repo.get("name")
            logger.info(f"Processing repository {i+1}/{len(repositories)}: {repo_name}")
            
            try:
                result = self.optimize_repository(username, repo_name)
                results.append(result)
            except Exception as e:
                logger.error(f"Error optimizing repository {repo_name}: {e}")
                results.append({
                    "name": repo_name,
                    "error": str(e),
                    "success": False
                })
        
        logger.info(f"Optimized {len(results)} repositories")
        
        # Save the results
        timestamp = generate_timestamp()
        results_file = f"seo_results_{timestamp}.json"
        save_json(results, results_file)
        logger.info(f"Results saved to {results_file}")
        
        return results
    
    def optimize_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Optimize a single repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            A dictionary containing the optimization results.
        """
        logger.info(f"Optimizing repository: {owner}/{repo}")
        
        # Check if the repository is a fork and sync it if needed
        if self.sync_forks and self.github.is_fork(owner, repo):
            logger.info(f"Repository {repo} is a fork, syncing with upstream")
            self.github.sync_fork(owner, repo)
        
        # Get repository information
        repository = self.github.get_repository(owner, repo)
        if not repository:
            raise ValueError(f"Repository {owner}/{repo} not found")
        
        # Get repository languages
        languages = list(self.github.get_repository_languages(owner, repo).keys())
        
        # Get repository topics
        topics = self.github.get_repository_topics(owner, repo)
        
        # Get repository README
        readme = self.github.get_repository_readme(owner, repo) or ""
        
        # Get repository description
        description = repository.get("description", "")
        
        # Optimize the repository content
        optimization = self.generator.optimize_repository(
            repo_name=repo,
            languages=languages,
            current_topics=topics,
            current_description=description,
            readme=readme
        )
        
        # Apply changes if requested
        if self.apply_changes:
            changes = optimization.get("changes", {})
            
            # Update description and topics
            if changes.get("description") or changes.get("topics"):
                logger.info(f"Updating description and topics for {repo}")
                self.github.update_repository(
                    owner=owner,
                    repo=repo,
                    description=optimization.get("new_description"),
                    topics=optimization.get("new_topics")
                )
            
            # Update README
            if changes.get("readme"):
                logger.info(f"Updating README for {repo}")
                self.github.update_repository_readme(
                    owner=owner,
                    repo=repo,
                    content=optimization.get("new_readme"),
                    message="Update README with SEO optimization"
                )
        
        # Add repository information to the results
        optimization["owner"] = owner
        optimization["repo"] = repo
        optimization["success"] = True
        optimization["timestamp"] = datetime.now().isoformat()
        
        return optimization


def main():
    """Main function for the repository optimizer."""
    parser = argparse.ArgumentParser(description="GitHub Repository SEO Optimizer")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--provider", default="local", help="LLM provider to use (default: local)")
    parser.add_argument("--no-sync", action="store_true", help="Don't sync forked repositories")
    parser.add_argument("--max-repos", type=int, default=100, help="Maximum number of repositories to optimize")
    parser.add_argument("--token", help="GitHub API token (default: use GitHub CLI)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
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


if __name__ == "__main__":
    main()
