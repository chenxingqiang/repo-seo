#!/usr/bin/env python3
"""
Repository manager module for the GitHub Repository SEO Optimizer.

This module provides functionality for managing GitHub repositories,
including fetching repository information, updating repositories, and more.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

from .github_client import GitHubCliClient, GitHubApiClient
from .utils.common import save_json, generate_timestamp

# Configure logging
logger = logging.getLogger(__name__)


class RepositoryManager:
    """Repository manager for GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize the repository manager.
        
        Args:
            github_token: The GitHub API token, or None to use the GitHub CLI.
        """
        # Initialize GitHub client
        if github_token:
            self.github = GitHubApiClient(token=github_token)
            logger.info("Using GitHub API client")
        else:
            self.github = GitHubCliClient()
            logger.info("Using GitHub CLI client")
    
    def get_user_repositories(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """Get all repositories for a user.
        
        Args:
            username: The GitHub username.
            max_repos: The maximum number of repositories to return.
            
        Returns:
            A list of repository dictionaries.
        """
        logger.info(f"Getting repositories for user: {username}")
        
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
        
        return repositories
    
    def get_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed information about a repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            A dictionary containing repository details.
        """
        logger.info(f"Getting details for repository: {owner}/{repo}")
        
        # Get repository information
        repository = self.github.get_repository(owner, repo)
        if not repository:
            logger.error(f"Repository {owner}/{repo} not found")
            return {}
        
        # Get repository languages
        languages = list(self.github.get_repository_languages(owner, repo).keys())
        
        # Get repository topics
        topics = self.github.get_repository_topics(owner, repo)
        
        # Get repository README
        readme = self.github.get_repository_readme(owner, repo) or ""
        
        # Combine all information
        details = {
            "name": repo,
            "owner": owner,
            "description": repository.get("description", ""),
            "languages": languages,
            "topics": topics,
            "readme": readme,
            "is_fork": self.github.is_fork(owner, repo)
        }
        
        return details
    
    def update_repository(self, owner: str, repo: str, description: Optional[str] = None,
                         topics: Optional[List[str]] = None, readme: Optional[str] = None) -> bool:
        """Update a repository's description, topics, and README.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            description: The new description, or None to leave unchanged.
            topics: The new topics, or None to leave unchanged.
            readme: The new README content, or None to leave unchanged.
            
        Returns:
            True if the update was successful, False otherwise.
        """
        logger.info(f"Updating repository: {owner}/{repo}")
        
        success = True
        
        # Update description and topics
        if description is not None or topics is not None:
            logger.info(f"Updating description and topics for {repo}")
            if not self.github.update_repository(
                owner=owner,
                repo=repo,
                description=description,
                topics=topics
            ):
                logger.error(f"Failed to update description and topics for {repo}")
                success = False
        
        # Update README
        if readme is not None:
            logger.info(f"Updating README for {repo}")
            if not self.github.update_repository_readme(
                owner=owner,
                repo=repo,
                content=readme,
                message="Update README with SEO optimization"
            ):
                logger.error(f"Failed to update README for {repo}")
                success = False
        
        return success
    
    def sync_fork(self, owner: str, repo: str) -> bool:
        """Sync a forked repository with its upstream.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            True if the sync was successful, False otherwise.
        """
        logger.info(f"Syncing fork: {owner}/{repo}")
        
        # Check if the repository is a fork
        if not self.github.is_fork(owner, repo):
            logger.warning(f"Repository {repo} is not a fork, skipping sync")
            return True
        
        # Sync the fork
        if not self.github.sync_fork(owner, repo):
            logger.error(f"Failed to sync fork {repo}")
            return False
        
        return True
    
    def export_repository_data(self, repositories: List[Dict[str, Any]], 
                              filename: Optional[str] = None) -> str:
        """Export repository data to a JSON file.
        
        Args:
            repositories: A list of repository dictionaries.
            filename: The filename to save to, or None to generate a filename.
            
        Returns:
            The filename where the data was saved.
        """
        if filename is None:
            timestamp = generate_timestamp()
            filename = f"repository_data_{timestamp}.json"
        
        logger.info(f"Exporting repository data to {filename}")
        
        # Save the data
        if save_json(repositories, filename):
            logger.info(f"Repository data saved to {filename}")
        else:
            logger.error(f"Failed to save repository data to {filename}")
        
        return filename
    
    def import_repository_data(self, filename: str) -> List[Dict[str, Any]]:
        """Import repository data from a JSON file.
        
        Args:
            filename: The filename to load from.
            
        Returns:
            A list of repository dictionaries.
        """
        logger.info(f"Importing repository data from {filename}")
        
        try:
            with open(filename, 'r') as f:
                repositories = json.load(f)
            
            logger.info(f"Imported {len(repositories)} repositories from {filename}")
            return repositories
        except Exception as e:
            logger.error(f"Error importing repository data from {filename}: {e}")
            return []
