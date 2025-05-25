#!/bin/bash
# Build script for repo-seo-optimizer package

set -e

echo "🏗️  Building repo-seo-optimizer package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
twine check dist/*

echo "✅ Package built successfully!"
echo "📁 Distribution files:"
ls -la dist/

echo ""
echo "🚀 To upload to PyPI:"
echo "   twine upload dist/*"
echo ""
echo "🧪 To test install locally:"
echo "   pip install dist/*.whl" 