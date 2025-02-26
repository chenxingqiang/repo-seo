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

def generate_target_doc(github_client: GitHubClient, username: str, repo_name: str) -> str:
    """Generate a target document outlining repository goals and plans"""
    repo_data = github_client.get_repo_data(username, repo_name)
    readme_content = github_client.get_repo_content(username, repo_name)

    target_doc = f"# Repository Targets and Plans for {repo_name}\n\n"
    target_doc += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Current Status
    target_doc += "## Current Status\n\n"
    target_doc += f"**Repository:** [{repo_name}]({repo_data.get('url', '')})\n\n"
    target_doc += f"**Description:** {repo_data.get('description', 'No description')}\n\n"
    if repo_data.get('primaryLanguage', {}).get('name'):
        target_doc += f"**Primary Language:** {repo_data['primaryLanguage']['name']}\n\n"

    # Topics
    if repo_data.get('repositoryTopics'):
        target_doc += "**Topics:**\n"
        for topic in repo_data['repositoryTopics']:
            target_doc += f"- {topic.get('name', '')}\n"
        target_doc += "\n"

    # Goals and Objectives
    target_doc += "## Goals and Objectives\n\n"
    target_doc += "1. **Code Quality**\n"
    target_doc += "   - Maintain high code quality standards\n"
    target_doc += "   - Regular code reviews and updates\n"
    target_doc += "   - Comprehensive documentation\n\n"

    target_doc += "2. **Feature Development**\n"
    target_doc += "   - Implement core functionality\n"
    target_doc += "   - Add new features based on user feedback\n"
    target_doc += "   - Regular feature updates\n\n"

    target_doc += "3. **Documentation**\n"
    target_doc += "   - Maintain up-to-date README\n"
    target_doc += "   - Code documentation and comments\n"
    target_doc += "   - Usage examples and tutorials\n\n"

    target_doc += "4. **Community**\n"
    target_doc += "   - Encourage community contributions\n"
    target_doc += "   - Respond to issues and pull requests\n"
    target_doc += "   - Regular communication with users\n\n"

    # Development Plan
    target_doc += "## Development Plan\n\n"
    target_doc += "### Short-term Goals (1-3 months)\n\n"
    target_doc += "- [ ] Complete core functionality\n"
    target_doc += "- [ ] Add comprehensive tests\n"
    target_doc += "- [ ] Improve documentation\n"
    target_doc += "- [ ] Set up CI/CD pipeline\n\n"

    target_doc += "### Medium-term Goals (3-6 months)\n\n"
    target_doc += "- [ ] Add advanced features\n"
    target_doc += "- [ ] Optimize performance\n"
    target_doc += "- [ ] Increase test coverage\n"
    target_doc += "- [ ] Add integration examples\n\n"

    target_doc += "### Long-term Goals (6+ months)\n\n"
    target_doc += "- [ ] Scale the project\n"
    target_doc += "- [ ] Build community\n"
    target_doc += "- [ ] Add enterprise features\n"
    target_doc += "- [ ] Regular maintenance and updates\n\n"

    # Contribution Guidelines
    target_doc += "## Contribution Guidelines\n\n"
    target_doc += "1. Fork the repository\n"
    target_doc += "2. Create a feature branch\n"
    target_doc += "3. Make your changes\n"
    target_doc += "4. Add or update tests\n"
    target_doc += "5. Update documentation\n"
    target_doc += "6. Submit a pull request\n\n"

    # Maintenance Plan
    target_doc += "## Maintenance Plan\n\n"
    target_doc += "### Regular Tasks\n\n"
    target_doc += "- Weekly code reviews\n"
    target_doc += "- Monthly dependency updates\n"
    target_doc += "- Quarterly security audits\n"
    target_doc += "- Regular backup and maintenance\n\n"

    target_doc += "### Quality Assurance\n\n"
    target_doc += "- Automated testing\n"
    target_doc += "- Code coverage monitoring\n"
    target_doc += "- Performance benchmarking\n"
    target_doc += "- Security scanning\n\n"

    return target_doc

