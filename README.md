# GitHub Repository SEO Optimizer

A Python tool for automatically enhancing GitHub repository SEO by analyzing content, generating optimized descriptions, keywords, and documentation.

## Overview

This tool helps improve the discoverability of your GitHub repositories by:

1. Analyzing repository content, code languages, and existing documentation
2. Generating SEO-friendly descriptions and topics
3. Creating or updating README files with comprehensive information
4. Tracking and reporting on optimization changes

## Features

- **Repository Analysis**: Examines repository content, languages, and existing metadata
- **Description Optimization**: Generates concise, keyword-rich descriptions
- **Topic Generation**: Creates relevant topics based on repository content and technologies
- **README Enhancement**: Creates or updates README files with structured, SEO-friendly content
- **Batch Processing**: Optimize multiple repositories in a single run
- **Dry Run Mode**: Preview changes without applying them
- **Detailed Reporting**: Generate reports of all changes made

## Installation

```bash
# Clone the repository
git clone https://github.com/chenxingqiang/repo-seo.git
cd repo-seo

# Make the script executable
chmod +x repo_seo.py
```

## Requirements

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Required Python packages:
  - No external packages required (uses standard library)

## Usage

```bash
# Basic usage (optimize all repositories)
./repo_seo.py chenxingqiang

# Dry run (show changes without applying them)
./repo_seo.py chenxingqiang --dry-run

# Skip private repositories
./repo_seo.py chenxingqiang --skip-private

# Limit the number of repositories to process
./repo_seo.py chenxingqiang --limit 10

# Save results to a JSON file
./repo_seo.py chenxingqiang --output results.json
```

## How It Works

1. **Repository Fetching**: Uses GitHub CLI to fetch repository information
2. **Content Analysis**: Analyzes repository languages, topics, and README content
3. **SEO Generation**: Creates optimized descriptions and topics based on analysis
4. **Content Updates**: Updates repository metadata and README files via GitHub API
5. **Reporting**: Generates detailed reports of changes made

## Example Output

```
Fetching repositories for user: chenxingqiang
Found 85 repositories

Optimizing repository: repo-seo
Current description:
A Python tool for automatically enhancing GitHub repository SEO by analyzing content, generating optimized descriptions, keywords, and documentation.
New description:
A Python tool for automatically enhancing GitHub repository SEO by analyzing content, generating optimized descriptions, keywords, and documentation.
Current topics:
None
New topics:
python, repo, seo, github, repository

Updated topics for repo-seo
README for repo-seo is already substantial. Skipping update.

Summary:
Total repositories: 85
Optimized: 78
Skipped: 7
Dry run: False
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Keywords

github, seo, repository, optimization, python, automation, metadata, description, topics, readme
