#!/bin/bash
# Script to run all tests with coverage reporting

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running tests for GitHub Repository SEO Optimizer...${NC}"
echo "======================================================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed.${NC}"
    echo "Please install it with: pip install pytest pytest-cov"
    exit 1
fi

# Run tests with coverage
echo -e "${BLUE}Running tests with coverage...${NC}"
pytest --cov=src tests/

# Generate HTML coverage report
echo -e "${BLUE}Generating HTML coverage report...${NC}"
pytest --cov=src --cov-report=html tests/

echo -e "${GREEN}Tests completed!${NC}"
echo "Coverage report is available in the htmlcov directory."
echo "Open htmlcov/index.html in your browser to view it."

# Run specific test files if provided
if [ $# -gt 0 ]; then
    echo -e "${BLUE}Running specific tests: $@${NC}"
    pytest "$@"
fi

echo "======================================================"
echo -e "${GREEN}All tests completed!${NC}" 