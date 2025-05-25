# Quick Start Guide for repo-seo-optimizer

## Installation

### From PyPI (when published)
```bash
pip install repo-seo-optimizer
```

### From Source
```bash
git clone https://github.com/chenxingqiang/repo-seo.git
cd repo-seo
pip install .
```

### Development Installation
```bash
git clone https://github.com/chenxingqiang/repo-seo.git
cd repo-seo
pip install -e .
```

## Basic Usage

### 1. Analyze a Repository
```bash
# Analyze current directory
repo-seo analyze

# Analyze specific repository
repo-seo analyze -r /path/to/repo
```

### 2. Optimize a Single Repository
```bash
# Optimize with local provider (no API key needed)
repo-seo optimize

# Optimize with OpenAI
repo-seo optimize -p openai -k YOUR_API_KEY

# Save results to file
repo-seo optimize -o results.json
```

### 3. Batch Optimize Multiple Repositories
```bash
# Optimize all your GitHub repositories
repo-seo batch

# Limit to 10 repositories
repo-seo batch -m 10

# Use specific provider
repo-seo batch -p anthropic -k YOUR_API_KEY
```

### 4. Sync Forked Repositories
```bash
# Sync all forks
repo-seo sync

# Force sync even with conflicts
repo-seo sync --force

# Limit to 5 repositories
repo-seo sync -m 5
```

## Python API Usage

```python
from repo_seo import RepoAnalyzer, AIClient

# Initialize analyzer
analyzer = RepoAnalyzer('/path/to/repo')

# Run analysis
results = analyzer.analyze()
print(f"Language: {results['language']}")
print(f"Topics: {results['topics']}")

# Use with AI provider
ai_client = AIClient(provider='openai', api_key='YOUR_KEY')
# ... use AI client for advanced features
```

## Environment Variables

You can set API keys as environment variables:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

## Common Use Cases

### 1. Improve Repository Discoverability
```bash
# Analyze and get recommendations
repo-seo optimize --dry-run

# Apply optimizations
repo-seo optimize
```

### 2. Maintain Multiple Projects
```bash
# Batch optimize all repositories
repo-seo batch --provider openai

# Keep forks up to date
repo-seo sync
```

### 3. CI/CD Integration
```yaml
# GitHub Actions example
- name: Optimize Repository SEO
  run: |
    pip install repo-seo-optimizer
    repo-seo optimize --provider local
```

## Tips

1. Start with the `local` provider to test without API costs
2. Use `--dry-run` to preview changes before applying
3. Set up environment variables for API keys to avoid typing them
4. Use batch mode for maintaining multiple repositories efficiently

## Getting Help

```bash
# General help
repo-seo --help

# Command-specific help
repo-seo optimize --help
repo-seo batch --help
```

# 查看版本
repo-seo --version

# 查看帮助
repo-seo --help

# 分析仓库
repo-seo analyze

# 优化仓库
repo-seo optimize

# 批量优化
repo-seo batch

# 同步fork
repo-seo sync

# 查看可用的LLM提供商
repo-seo providers 