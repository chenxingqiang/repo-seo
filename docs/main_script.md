# GitHub Repository SEO Optimizer - Main Script

This document provides detailed information about the main script (`repo_seo.py`) in the GitHub Repository SEO Optimizer.

## Overview

The main script (`repo_seo.py`) is the entry point for the GitHub Repository SEO Optimizer. It provides a command-line interface for optimizing GitHub repositories for better discoverability through improved descriptions, topics, and documentation.

## Command-Line Interface

The script provides the following command-line options:

```
usage: repo_seo.py [-h] [--repo REPO] [--limit LIMIT] [--dry-run] [--skip-private] [--output OUTPUT] [--provider {local,openai,ollama,anthropic}] username

GitHub Repository SEO Optimizer

positional arguments:
  username              GitHub username

optional arguments:
  -h, --help            show this help message
  --repo REPO           Specific repository to optimize
  --limit LIMIT         Maximum number of repositories to process (default: 100)
  --dry-run             Show changes without applying them
  --skip-private        Skip private repositories
  --output OUTPUT       Output file for results (default: seo_results_YYYYMMDD_HHMMSS.json)
  --provider {local,openai,ollama,anthropic}
                        LLM provider to use (default: local)
```

## Main Functions

### `main()`

The main function parses command-line arguments and orchestrates the optimization process.

```python
def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="GitHub Repository SEO Optimizer")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--repo", help="Specific repository to optimize")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of repositories to process")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--skip-private", action="store_true", help="Skip private repositories")
    parser.add_argument("--output", default=f"seo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", help="Output file for results")
    parser.add_argument("--provider", default="local", choices=["local", "openai", "ollama", "anthropic"], help="LLM provider to use")

    args = parser.parse_args()

    # Print banner
    print_colored("\nGitHub Repository SEO Optimizer", Colors.HEADER)
    print_colored("================================\n", Colors.HEADER)

    results = []

    if args.repo:
        # Optimize a specific repository
        result = optimize_repository(args.username, args.repo, args.dry_run, args.provider)
        results.append(result)
    else:
        # Get all repositories for the user
        repos = get_user_repos(args.username, args.limit)

        # Filter out private repositories if requested
        if args.skip_private:
            repos = [repo for repo in repos if not repo.get("isPrivate", False)]
            print_colored(f"Filtered to {len(repos)} public repositories", Colors.BLUE)

        # Optimize each repository
        for i, repo in enumerate(repos):
            repo_name = repo["name"]
            print_colored(f"\nProcessing repository {i+1}/{len(repos)}", Colors.HEADER)

            result = optimize_repository(args.username, repo_name, args.dry_run, args.provider)
            results.append(result)

            # Add a small delay to avoid rate limiting
            if i < len(repos) - 1:
                time.sleep(1)

    # Save results to file
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print_colored(f"\nResults saved to {args.output}", Colors.GREEN)
    print_colored("\nDone!", Colors.HEADER)
```

### `optimize_repository()`

This function optimizes a single repository by generating SEO-friendly descriptions and topics.

```python
def optimize_repository(username: str, repo_name: str, dry_run: bool = False, llm_provider: str = "local") -> Dict[str, Any]:
    """Optimize a repository for SEO."""
    print_colored(f"\nOptimizing repository: {repo_name}", Colors.HEADER)

    # Get repository details
    repo = get_repo_details(username, repo_name)
    if not repo:
        return {"status": "error", "message": f"Could not fetch details for repository {repo_name}"}

    # Get repository languages
    languages = get_repo_languages(username, repo_name)

    # Get repository topics
    current_topics = get_repo_topics(username, repo_name)

    # Get repository README
    readme = get_repo_readme(username, repo_name)

    # Initialize the LLM provider
    try:
        provider = get_provider(llm_provider)
    except Exception as e:
        print_colored(f"Error initializing LLM provider '{llm_provider}': {str(e)}", Colors.RED)
        print_colored("Falling back to local provider", Colors.YELLOW)
        provider = get_provider("local")

    # Generate SEO-friendly description and topics
    new_description = provider.generate_description(
        repo_name=repo_name,
        languages=list(languages.keys()),
        topics=current_topics,
        readme=readme
    )

    new_topics = provider.generate_topics(
        repo_name=repo_name,
        languages=list(languages.keys()),
        current_topics=current_topics,
        readme=readme
    )

    # Display changes
    print_colored("\nChanges for repository:", Colors.HEADER)
    print_colored(f"Name: {repo_name}", Colors.BLUE)

    print_colored("Current description:", Colors.BLUE)
    print(repo.get("description", "None"))
    print_colored("New description:", Colors.GREEN)
    print(new_description)

    print_colored("Current topics:", Colors.BLUE)
    print(", ".join(current_topics) if current_topics else "None")

    # Validate topics to show what will actually be sent to GitHub
    validated_topics = []
    for topic in new_topics:
        valid_topic = validate_github_topic(topic)
        if valid_topic and valid_topic not in validated_topics:
            validated_topics.append(valid_topic)

    print_colored("New topics:", Colors.GREEN)
    print(", ".join(new_topics))

    if set(new_topics) != set(validated_topics):
        print_colored("Validated topics (what will be sent to GitHub):", Colors.YELLOW)
        print(", ".join(validated_topics))

    # Store results
    results = {
        "repository": repo_name,
        "url": repo.get("url", ""),
        "description": {
            "before": repo.get("description", ""),
            "after": new_description
        },
        "topics": {
            "before": current_topics,
            "after": validated_topics
        },
        "readme": {
            "before_length": len(readme),
            "updated": False
        }
    }

    # Apply changes if not in dry run mode
    if not dry_run:
        # Update repository description
        if new_description != repo.get("description", ""):
            update_repo_description(username, repo_name, new_description)
            repo["description"] = new_description

        # Update repository topics
        if set(validated_topics) != set(current_topics):
            update_repo_topics(username, repo_name, validated_topics)

        # Create or update README if needed
        if not readme or len(readme) < 500:
            readme_updated = create_or_update_readme(
                username, repo_name, repo, languages, validated_topics, readme
            )
            results["readme"]["updated"] = readme_updated
    else:
        print_colored("\nDRY RUN: No changes were applied", Colors.YELLOW)

    return results
```

