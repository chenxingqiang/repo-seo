#!/usr/bin/env python3
import os
import sys
import re
import subprocess
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Commit types and descriptions
COMMIT_TYPES = {
    'feat': 'New feature',
    'fix': 'Bug fix',
    'docs': 'Documentation changes',
    'style': 'Changes that do not affect code meaning (whitespace, formatting, etc.)',
    'refactor': 'Code changes that neither fix bugs nor add features',
    'perf': 'Code changes that improve performance',
    'test': 'Adding missing tests or correcting existing tests',
    'build': 'Changes that affect the build system or external dependencies',
    'ci': 'Changes to CI configuration files and scripts',
    'chore': 'Other changes that do not modify src or test files'
}

def parse_commit_message(message):
    """Parse commit message"""
    pattern = r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore)(?:\((?P<scope>[^)]+)\))?: (?P<description>.+)$'
    match = re.match(pattern, message)
    if match and match.group('type') in COMMIT_TYPES:
        result = match.groupdict()
        # Ensure empty scope returns None instead of empty string
        if not result['scope'] or result['scope'].strip() == '':
            result['scope'] = None
        return result
    return None

def suggest_commit_type(files_changed):
    """Suggest commit type based on changed files"""
    if not files_changed:
        return 'feat'  # Default type

    # File type checks ordered by priority
    type_patterns = [
        (r'(^|/)(test_.*|.*_test)\.(py|js|ts|go|java|cpp|cs)$', 'test'),
        (r'(^|/)(package\.json|requirements\.txt|go\.mod|Dockerfile|setup\.py|Makefile|CMakeLists\.txt)$', 'build'),
        (r'(^|/)(\.github/|\.gitlab-ci\.yml|\.travis\.yml|jenkins|circleci)', 'ci'),
        (r'(^|/)(.*\.(md|rst|doc|docx|pdf))$', 'docs'),  # Removed txt as it might be other types
        (r'\.(css|scss|less|html|json|xml|yaml|yml)$', 'style')
    ]

    # First check build files
    for file in files_changed:
        file = file.lower()
        if re.search(type_patterns[1][0], file):  # Check build file pattern
            return 'build'

    # Then check other types
    for file in files_changed:
        file = file.lower()
        for pattern, commit_type in type_patterns:
            if re.search(pattern, file):
                return commit_type

    return 'feat'  # Default to new feature

def get_changed_files():
    """Get list of files changed in the most recent commit"""
    try:
        # Try to get files in staging area
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                              capture_output=True, text=True, check=True)
        files = result.stdout.strip().split('\n')

        # If no files in staging area, get changes in working directory
        if not files or files == ['']:
            result = subprocess.run(['git', 'ls-files', '--modified', '--others', '--exclude-standard'],
                                  capture_output=True, text=True, check=True)
            files = result.stdout.strip().split('\n')

        return [f for f in files if f]  # Filter empty strings
    except subprocess.CalledProcessError:
        logger.error("Unable to get list of changed files")
        return []

def fix_commit_message(old_message):
    """Fix commit message"""
    # First check if it's already a valid commit message
    parsed = parse_commit_message(old_message)
    if parsed:
        logger.info("Commit message format is correct, no changes needed")
        return old_message

    # Get changed files
    files_changed = get_changed_files()
    suggested_type = suggest_commit_type(files_changed)

    # Clean and format message
    message = old_message.strip()
    first_line = message.split('\n')[0]

    # Build new commit message
    new_message = f"{suggested_type}: {first_line}"

    logger.info(f"Original commit message: {old_message}")
    logger.info(f"Modified commit message: {new_message}")

    return new_message

def check_branch_name():
    """Check if branch name follows conventions"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True, check=True)
        branch = result.stdout.strip()
        pattern = r'^\d+-(feat|fix|docs|style|refactor|perf|test|build|ci|chore)-[a-z0-9-]+$'

        if branch == 'main' or branch == 'master':
            logger.info("Currently on main branch, skipping branch name check")
            return True

        if not re.match(pattern, branch):
            logger.warning(f"Branch name '{branch}' does not follow conventions")
            logger.info("Branch name should follow format: <number>-<type>-<description>")
            logger.info("Example: 123-feat-add-new-feature")
            return False

        logger.info(f"Branch name '{branch}' follows conventions")
        return True
    except subprocess.CalledProcessError:
        logger.error("Unable to get current branch name")
        return False

def print_commit_guide():
    """Print commit message guide"""
    logger.info("\nCommit Message Guide:")
    logger.info("Format: <type>(<scope>): <description>")
    logger.info("\nAvailable commit types:")
    for type_, desc in COMMIT_TYPES.items():
        logger.info(f"  {type_:<8} - {desc}")
    logger.info("\nExamples:")
    logger.info("  feat(auth): Add user authentication")
    logger.info("  fix(api): Fix user query API bug")
    logger.info("  docs: Update README documentation")

def main():
    if len(sys.argv) < 2:
        logger.error("Please provide commit message file path")
        sys.exit(1)

    commit_msg_file = sys.argv[1]

    # Check branch name
    if not check_branch_name():
        print_commit_guide()
        sys.exit(1)

    try:
        # Read current commit message
        with open(commit_msg_file, 'r') as f:
            current_message = f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read commit message file: {e}")
        sys.exit(1)

    # Fix commit message
    new_message = fix_commit_message(current_message)

    try:
        # Write new commit message
        with open(commit_msg_file, 'w') as f:
            f.write(new_message)
        logger.info("Updated commit message")
    except Exception as e:
        logger.error(f"Failed to write new commit message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
