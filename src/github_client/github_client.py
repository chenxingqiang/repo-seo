#!/usr/bin/env python3
"""
GitHub client module for interacting with the GitHub API.

This module provides classes for interacting with the GitHub API,
either through the GitHub CLI or directly through the REST API.
"""

import os
import json
import subprocess
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple

from ..utils.common import run_command, logger


class GitHubClient(ABC):
    """Abstract base class for GitHub clients."""
    
    @abstractmethod
    def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get a list of repositories for a user.
        
        Args:
            username: The GitHub username.
            
        Returns:
            A list of repository dictionaries.
        """
        pass
    
    @abstractmethod
    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get information about a repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            A dictionary containing repository information, or None if not found.
        """
        pass
    
    @abstractmethod
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get the languages used in a repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            A dictionary mapping language names to byte counts.
        """
        pass
    
    @abstractmethod
    def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Get the topics for a repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            A list of topic strings.
        """
        pass
    
    @abstractmethod
    def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get the README content for a repository.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            The README content as a string, or None if not found.
        """
        pass
    
    @abstractmethod
    def update_repository(self, owner: str, repo: str, 
                         description: Optional[str] = None,
                         topics: Optional[List[str]] = None) -> bool:
        """Update a repository's description and topics.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            description: The new description, or None to leave unchanged.
            topics: The new topics, or None to leave unchanged.
            
        Returns:
            True if the update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def update_repository_readme(self, owner: str, repo: str, 
                                content: str, message: str = "Update README") -> bool:
        """Update a repository's README file.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            content: The new README content.
            message: The commit message.
            
        Returns:
            True if the update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_fork(self, owner: str, repo: str) -> bool:
        """Check if a repository is a fork.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            True if the repository is a fork, False otherwise.
        """
        pass
    
    @abstractmethod
    def sync_fork(self, owner: str, repo: str) -> bool:
        """Sync a forked repository with its upstream.
        
        Args:
            owner: The repository owner.
            repo: The repository name.
            
        Returns:
            True if the sync was successful, False otherwise.
        """
        pass


class GitHubCliClient(GitHubClient):
    """GitHub client that uses the GitHub CLI."""
    
    def __init__(self):
        """Initialize the GitHub CLI client."""
        # Check if the GitHub CLI is installed
        returncode, stdout, stderr = run_command(["gh", "--version"])
        if returncode != 0:
            raise RuntimeError(
                "GitHub CLI not found. Please install it from https://cli.github.com/"
            )
        
        # Check if the user is authenticated
        returncode, stdout, stderr = run_command(["gh", "auth", "status"])
        if returncode != 0:
            raise RuntimeError(
                "Not authenticated with GitHub CLI. Please run 'gh auth login'."
            )
    
    def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get a list of repositories for a user using the GitHub CLI."""
        returncode, stdout, stderr = run_command([
            "gh", "repo", "list", username, "--json",
            "name,description,isPrivate,isFork,defaultBranchRef"
        ])
        
        if returncode != 0:
            logger.error(f"Error getting repositories for {username}: {stderr}")
            return []
        
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            logger.error(f"Error parsing repository list for {username}")
            return []
    
    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get information about a repository using the GitHub CLI."""
        returncode, stdout, stderr = run_command([
            "gh", "repo", "view", f"{owner}/{repo}", "--json",
            "name,description,isPrivate,isFork,defaultBranchRef,languages,topics"
        ])
        
        if returncode != 0:
            logger.error(f"Error getting repository {owner}/{repo}: {stderr}")
            return None
        
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            logger.error(f"Error parsing repository info for {owner}/{repo}")
            return None
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get the languages used in a repository using the GitHub CLI."""
        repository = self.get_repository(owner, repo)
        if not repository or "languages" not in repository:
            return {}
        
        # Convert the languages list to a dictionary
        languages = {}
        for lang in repository["languages"]["edges"]:
            languages[lang["node"]["name"]] = lang["size"]
        
        return languages
    
    def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Get the topics for a repository using the GitHub CLI."""
        repository = self.get_repository(owner, repo)
        if not repository or "topics" not in repository:
            return []
        
        return repository["topics"]["nodes"]
    
    def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get the README content for a repository using the GitHub CLI."""
        returncode, stdout, stderr = run_command([
            "gh", "repo", "view", f"{owner}/{repo}", "--readme"
        ])
        
        if returncode != 0:
            logger.error(f"Error getting README for {owner}/{repo}: {stderr}")
            return None
        
        return stdout
    
    def update_repository(self, owner: str, repo: str, 
                         description: Optional[str] = None,
                         topics: Optional[List[str]] = None) -> bool:
        """Update a repository's description and topics using the GitHub CLI."""
        command = ["gh", "repo", "edit", f"{owner}/{repo}"]
        
        if description is not None:
            command.extend(["--description", description])
        
        if topics is not None:
            command.extend(["--add-topic", ",".join(topics)])
        
        returncode, stdout, stderr = run_command(command)
        
        if returncode != 0:
            logger.error(f"Error updating repository {owner}/{repo}: {stderr}")
            return False
        
        return True
    
    def update_repository_readme(self, owner: str, repo: str, 
                                content: str, message: str = "Update README") -> bool:
        """Update a repository's README file using the GitHub CLI."""
        # This is more complex with the CLI, so we'll use a temporary file
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        
        try:
            # Create or update the README.md file
            returncode, stdout, stderr = run_command([
                "gh", "api", "--method", "PUT",
                f"/repos/{owner}/{repo}/contents/README.md",
                "-f", f"message={message}",
                "-f", f"content={content}",
                "--input", temp_path
            ])
            
            os.unlink(temp_path)
            
            if returncode != 0:
                logger.error(f"Error updating README for {owner}/{repo}: {stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error updating README for {owner}/{repo}: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return False
    
    def is_fork(self, owner: str, repo: str) -> bool:
        """Check if a repository is a fork using the GitHub CLI."""
        repository = self.get_repository(owner, repo)
        if not repository:
            return False
        
        return repository.get("isFork", False)
    
    def sync_fork(self, owner: str, repo: str) -> bool:
        """Sync a forked repository with its upstream using the GitHub CLI."""
        returncode, stdout, stderr = run_command([
            "gh", "repo", "sync", f"{owner}/{repo}"
        ])
        
        if returncode != 0:
            logger.error(f"Error syncing fork {owner}/{repo}: {stderr}")
            return False
        
        return True


class GitHubApiClient(GitHubClient):
    """GitHub client that uses the GitHub REST API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub API client.
        
        Args:
            token: The GitHub API token, or None to use the GITHUB_TOKEN environment variable.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub API token not provided. Please set the GITHUB_TOKEN environment variable."
            )
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_url = "https://api.github.com"
    
    def _make_request(self, method: str, endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
        """Make a request to the GitHub API.
        
        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint.
            params: Query parameters.
            data: Request body data.
            
        Returns:
            A tuple containing the status code and the response JSON.
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return getattr(e.response, "status_code", 500), {}
    
    def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get a list of repositories for a user using the GitHub API."""
        status_code, response = self._make_request(
            "GET",
            f"/users/{username}/repos",
            params={"per_page": 100}
        )
        
        if status_code != 200:
            logger.error(f"Error getting repositories for {username}: {response}")
            return []
        
        return response
    
    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get information about a repository using the GitHub API."""
        status_code, response = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}"
        )
        
        if status_code != 200:
            logger.error(f"Error getting repository {owner}/{repo}: {response}")
            return None
        
        return response
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get the languages used in a repository using the GitHub API."""
        status_code, response = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/languages"
        )
        
        if status_code != 200:
            logger.error(f"Error getting languages for {owner}/{repo}: {response}")
            return {}
        
        return response
    
    def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Get the topics for a repository using the GitHub API."""
        status_code, response = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/topics",
            headers={"Accept": "application/vnd.github.mercy-preview+json"}
        )
        
        if status_code != 200:
            logger.error(f"Error getting topics for {owner}/{repo}: {response}")
            return []
        
        return response.get("names", [])
    
    def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get the README content for a repository using the GitHub API."""
        status_code, response = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/readme"
        )
        
        if status_code != 200:
            logger.error(f"Error getting README for {owner}/{repo}: {response}")
            return None
        
        import base64
        try:
            content = response.get("content", "")
            if content:
                return base64.b64decode(content).decode("utf-8")
        except Exception as e:
            logger.error(f"Error decoding README for {owner}/{repo}: {e}")
        
        return None
    
    def update_repository(self, owner: str, repo: str, 
                         description: Optional[str] = None,
                         topics: Optional[List[str]] = None) -> bool:
        """Update a repository's description and topics using the GitHub API."""
        data = {}
        
        if description is not None:
            data["description"] = description
        
        status_code, response = self._make_request(
            "PATCH",
            f"/repos/{owner}/{repo}",
            data=data
        )
        
        if status_code != 200:
            logger.error(f"Error updating description for {owner}/{repo}: {response}")
            return False
        
        if topics is not None:
            status_code, response = self._make_request(
                "PUT",
                f"/repos/{owner}/{repo}/topics",
                headers={"Accept": "application/vnd.github.mercy-preview+json"},
                data={"names": topics}
            )
            
            if status_code != 200:
                logger.error(f"Error updating topics for {owner}/{repo}: {response}")
                return False
        
        return True
    
    def update_repository_readme(self, owner: str, repo: str, 
                                content: str, message: str = "Update README") -> bool:
        """Update a repository's README file using the GitHub API."""
        # First, check if the README exists
        status_code, response = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/contents/README.md"
        )
        
        import base64
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
        }
        
        if status_code == 200:
            # Update existing README
            data["sha"] = response.get("sha")
        
        status_code, response = self._make_request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/README.md",
            data=data
        )
        
        if status_code not in (200, 201):
            logger.error(f"Error updating README for {owner}/{repo}: {response}")
            return False
        
        return True
    
    def is_fork(self, owner: str, repo: str) -> bool:
        """Check if a repository is a fork using the GitHub API."""
        repository = self.get_repository(owner, repo)
        if not repository:
            return False
        
        return repository.get("fork", False)
    
    def sync_fork(self, owner: str, repo: str) -> bool:
        """Sync a forked repository with its upstream using the GitHub API."""
        # Get the default branch
        repository = self.get_repository(owner, repo)
        if not repository:
            return False
        
        default_branch = repository.get("default_branch", "main")
        
        # Get the parent repository
        parent = repository.get("parent")
        if not parent:
            logger.error(f"Repository {owner}/{repo} is not a fork or has no parent")
            return False
        
        parent_owner = parent.get("owner", {}).get("login")
        parent_repo = parent.get("name")
        
        if not parent_owner or not parent_repo:
            logger.error(f"Could not determine parent repository for {owner}/{repo}")
            return False
        
        # Create a merge request to sync with the parent
        status_code, response = self._make_request(
            "POST",
            f"/repos/{owner}/{repo}/merge-upstream",
            data={"branch": default_branch}
        )
        
        if status_code != 200:
            logger.error(f"Error syncing fork {owner}/{repo}: {response}")
            return False
        
        return True 