def process_code_summary(github_client: GitHubClient, username: str, repo_name: str, logger: logging.Logger) -> bool:
    """Process code summary task"""
    try:
        logger.info(f"Generating code summary for {repo_name}")
        code_summary = generate_code_summary(github_client, username, repo_name)
        summary_filename = os.path.join('docs', f"code-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
        with open(summary_filename, 'w') as f:
            f.write(code_summary)
        logger.info(f"Code summary saved to {summary_filename}")
        return True
    except Exception as e:
        logger.error(f"Error generating code summary: {str(e)}")
        return False

def process_commit_timeline(github_client: GitHubClient, username: str, repo_name: str, logger: logging.Logger) -> bool:
    """Process commit timeline task"""
    try:
        logger.info(f"Generating commit timeline for {repo_name}")
        commit_timeline = generate_commit_timeline(github_client, username, repo_name)
        timeline_filename = os.path.join('docs', "commit-timeline-info.md")
        with open(timeline_filename, 'w') as f:
            f.write(commit_timeline)
        logger.info(f"Commit timeline saved to {timeline_filename}")
        return True
    except Exception as e:
        logger.error(f"Error generating commit timeline: {str(e)}")
        return False

def process_target_doc(github_client: GitHubClient, username: str, repo_name: str, logger: logging.Logger) -> bool:
    """Process target document task"""
    try:
        logger.info(f"Generating target document for {repo_name}")
        target_doc = generate_target_doc(github_client, username, repo_name)
        target_filename = os.path.join('docs', "target.md")
        with open(target_filename, 'w') as f:
            f.write(target_doc)
        logger.info(f"Target document saved to {target_filename}")
        return True
    except Exception as e:
        logger.error(f"Error generating target document: {str(e)}")
        return False

def process_seo_analysis(github_client: GitHubClient, content_analyzer: ContentAnalyzer,
                        seo_generator: SEOGenerator, username: str, repo_name: str,
                        logger: logging.Logger, update_description: bool = False) -> bool:
    """Process SEO analysis task"""
    try:
        logger.info(f"Analyzing repository content for SEO: {repo_name}")

        # Get repository data
        repo_data = github_client.get_repo_data(username, repo_name)
        if not repo_data:
            logger.error("Failed to fetch repository data")
            return False

        # Analyze repository content
        analyzed_data = content_analyzer.analyze_repository(repo_data)

        # Get and analyze README content
        readme_content = github_client.get_repo_content(username, repo_name)
        if readme_content:
            summary, topics, entities = content_analyzer.analyze_readme(readme_content)
            analyzed_data["readme_summary"] = summary
            analyzed_data["readme_topics"] = topics
            analyzed_data["readme_entities"] = entities

        # Generate SEO optimizations
        seo_data = seo_generator.optimize_repository(analyzed_data)

        # Generate SEO report
        report = f"# SEO Analysis Report for {repo_name}\n\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## Current Description\n\n"
        report += f"{repo_data.get('description', 'No description')}\n\n"

        report += "## Suggested Description\n\n"
        report += f"{seo_data.get('seo_description', 'No suggestion')}\n\n"

        report += "## Keywords\n\n"
        keywords = seo_data.get('seo_keywords', [])
        for keyword in keywords:
            report += f"- {keyword}\n"
        report += "\n"

        if analyzed_data.get('readme_topics'):
            report += "## README Topics\n\n"
            for topic in analyzed_data['readme_topics']:
                report += f"- {topic}\n"
            report += "\n"

        if analyzed_data.get('readme_entities'):
            report += "## Named Entities\n\n"
            for entity in analyzed_data['readme_entities']:
                report += f"- {entity}\n"
            report += "\n"

        # Save the report
        report_filename = os.path.join('docs', f"seo-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
        with open(report_filename, 'w') as f:
            f.write(report)
        logger.info(f"SEO report saved to {report_filename}")

        # Update repository description if requested
        if update_description and seo_data.get('seo_description'):
            logger.info("Updating repository description...")
            if github_client.update_repo_description(username, repo_name, seo_data['seo_description']):
                logger.info("Repository description updated successfully")
            else:
                logger.warning("Failed to update repository description")

        return True
    except Exception as e:
        logger.error(f"Error in SEO analysis: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository SEO Enhancement Tool')
    parser.add_argument('--username', required=True, help='GitHub username')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--task', choices=['code-summary', 'commit-timeline', 'seo-analysis', 'target', 'all'],
                      default='all', help='Specific task to run (default: all)')
    parser.add_argument('--no-commit', action='store_true',
                      help='Do not commit changes to repository')
    parser.add_argument('--update-description', action='store_true',
                      help='Update repository description with SEO-optimized version')
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Initialize components
        logger.info("Initializing components...")
        github_client = GitHubClient()
        content_analyzer = ContentAnalyzer()
        seo_generator = SEOGenerator()

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

            success = True
            if args.task in ['code-summary', 'all']:
                success &= process_code_summary(github_client, args.username, repo_name, logger)

            if args.task in ['commit-timeline', 'all']:
                success &= process_commit_timeline(github_client, args.username, repo_name, logger)

            if args.task in ['seo-analysis', 'all']:
                success &= process_seo_analysis(github_client, content_analyzer, seo_generator,
                                             args.username, repo_name, logger, args.update_description)

            if args.task in ['target', 'all']:
                success &= process_target_doc(github_client, args.username, repo_name, logger)

            # Commit changes if requested and if all tasks succeeded
            if success and not args.no_commit:
                logger.info("Committing documentation changes...")
                if commit_docs_changes(repo_name, logger):
                    logger.info("Documentation update completed successfully")
                else:
                    logger.warning("Failed to commit documentation changes")
            elif not success:
                logger.error("One or more tasks failed, skipping commit")
            else:
                logger.info("Changes were not committed (--no-commit flag was set)")

        except Exception as e:
            logger.error(f"Error processing repository {repo_name}: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
