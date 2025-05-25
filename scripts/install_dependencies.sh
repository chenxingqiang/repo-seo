#!/bin/bash
# Installation script for GitHub Repository SEO Optimizer

set -e  # Exit on error

echo "Installing GitHub Repository SEO Optimizer dependencies..."

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed. Please install Python and pip first."
    exit 1
fi

# Check if Python version is at least 3.8
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python version must be at least 3.8. Found version $python_version"
    exit 1
fi

# Install core dependencies
echo "Installing core dependencies..."
pip install -r requirements.txt

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Warning: GitHub CLI (gh) is not installed."
    echo "The GitHub CLI is required for this tool to work."
    echo "Please install it from: https://cli.github.com/manual/installation"
    
    # Detect OS and provide installation instructions
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "For Debian/Ubuntu:"
        echo "  sudo apt install gh"
        echo "For Fedora/CentOS/RHEL:"
        echo "  sudo dnf install gh"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "For macOS (using Homebrew):"
        echo "  brew install gh"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "For Windows (using Scoop):"
        echo "  scoop install gh"
        echo "Or download from: https://github.com/cli/cli/releases/latest"
    fi
else
    echo "GitHub CLI is already installed."
    echo "Checking if you're authenticated..."
    if ! gh auth status &> /dev/null; then
        echo "You need to authenticate with GitHub CLI:"
        echo "  gh auth login"
    else
        echo "You're already authenticated with GitHub CLI."
    fi
fi

# Install spaCy models
echo "Installing spaCy models..."
python -m spacy download en_core_web_sm

# Install NLTK data
echo "Installing NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Make scripts executable
echo "Making scripts executable..."
chmod +x repo-seo.py
chmod +x src/*.py
if [ -d "examples" ]; then
    chmod +x examples/*.py
fi

echo "Installation complete!"
echo "You can now use the GitHub Repository SEO Optimizer:"
echo "  python repo-seo.py optimize <github_username>"
echo "  python repo-seo.py setup-hook"
echo "  python repo-seo.py test" 