#!/bin/bash
# GitHub Repository SEO Optimizer Runner
# This script runs the SEO optimization for all repositories

# Set default values
USERNAME="chenxingqiang"
LIMIT=100
DRY_RUN=false
SKIP_PRIVATE=false
OUTPUT_FILE="seo_results_$(date +%Y%m%d_%H%M%S).json"

# Display help message
show_help() {
    echo "GitHub Repository SEO Optimizer Runner"
    echo ""
    echo "Usage: ./run_seo.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -u, --username      GitHub username (default: chenxingqiang)"
    echo "  -l, --limit         Maximum number of repositories to process (default: 100)"
    echo "  -d, --dry-run       Show changes without applying them"
    echo "  -s, --skip-private  Skip private repositories"
    echo "  -o, --output        Output file for results (default: seo_results_YYYYMMDD_HHMMSS.json)"
    echo ""
    echo "Example:"
    echo "  ./run_seo.sh --dry-run --limit 10"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -s|--skip-private)
            SKIP_PRIVATE=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build command
CMD="./repo_seo.py $USERNAME --limit $LIMIT --output $OUTPUT_FILE"

if [ "$DRY_RUN" = true ]; then
    CMD="$CMD --dry-run"
fi

if [ "$SKIP_PRIVATE" = true ]; then
    CMD="$CMD --skip-private"
fi

# Display command
echo "Running: $CMD"
echo ""

# Run command
eval $CMD

# Check if command was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "SEO optimization completed successfully!"
    echo "Results saved to: $OUTPUT_FILE"
else
    echo ""
    echo "Error: SEO optimization failed!"
    exit 1
fi
