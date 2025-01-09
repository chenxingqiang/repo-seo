import os
import subprocess
import logging
from typing import List, Dict, Optional
import json

class GitHubClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._check_gh_cli()

    def _check_gh_cli(self):
        """Verify GitHub CLI is installed and authenticated"""
        try:
            subprocess.run(['gh', '--version'], check=True, capture_output=True)
            # Check authentication
            result = subprocess.run(['gh', 'auth', 'status'], check=True, capture_output=True, text=True)
            self.logger.info("GitHub CLI authentication successful")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"GitHub CLI error: {e.stderr}")
            raise RuntimeError("GitHub CLI (gh) is not installed or not authenticated")

    def sync_fork(self, username: str, repo: str) -> bool:
        """Sync a forked repository with its upstream"""
        try:
            self.logger.info(f"Checking if {repo} is a fork...")
            # Check if repo is a fork
            cmd = ['gh', 'repo', 'view', f"{username}/{repo}", '--json', 'isFork,parent']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Failed to check fork status: {result.stderr}")
                return False

            repo_info = json.loads(result.stdout)
            if not repo_info.get('isFork', False):
                self.logger.info(f"{repo} is not a fork, skipping sync")
                return True

            parent = repo_info.get('parent', {})
            if not parent:
                self.logger.warning(f"No parent information found for {repo}")
                return False

            # Clone the repository
            self.logger.info(f"Syncing fork {repo} with upstream...")
            clone_cmd = ['gh', 'repo', 'clone', f"{username}/{repo}", '--', '--quiet']
            subprocess.run(clone_cmd, check=True, capture_output=True)

            # Change to repo directory
            os.chdir(repo)

            # Add upstream remote if not exists
            upstream_url = parent.get('url', '').replace('https://github.com/', '')
            add_upstream_cmd = ['git', 'remote', 'add', 'upstream', f"https://github.com/{upstream_url}"]
            subprocess.run(add_upstream_cmd, capture_output=True)

            # Fetch upstream
            fetch_cmd = ['git', 'fetch', 'upstream']
            subprocess.run(fetch_cmd, check=True, capture_output=True)

            # Get default branch
            default_branch = parent.get('defaultBranchRef', {}).get('name', 'main')

            # Merge upstream changes
            merge_cmd = ['git', 'merge', f"upstream/{default_branch}"]
            subprocess.run(merge_cmd, check=True, capture_output=True)

            # Push changes
            push_cmd = ['git', 'push', 'origin', default_branch]
            subprocess.run(push_cmd, check=True, capture_output=True)

            # Change back and cleanup
            os.chdir('..')
            subprocess.run(['rm', '-rf', repo], check=True)

            self.logger.info(f"Successfully synced fork {repo}")
            return True

        except Exception as e:
            self.logger.error(f"Error syncing fork {repo}: {str(e)}")
            # Try to cleanup if something went wrong
            try:
                if os.path.exists(repo):
                    os.chdir('..')
                    subprocess.run(['rm', '-rf', repo], check=True)
            except:
                pass
            return False

    def check_auth(self) -> bool:
        """
        Check if GitHub CLI is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking GitHub CLI authentication: {str(e)}")
            return False

    def get_user_repos(self, username: str) -> List[Dict]:
        """
        Get all repositories for a user using GitHub CLI.
        
        Args:
            username: GitHub username
            
        Returns:
            List of repository data dictionaries
        """
        try:
            result = subprocess.run(
                ["gh", "repo", "list", username, "--json", "name,description,url,repositoryTopics,primaryLanguage,isFork"],
                capture_output=True,
                text=True,
                check=True
            )
            
            repos = json.loads(result.stdout)
            self.logger.info(f"Found {len(repos)} repositories")
            return repos
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error fetching repositories: {e.stderr}")
            return []
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return []

    def get_repo_content(self, username: str, repo: str) -> Optional[str]:
        """
        Get repository README content using GitHub CLI.
        
        Args:
            username: GitHub username
            repo: Repository name
            
        Returns:
            README content if available, None otherwise
        """
        try:
            # First, get the default branch
            result = subprocess.run(
                ["gh", "api", f"/repos/{username}/{repo}/readme", "--jq", ".content"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                import base64
                return base64.b64decode(result.stdout.strip()).decode('utf-8')
            return None
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error fetching repository content: {e.stderr}")
            return None
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return None

    def update_repo_description(self, username: str, repo: str, description: str) -> bool:
        """
        Update repository description using GitHub CLI.
        
        Args:
            username: GitHub username
            repo: Repository name
            description: New repository description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["gh", "repo", "edit", f"{username}/{repo}", "--description", description],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error updating repository description: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return False

    def get_repo_commits(self, username: str, repo: str) -> List[Dict]:
        """
        Get repository commit history using GitHub CLI.
        
        Args:
            username: GitHub username
            repo: Repository name
            
        Returns:
            List of commit data dictionaries
        """
        try:
            result = subprocess.run(
                ["gh", "api", f"/repos/{username}/{repo}/commits", "--paginate"],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = json.loads(result.stdout)
            self.logger.info(f"Found {len(commits)} commits")
            return commits
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error fetching commits: {e.stderr}")
            return []
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return []

    def get_repo_tree(self, username: str, repo: str) -> List[Dict]:
        """
        Get repository file tree using GitHub CLI.
        
        Args:
            username: GitHub username
            repo: Repository name
            
        Returns:
            List of file data dictionaries
        """
        try:
            # First get the default branch SHA
            branch_result = subprocess.run(
                ["gh", "api", f"/repos/{username}/{repo}/branches/main"],
                capture_output=True,
                text=True,
                check=True
            )
            
            branch_data = json.loads(branch_result.stdout)
            tree_sha = branch_data['commit']['commit']['tree']['sha']
            
            # Then get the tree
            tree_result = subprocess.run(
                ["gh", "api", f"/repos/{username}/{repo}/git/trees/{tree_sha}?recursive=1"],
                capture_output=True,
                text=True,
                check=True
            )
            
            tree_data = json.loads(tree_result.stdout)
            return tree_data.get('tree', [])
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error fetching repository tree: {e.stderr}")
            return []
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return [] 