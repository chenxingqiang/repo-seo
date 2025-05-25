#!/usr/bin/env python3
"""
Common utility functions for the GitHub Repository SEO Optimizer.

This module contains utility functions that are used throughout the project.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("repo-seo")


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging with the specified log level.
    
    Args:
        log_level: The log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logger.setLevel(numeric_level)


def run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr.
    
    Args:
        command: The command to run, as a list of strings.
        cwd: The working directory to run the command in.
        
    Returns:
        A tuple containing the exit code, stdout, and stderr.
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        logger.error(f"Error running command {' '.join(command)}: {e}")
        return 1, "", str(e)


def save_json(data: Any, filename: str) -> bool:
    """Save data to a JSON file.
    
    Args:
        data: The data to save.
        filename: The filename to save to.
        
    Returns:
        True if the data was saved successfully, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filename}: {e}")
        return False


def load_json(filename: str) -> Optional[Any]:
    """Load data from a JSON file.
    
    Args:
        filename: The filename to load from.
        
    Returns:
        The loaded data, or None if the file could not be loaded.
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filename}: {e}")
        return None


def generate_timestamp() -> str:
    """Generate a timestamp string.
    
    Returns:
        A timestamp string in the format YYYYMMDD_HHMMSS.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def is_valid_topic(topic: str) -> bool:
    """Check if a topic is valid according to GitHub's rules.
    
    Args:
        topic: The topic to check.
        
    Returns:
        True if the topic is valid, False otherwise.
    """
    # GitHub topics must be between 1 and 35 characters long
    if not topic or len(topic) > 35:
        return False
    
    # GitHub topics can only contain alphanumeric characters, hyphens, and underscores
    if not all(c.isalnum() or c in ['-', '_'] for c in topic):
        return False
    
    # GitHub topics cannot start with a hyphen
    if topic.startswith('-'):
        return False
    
    return True


def sanitize_topics(topics: List[str]) -> List[str]:
    """Sanitize a list of topics according to GitHub's rules.
    
    Args:
        topics: The list of topics to sanitize.
        
    Returns:
        A list of sanitized topics.
    """
    sanitized = []
    
    for topic in topics:
        # Convert to lowercase
        topic = topic.lower()
        
        # Replace spaces with hyphens
        topic = topic.replace(' ', '-')
        
        # Remove invalid characters
        topic = ''.join(c for c in topic if c.isalnum() or c in ['-', '_'])
        
        # Remove leading hyphens
        topic = topic.lstrip('-')
        
        # Truncate to 35 characters
        topic = topic[:35]
        
        if topic and topic not in sanitized:
            sanitized.append(topic)
    
    return sanitized


def truncate_string(text: str, max_length: int, ellipsis: str = "...") -> str:
    """Truncate a string to a maximum length.
    
    Args:
        text: The string to truncate.
        max_length: The maximum length of the string.
        ellipsis: The ellipsis to append to the truncated string.
        
    Returns:
        The truncated string.
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(ellipsis)] + ellipsis


def is_github_cli_installed() -> bool:
    """Check if the GitHub CLI is installed.
    
    Returns:
        True if the GitHub CLI is installed, False otherwise.
    """
    returncode, _, _ = run_command(["gh", "--version"])
    return returncode == 0


def is_github_cli_authenticated() -> bool:
    """Check if the GitHub CLI is authenticated.
    
    Returns:
        True if the GitHub CLI is authenticated, False otherwise.
    """
    returncode, _, _ = run_command(["gh", "auth", "status"])
    return returncode == 0 