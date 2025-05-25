# GitHub Topic Validation

This document provides detailed information about the topic validation functionality in the GitHub Repository SEO Optimizer.

## Overview

GitHub has specific requirements for repository topics:

1. Topics must contain only lowercase letters, numbers, and hyphens
2. No spaces are allowed (converted to hyphens)
3. Topics must start with a letter or number
4. Topics can't be longer than 35 characters

The GitHub Repository SEO Optimizer includes a robust validation function to ensure that all topics meet these requirements.

## Validation Function

The `validate_github_topic` function is responsible for validating and formatting topics according to GitHub's requirements:

```python
def validate_github_topic(topic: str) -> str:
    """
    Validate and format a topic string according to GitHub's requirements:
    - Must contain only lowercase letters, numbers, and hyphens
    - No spaces allowed (convert to hyphens)
    - Must start with a letter or number
    - Maximum length of 35 characters

    Returns a properly formatted topic or empty string if invalid.
    """
    # Handle None or empty strings
    if not topic:
        return ""

    # Convert to lowercase
    topic = topic.lower().strip()

    # Handle specific problematic cases
    if ',' in topic:
        # If topic contains commas, it might be multiple topics incorrectly combined
        return ""

    # Replace spaces and underscores with hyphens
    topic = re.sub(r'[\s_]+', '-', topic)

    # Remove any characters that aren't lowercase letters, numbers, or hyphens
    topic = re.sub(r'[^a-z0-9-]', '', topic)

    # Remove consecutive hyphens
    topic = re.sub(r'-+', '-', topic)

    # Remove leading and trailing hyphens
    topic = topic.strip('-')

    # Ensure it starts with a letter or number
    if not topic or not re.match(r'^[a-z0-9]', topic):
        return ""

    # Truncate to maximum length
    return topic[:35]
```

## Validation Rules

The function applies the following transformations to ensure topics meet GitHub's requirements:

1. **Lowercase Conversion**: All uppercase letters are converted to lowercase
   - Example: `Python` → `python`

2. **Space and Underscore Conversion**: Spaces and underscores are converted to hyphens
   - Example: `machine learning` → `machine-learning`
   - Example: `api_v2` → `api-v2`

3. **Invalid Character Removal**: Characters that aren't lowercase letters, numbers, or hyphens are removed
   - Example: `c++` → `c`
   - Example: `data.science` → `datascience`

4. **Consecutive Hyphen Collapse**: Multiple consecutive hyphens are collapsed into a single hyphen
   - Example: `machine--learning` → `machine-learning`

5. **Leading/Trailing Hyphen Removal**: Hyphens at the beginning or end of the topic are removed
   - Example: `-python-` → `python`

6. **Length Truncation**: Topics longer than 35 characters are truncated
   - Example: `abcdefghijklmnopqrstuvwxyz1234567890` → `abcdefghijklmnopqrstuvwxyz123456789`

7. **Comma Handling**: Topics containing commas are rejected (returned as empty string)
   - Example: `python,javascript` → `""`

8. **Empty Input Handling**: `None` or empty strings return an empty string
   - Example: `None` → `""`
   - Example: `""` → `""`
   - Example: `"   "` → `""`

## Usage

The `validate_github_topic` function is used in the `update_repo_topics` function to ensure that all topics meet GitHub's requirements before being sent to the GitHub API:

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

    # Send the validated topics to the GitHub API
    topics_json = json.dumps({"names": valid_topics})
    # ...
```

## Testing

The topic validation functionality is thoroughly tested in `tests/test_topic_validation.py`. The tests cover all the validation rules and edge cases to ensure the function works correctly.

## Common Issues

1. **Empty Result**: If a topic is returned as an empty string, it likely contains only invalid characters or commas.

2. **Unexpected Transformation**: If a topic is transformed in an unexpected way, check if it contains special characters, spaces, or uppercase letters.

3. **GitHub API Validation Failure**: If the GitHub API still returns a validation error, ensure that the topic meets all of GitHub's requirements and doesn't exceed the maximum length.

## References

- [GitHub Topics Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
- [GitHub API - Repository Topics](https://docs.github.com/en/rest/reference/repos#replace-all-repository-topics)