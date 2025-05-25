#!/usr/bin/env python3
"""
repo-seo: AI-powered GitHub Repository SEO Optimization Tool

Leverages large language models to analyze and optimize GitHub repositories
for better discoverability and user engagement.
"""

import argparse
import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Tuple

from .analyzer import RepoAnalyzer
from .ai_client import AIClient

# Try to import framework classes
try:
    from src.utils.analyzers import AnalyzerFactory
    ANALYZER_FRAMEWORK_AVAILABLE = True
except ImportError:
    ANALYZER_FRAMEWORK_AVAILABLE = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze and optimize GitHub repositories for SEO")

    parser.add_argument("repo_url", nargs="?", help="GitHub repository URL or local path")
    parser.add_argument("--token", "-t", help="GitHub API token")

    # Analysis options
    parser.add_argument("--analyze", "-a", action="store_true", help="Analyze repository SEO")
    parser.add_argument("--readme", "-r", action="store_true", help="Generate README recommendations")
    parser.add_argument("--topics", "-o", action="store_true", help="Generate topic recommendations")
    parser.add_argument("--description", "-d", action="store_true", help="Generate description recommendations")

    # File generation options
    parser.add_argument("--license", "-l", action="store_true", help="Generate LICENSE file")
    parser.add_argument("--license-type", choices=["mit", "apache2", "gpl3", "bsd", "cc0", "unlicense"],
                       default="mit", help="License type to generate (default: mit)")
    parser.add_argument("--contributing", "-b", action="store_true", help="Generate CONTRIBUTING.md file")
    parser.add_argument("--coc", action="store_true", help="Generate CODE_OF_CONDUCT.md file")
    parser.add_argument("--generate-all", "-g", action="store_true",
                       help="Generate all recommended files (README, LICENSE, CONTRIBUTING, etc.)")

    # Output options
    parser.add_argument("--output", "-u", help="Output results to file")
    parser.add_argument("--format", "-f", choices=["json", "text", "markdown"], default="text",
                       help="Output format (default: text)")

    # AI provider options
    parser.add_argument("--provider", "-p", choices=["auto", "openai", "deepseek", "claude"], default="auto",
                       help="AI provider to use (default: auto)")
    parser.add_argument("--api-key", "-k", help="API key for AI provider")

    # Advanced options
    parser.add_argument("--deep", action="store_true", help="Perform deep analysis with AI")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Git integration options
    parser.add_argument("--commit", "-c", action="store_true",
                       help="Commit generated files to repository")
    parser.add_argument("--commit-message", "-m", default="Add AI-generated documentation",
                       help="Commit message for file commits")
    parser.add_argument("--push", action="store_true",
                       help="Push changes to remote repository after commit")
    parser.add_argument("--skip-hooks", "-s", action="store_true",
                       help="Skip git hooks when committing")

    return parser.parse_args()


