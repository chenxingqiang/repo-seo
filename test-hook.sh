#!/bin/sh

echo "Running pre-commit hook..."

# Check for trailing whitespace
if git diff --cached --check; then
    echo "No trailing whitespace found."
else
    echo "Error: Trailing whitespace found. Please remove it before committing."
    exit 1
fi

# Check for large files
MAX_SIZE_KB=1024
for file in $(git diff --cached --name-only); do
    size=$(git cat-file -s :$file)
    if [ $size -gt $((MAX_SIZE_KB * 1024)) ]; then
        echo "Error: File $file is larger than ${MAX_SIZE_KB}KB"
        exit 1
    fi
done

echo "All checks passed."
exit 0