## GitHub API Functions

The script includes several functions for interacting with the GitHub API:

### `get_user_repos()`

Gets a list of repositories for a GitHub user.

```python
def get_user_repos(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get a list of repositories for a GitHub user."""
    print_colored(f"Fetching repositories for user: {username}", Colors.BLUE)

    cmd = ["gh", "repo", "list", username, "--limit", str(limit), "--json", "name,description,isPrivate"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"Error fetching repositories: {stderr}", Colors.RED)
        return []

    try:
        repos = json.loads(stdout)
        print_colored(f"Found {len(repos)} repositories", Colors.GREEN)
        return repos
    except json.JSONDecodeError:
        print_colored(f"Error parsing repository data: {stdout}", Colors.RED)
        return []
```

### `get_repo_details()`

Gets detailed information about a repository.

```python
def get_repo_details(username: str, repo_name: str) -> Dict[str, Any]:
    """Get detailed information about a repository."""
    cmd = ["gh", "repo", "view", f"{username}/{repo_name}", "--json", "name,description,url,isPrivate"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"Error fetching repository details for {repo_name}: {stderr}", Colors.RED)
        return {}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print_colored(f"Error parsing repository details for {repo_name}: {stdout}", Colors.RED)
        return {}
```

### `get_repo_languages()`

Gets the languages used in a repository.

```python
def get_repo_languages(username: str, repo_name: str) -> Dict[str, float]:
    """Get the languages used in a repository."""
    cmd = ["gh", "api", f"repos/{username}/{repo_name}/languages"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"Error fetching languages for {repo_name}: {stderr}", Colors.RED)
        return {}

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print_colored(f"Error parsing languages data for {repo_name}: {stdout}", Colors.RED)
        return {}
```

### `get_repo_topics()`

Gets the topics for a repository.

```python
def get_repo_topics(username: str, repo_name: str) -> List[str]:
    """Get the topics for a repository."""
    cmd = ["gh", "api", f"repos/{username}/{repo_name}/topics"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"Error fetching topics for {repo_name}: {stderr}", Colors.RED)
        return []

    try:
        topics_data = json.loads(stdout)
        return topics_data.get("names", [])
    except json.JSONDecodeError:
        print_colored(f"Error parsing topics data for {repo_name}: {stdout}", Colors.RED)
        return []
```

### `get_repo_readme()`

Gets the README content for a repository.

```python
def get_repo_readme(username: str, repo_name: str) -> str:
    """Get the README content for a repository."""
    cmd = ["gh", "api", f"repos/{username}/{repo_name}/readme", "--header", "Accept: application/vnd.github.raw"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"No README found for {repo_name}", Colors.YELLOW)
        return ""

    return stdout
```

### `update_repo_description()`

Updates the description of a repository.

```python
def update_repo_description(username: str, repo_name: str, description: str) -> bool:
    """Update the description of a repository."""
    cmd = ["gh", "api", f"repos/{username}/{repo_name}", "-X", "PATCH", "-f", f"description={description}"]
    stdout, stderr, returncode = run_command(cmd)

    if returncode != 0:
        print_colored(f"Error updating description for {repo_name}: {stderr}", Colors.RED)
        return False

    print_colored(f"Updated description for {repo_name}", Colors.GREEN)
    return True
```

### `update_repo_topics()`

Updates the topics of a repository.