def get_repo_info(repo_url: str, token: Optional[str] = None) -> Dict:
    """
    Get repository information from GitHub or local path.

    Args:
        repo_url: GitHub repository URL or local path
        token: GitHub API token (optional)

    Returns:
        Dictionary containing repository information
    """
    # Determine if repo_url is a local path
    is_local = False
    local_path = None

    # Autodetect current directory if no path specified
    if repo_url is None:
        repo_url = os.getcwd()
        print(f"No repository specified, using current directory: {repo_url}")

    # Check if repo_url is a local path
    if os.path.exists(repo_url):
        is_local = True
        local_path = os.path.abspath(repo_url)
        print(f"Detected local repository path: {local_path}")

        # Try to get repository name from git config
        try:
            repo_name = subprocess.check_output(
                ["git", "-C", local_path, "config", "--get", "remote.origin.url"],
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            ).strip()

            # Extract repo name from URL (handles various URL formats)
            if repo_name:
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]
                repo_name = os.path.basename(repo_name)
                print(f"Detected repository name from git: {repo_name}")
        except subprocess.CalledProcessError:
            # Use directory name as repo name
            repo_name = os.path.basename(local_path)
            print(f"Using directory name as repository name: {repo_name}")

        # Read README from local repo if it exists
        readme_path = os.path.join(local_path, "README.md")
        readme = ""
        readme_exists = False
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8", errors='ignore') as f:
                readme = f.read()
                readme_exists = True

        # Detect languages by scanning files
        languages = detect_languages(local_path)

        # Try to get description and topics from .git or repository files
        description = ""
        try:
            # Try to get description from package.json if it exists
            package_json_path = os.path.join(local_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_data = json.load(f)
                    description = package_data.get("description", "")

            # Try to get description from pyproject.toml if it exists
            if not description:
                pyproject_path = os.path.join(local_path, "pyproject.toml")
                if os.path.exists(pyproject_path):
                    with open(pyproject_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("description"):
                                description = line.split("=")[1].strip().strip('"\'')
                                break

            # Try to get description from setup.py if it exists
            if not description:
                setup_py_path = os.path.join(local_path, "setup.py")
                if os.path.exists(setup_py_path):
                    with open(setup_py_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        import re
                        match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                        if match:
                            description = match.group(1)
        except Exception as e:
            print(f"Error getting description from repository files: {e}")

        # Get topics from repository files or directories
        topics = []
        # Add main programming languages as topics
        topics.extend([lang.lower() for lang in languages[:3]])
        # Add repo name components as topics
        topics.extend([part.lower() for part in repo_name.replace('-', ' ').replace('_', ' ').split() if len(part) > 2])
        # Remove duplicates
        topics = list(set(topics))

        return {
            "name": repo_name,
            "description": description,
            "languages": languages,
            "topics": topics,
            "readme": readme,
            "readme_exists": readme_exists,
            "local_path": local_path,
            "is_local": is_local
        }

    # For GitHub URLs, we'll use mock data for now
    # In a production implementation, this would use GitHub API
    return {
        "name": os.path.basename(repo_url.rstrip("/")) if "/" in repo_url else repo_url,
        "description": "GitHub Repository SEO Optimization Tool",
        "languages": ["Python", "Markdown"],
        "topics": ["github", "seo", "optimization"],
        "readme": "",
        "readme_exists": False,
        "local_path": None,
        "is_local": False
    }


def detect_languages(repo_path: str) -> List[str]:
    """
    Detect programming languages in the repository.

    Args:
        repo_path: Path to the repository

    Returns:
        List of detected languages
    """
    languages = {}

    # File extensions to language mapping
    extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.jsx': 'JavaScript',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C/C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.sh': 'Shell',
        '.bat': 'Batch',
        '.ps1': 'PowerShell',
        '.sql': 'SQL',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.dart': 'Dart',
        '.r': 'R'
    }

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories and vendor/dependency directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                  ['node_modules', 'venv', '.venv', 'build', 'dist', 'vendor']]

        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue

            # Get file extension
            _, ext = os.path.splitext(file)
            if ext in extensions:
                lang = extensions[ext]
                if lang in languages:
                    languages[lang] += 1
                else:
                    languages[lang] = 1

    # Sort languages by frequency
    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    return [lang for lang, _ in sorted_languages]


def format_output(results: Dict, output_format: str) -> str:
    """
    Format analysis results.

    Args:
        results: Analysis results dictionary
        output_format: Output format (json, text, markdown)

    Returns:
        Formatted output string
    """
    if output_format == "json":
        return json.dumps(results, indent=2)

    elif output_format == "markdown":
        md = f"# Repository Analysis: {results.get('metadata', {}).get('name', 'Unknown')}\n\n"

        # Overall score
        md += f"## Overall Score: {results.get('score', 0)}/100\n\n"

        # README analysis
        if "readme" in results:
            readme = results["readme"]
            md += "## README Analysis\n\n"

            if readme.get("exists", False):
                md += f"- **Length**: {readme.get('length', 0)} lines\n"
                md += f"- **Score**: {readme.get('score', 0)}/100\n"

                if "sections" in readme and readme["sections"]:
                    md += f"- **Sections**: {', '.join(readme['sections'])}\n"

                if "issues" in readme and readme["issues"]:
                    md += "\n### Issues\n\n"
                    for issue in readme["issues"]:
                        md += f"- {issue}\n"

                if "suggestions" in readme and readme["suggestions"]:
                    md += "\n### Suggestions\n\n"
                    for suggestion in readme["suggestions"]:
                        md += f"- {suggestion}\n"
            else:
                md += "- No README found\n"

        # Topics analysis
        if "topics" in results:
            topics = results["topics"]
            md += "\n## Topics Analysis\n\n"

            if "current" in topics and topics["current"]:
                md += f"- **Current Topics**: {', '.join(topics['current'])}\n"
            else:
                md += "- No topics defined\n"

            if "suggested" in topics and topics["suggested"]:
                md += f"- **Suggested Topics**: {', '.join(topics['suggested'])}\n"

            if "issues" in topics and topics["issues"]:
                md += "\n### Issues\n\n"
                for issue in topics["issues"]:
                    md += f"- {issue}\n"

            if "suggestions" in topics and topics["suggestions"]:
                md += "\n### Suggestions\n\n"
                for suggestion in topics["suggestions"]:
                    md += f"- {suggestion}\n"

        # Description analysis
        if "description" in results:
            desc = results["description"]
            md += "\n## Description Analysis\n\n"

            if "content" in desc and desc["content"]:
                md += f"- **Current**: {desc['content']}\n"
                md += f"- **Length**: {desc.get('length', 0)} characters\n"
            else:
                md += "- No description found\n"

            if "issues" in desc and desc["issues"]:
                md += "\n### Issues\n\n"
                for issue in desc["issues"]:
                    md += f"- {issue}\n"

            if "suggestions" in desc and desc["suggestions"]:
                md += "\n### Suggestions\n\n"
                for suggestion in desc["suggestions"]:
                    md += f"- {suggestion}\n"

        return md

    else:  # text format
        text = f"Repository Analysis: {results.get('metadata', {}).get('name', 'Unknown')}\n"
        text += f"Overall Score: {results.get('score', 0)}/100\n\n"

        # README analysis
        if "readme" in results:
            readme = results["readme"]
            text += "README Analysis:\n"

            if readme.get("exists", False):
                text += f"  Length: {readme.get('length', 0)} lines\n"
                text += f"  Score: {readme.get('score', 0)}/100\n"

                if "issues" in readme and readme["issues"]:
                    text += "  Issues:\n"
                    for issue in readme["issues"]:
                        text += f"    - {issue}\n"

                if "suggestions" in readme and readme["suggestions"]:
                    text += "  Suggestions:\n"
                    for suggestion in readme["suggestions"]:
                        text += f"    - {suggestion}\n"
            else:
                text += "  No README found\n"

        # Topics analysis
        if "topics" in results:
            topics = results["topics"]
            text += "\nTopics Analysis:\n"

            if "current" in topics and topics["current"]:
                text += f"  Current: {', '.join(topics['current'])}\n"
            else:
                text += "  No topics defined\n"

            if "suggested" in topics and topics["suggested"]:
                text += f"  Suggested: {', '.join(topics['suggested'])}\n"

            if "issues" in topics and topics["issues"]:
                text += "  Issues:\n"
                for issue in topics["issues"]:
                    text += f"    - {issue}\n"

        # Description analysis
        if "description" in results:
            desc = results["description"]
            text += "\nDescription Analysis:\n"

            if "content" in desc and desc["content"]:
                text += f"  Current: {desc['content']}\n"
                text += f"  Length: {desc.get('length', 0)} characters\n"
            else:
                text += "  No description found\n"

            if "issues" in desc and desc["issues"]:
                text += "  Issues:\n"
                for issue in desc["issues"]:
                    text += f"    - {issue}\n"

        return text


def commit_to_repository(repo_path: str, file_path: str, commit_message: str, push: bool = False, skip_hooks: bool = True) -> Tuple[bool, str]:
    """
    Commit a file to the repository and optionally push changes.

    Args:
        repo_path: Path to the repository
        file_path: Path to the file to commit
        commit_message: Commit message
        push: Whether to push changes to remote
        skip_hooks: Whether to skip pre-commit hooks

    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if git is available
        subprocess.check_output(["git", "--version"], stderr=subprocess.DEVNULL)

        # Check if path is a git repository
        subprocess.check_output(
            ["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.DEVNULL
        )

        # Add file to staging
        subprocess.check_output(
            ["git", "-C", repo_path, "add", file_path],
            stderr=subprocess.STDOUT
        )

        # Commit changes
        commit_cmd = ["git", "-C", repo_path, "commit", "-m", commit_message]
        if skip_hooks:
            commit_cmd.append("--no-verify")

        subprocess.check_output(
            commit_cmd,
            stderr=subprocess.STDOUT
        )

        commit_result = "Changes committed successfully"

        # Push if requested
        if push:
            push_cmd = ["git", "-C", repo_path, "push"]
            if skip_hooks:
                push_cmd.append("--no-verify")

            subprocess.check_output(
                push_cmd,
                stderr=subprocess.STDOUT
            )
            commit_result += " and pushed to remote"

        return True, commit_result

    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8') if hasattr(e, 'output') else str(e)
        return False, f"Git operation failed: {error_message}"
    except FileNotFoundError:
        return False, "Git is not installed or not in PATH"


def main():
    """Main entry point."""
    args = parse_args()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser = argparse.ArgumentParser()
        parser.print_help()
        sys.exit(1)

    # Get repository information
    repo_info = get_repo_info(args.repo_url, args.token)

    if not repo_info:
        print("Error: No repository specified")
        sys.exit(1)

    # Initialize AI client if needed
    ai_client = None
    if args.deep or args.readme or args.topics or args.description:
        try:
            ai_client = AIClient(provider=args.provider, token=args.api_key)
        except Exception as e:
            print(f"Warning: Failed to initialize AI client: {e}")
            print("Falling back to basic analysis")

    # Initialize repo analyzer
    analyzer = RepoAnalyzer(repo_info, repo_info.get("local_path"), ai_client)

    # Use more capable analyzer if available
    if ANALYZER_FRAMEWORK_AVAILABLE and ai_client and ai_client.llm_provider:
        print("Using enhanced analysis with unified framework")

    # Perform requested operations
    if args.analyze or not (args.readme or args.topics or args.description):
        # Perform repository analysis
        print("Analyzing repository...")
        results = analyzer.analyze(deep=args.deep)

        # Format and output results
        output = format_output(results, args.format)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)

    # Generate README recommendations
    if args.readme and ai_client:
        print("Generating README recommendations...")
        readme = ai_client.generate_readme(repo_info)

        # Check if we should commit the README
        if args.commit and repo_info.get("is_local"):
            local_path = repo_info.get("local_path")

            if not local_path:
                print("Error: No local repository path available for commit")
            else:
                # Write README to file
                readme_path = os.path.join(local_path, "README.md")
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(readme)
                print(f"README written to {readme_path}")

                # Commit README to repository
                success, message = commit_to_repository(
                    local_path,
                    "README.md",
                    args.commit_message,
                    args.push,
                    args.skip_hooks
                )

                if success:
                    print(f"README committed: {message}")
                else:
                    print(f"Failed to commit README: {message}")
        elif args.output:
            output_file = args.output if not args.analyze else f"{os.path.splitext(args.output)[0]}_readme.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(readme)
            print(f"README saved to {output_file}")
        else:
            print("\nREADME Recommendations:\n")
            print(readme)

    # Generate topic recommendations
    if args.topics and ai_client:
        print("Generating topic recommendations...")
        topics = ai_client.suggest_topics(repo_info)

        if args.output and not args.analyze:
            output_file = args.output if not args.readme else f"{os.path.splitext(args.output)[0]}_topics.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(topics))
            print(f"Topics saved to {output_file}")
        else:
            print("\nRecommended Topics:\n")
            for topic in topics:
                print(f"- {topic}")

    # Generate description recommendations
    if args.description and ai_client:
        # This would normally call a specific method, but for simplicity we'll reuse the analysis
        print("Generating description recommendations...")
        results = analyzer.analyze(deep=True)
        desc_results = results.get("description", {})

        suggestions = desc_results.get("suggestions", [])
        if not suggestions and "ai_analysis" in results:
            # Try to extract from AI analysis
            ai_desc = results.get("ai_analysis", {}).get("description", {})
            if isinstance(ai_desc, dict):
                suggestions = ai_desc.get("suggestions", [])

        if args.output and not (args.analyze or args.readme or args.topics):
            output_file = args.output
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Current Description:\n")
                f.write(desc_results.get("content", "None") + "\n\n")
                f.write("Suggestions:\n")
                for suggestion in suggestions:
                    f.write(f"- {suggestion}\n")
            print(f"Description recommendations saved to {output_file}")
        else:
            print("\nDescription Recommendations:\n")
            print(f"Current: {desc_results.get('content', 'None')}")
            print("\nSuggestions:")
            for suggestion in suggestions:
                print(f"- {suggestion}")


if __name__ == "__main__":
    main()