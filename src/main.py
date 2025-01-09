import argparse
import logging
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from github_client import GitHubClient
from content_analyzer import ContentAnalyzer
from seo_generator import SEOGenerator

def setup_logging(verbose: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def commit_docs_changes(repo_name: str, logger):
    """Commit changes in docs directory using subprocess for better control"""
    try:
        # Add changes
        subprocess.run(['git', 'add', 'docs/'], check=True)
        
        # Create commit message
        commit_message = f"docs: Update repository documentation for {repo_name} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        logger.info("Successfully committed and pushed documentation changes")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in git operations: {e.stderr if e.stderr else str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error committing changes: {str(e)}")
        return False

def generate_code_summary(github_client: GitHubClient, username: str, repo_name: str) -> str:
    """Generate a markdown summary of the repository code structure"""
    tree = github_client.get_repo_tree(username, repo_name)
    
    summary = f"# Code Summary for {repo_name}\n\n"
    summary += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Group files by directory
    directories = {}
    for item in tree:
        if item['type'] == 'blob':  # Only process files
            path = Path(item['path'])
            directory = str(path.parent)
            if directory == '.':
                directory = 'root'
            
            if directory not in directories:
                directories[directory] = []
            directories[directory].append(path.name)
    
    # Generate markdown
    for directory, files in sorted(directories.items()):
        summary += f"## {directory}\n\n"
        for file in sorted(files):
            summary += f"- {file}\n"
        summary += "\n"
    
    return summary

def generate_commit_timeline(github_client: GitHubClient, username: str, repo_name: str) -> str:
    """Generate a markdown timeline of repository commits"""
    commits = github_client.get_repo_commits(username, repo_name)
    
    timeline = f"# Commit Timeline for {repo_name}\n\n"
    timeline += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for commit in commits:
        commit_data = commit['commit']
        author = commit_data['author']
        date = datetime.strptime(author['date'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        
        timeline += f"## {date}\n\n"
        timeline += f"**Author:** {author['name']} <{author['email']}>\n\n"
        timeline += f"**Message:**\n{commit_data['message']}\n\n"
        timeline += "---\n\n"
    
    return timeline

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository SEO Enhancement Tool')
    parser.add_argument('--username', required=True, help='GitHub username')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Initialize components
        logger.info("Initializing components...")
        github_client = GitHubClient()

        # Authenticate and check GitHub CLI
        logger.info("Checking GitHub CLI authentication...")
        if not github_client.check_auth():
            logger.error("GitHub CLI authentication failed")
            return

        # Process current repository (repo-seo)
        repo_name = "repo-seo"
        logger.info(f"Processing repository: {repo_name}")

        try:
            # Create docs directory if it doesn't exist
            os.makedirs('docs', exist_ok=True)

            # Generate code summary
            logger.info(f"Generating code summary for {repo_name}")
            code_summary = generate_code_summary(github_client, args.username, repo_name)
            summary_filename = os.path.join('docs', f"code-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
            with open(summary_filename, 'w') as f:
                f.write(code_summary)
            logger.info(f"Code summary saved to {summary_filename}")

            # Generate commit timeline
            logger.info(f"Generating commit timeline for {repo_name}")
            commit_timeline = generate_commit_timeline(github_client, args.username, repo_name)
            timeline_filename = os.path.join('docs', "commit-timeline-info.md")
            with open(timeline_filename, 'w') as f:
                f.write(commit_timeline)
            logger.info(f"Commit timeline saved to {timeline_filename}")

            # Commit the changes
            logger.info("Committing documentation changes...")
            if commit_docs_changes(repo_name, logger):
                logger.info("Documentation update completed successfully")
            else:
                logger.warning("Failed to commit documentation changes")

        except Exception as e:
            logger.error(f"Error processing repository {repo_name}: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 