```python
def update_repo_topics(username: str, repo_name: str, topics: List[str]) -> bool:
    """Update the topics of a repository."""
    # Validate and filter topics
    valid_topics = []
    invalid_topics = []

    for topic in topics:
        valid_topic = validate_github_topic(topic)
        if valid_topic and valid_topic not in valid_topics:
            valid_topics.append(valid_topic)
        else:
            invalid_topics.append(topic)

    # Log any invalid topics that were filtered out
    if invalid_topics:
        print_colored(f"Filtered out invalid topics: {', '.join(invalid_topics)}", Colors.YELLOW)

    # Ensure we don't exceed GitHub's limit
    if len(valid_topics) > 20:
        print_colored(f"Limiting to 20 topics (from {len(valid_topics)})", Colors.YELLOW)
        valid_topics = valid_topics[:20]

    topics_json = json.dumps({"names": valid_topics})
    cmd = ["gh", "api", f"repos/{username}/{repo_name}/topics", "-X", "PUT", "--input", "-"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=topics_json)

    if process.returncode != 0:
        print_colored(f"Error updating topics for {repo_name}: {stderr}", Colors.RED)
        return False

    print_colored(f"Updated topics for {repo_name}: {', '.join(valid_topics)}", Colors.GREEN)
    return True
```

### `create_or_update_readme()`

Creates or updates the README.md file for a repository.

```python
def create_or_update_readme(username: str, repo_name: str, repo_data: Dict[str, Any],
                          languages: Dict[str, float], topics: List[str], current_readme: str) -> bool:
    """Create or update the README.md file for a repository."""
    # If there's already a substantial README, don't modify it
    if current_readme and len(current_readme) >= 500:
        print_colored(f"Repository {repo_name} already has a substantial README", Colors.BLUE)
        return False

    print_colored(f"Generating README for {repo_name}", Colors.BLUE)

    # Generate a basic README
    readme_content = f"""# {repo_name}

{repo_data.get('description', '')}

## Overview

This repository contains code for {repo_name.replace('-', ' ').replace('_', ' ').title()}.

## Technologies

"""

    # Add languages
    if languages:
        readme_content += "### Languages\n\n"
        for lang, percentage in languages.items():
            percentage_str = f"{percentage:.1f}%" if isinstance(percentage, float) else f"{percentage}%"
            readme_content += f"- {lang}: {percentage_str}\n"

        readme_content += "\n"

    # Add topics
    if topics:
        readme_content += "### Topics\n\n"
        for topic in topics:
            readme_content += f"- {topic}\n"

        readme_content += "\n"

    # Add installation and usage sections
    readme_content += """## Installation

```bash
# Add installation instructions here
```

## Usage

```bash
# Add usage examples here
```

## License

This project is licensed under the terms of the license included in the repository.

"""

    # Create a temporary file with the README content
    with open("README.md.tmp", "w") as f:
        f.write(readme_content)

    # Use gh api to create or update the README.md file
    cmd = [
        "gh", "api", f"repos/{username}/{repo_name}/contents/README.md",
        "-X", "PUT",
        "-F", "message=Add auto-generated README",
        "-F", f"content=@README.md.tmp"
    ]

    # If the README already exists, we need to provide the SHA
    if current_readme:
        # Get the current README file metadata
        cmd_get = ["gh", "api", f"repos/{username}/{repo_name}/contents/README.md"]
        stdout, stderr, returncode = run_command(cmd_get)

        if returncode == 0:
            try:
                readme_data = json.loads(stdout)
                cmd.append("-F")
                cmd.append(f"sha={readme_data.get('sha', '')}")
            except json.JSONDecodeError:
                print_colored(f"Error parsing README metadata for {repo_name}: {stdout}", Colors.RED)
                return False

    stdout, stderr, returncode = run_command(cmd)

    # Clean up temporary file
    try:
        os.remove("README.md.tmp")
    except:
        pass

    if returncode != 0:
        print_colored(f"Error updating README for {repo_name}: {stderr}", Colors.RED)
        return False

    print_colored(f"Updated README for {repo_name}", Colors.GREEN)
    return True
```

## Utility Functions

### `run_command()`

Runs a shell command and returns stdout, stderr, and return code.

```python
def run_command(command: List[str]) -> Tuple[str, str, int]:
    """Run a shell command and return stdout, stderr, and return code."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode
```

### `print_colored()`

Prints colored text to the terminal.

```python
def print_colored(text: str, color: str) -> None:
    """Print colored text to the terminal."""
    print(f"{color}{text}{Colors.ENDC}")
```

## Dependencies

The script depends on the following Python modules:

- `os`: For file operations
- `sys`: For system operations
- `json`: For JSON parsing and serialization
- `re`: For regular expressions
- `subprocess`: For running shell commands
- `time`: For adding delays
- `datetime`: For generating timestamps
- `argparse`: For parsing command-line arguments
- `typing`: For type hints

It also depends on the GitHub CLI (`gh`) for interacting with the GitHub API.

## Requirements

- Python 3.6 or higher
- GitHub CLI (`gh`) installed and authenticated
- Required Python packages installed (see `requirements.txt`)

## Examples

### Optimizing a Specific Repository

```bash
python repo_seo.py chenxingqiang --repo repo-seo
```

### Optimizing All Repositories for a User

```bash
python repo_seo.py chenxingqiang
```

### Dry Run Mode

```bash
python repo_seo.py chenxingqiang --dry-run
```

### Using a Specific LLM Provider

```bash
python repo_seo.py chenxingqiang --provider openai
```