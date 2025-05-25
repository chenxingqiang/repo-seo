# Tests for GitHub Repository SEO Optimizer

This directory contains tests for the GitHub Repository SEO Optimizer project.

## Test Structure

The tests are organized into the following directories:

- **unit/**: Unit tests for individual components
  - `test_commit_message_fixer.py`: Tests for the commit message fixer
  - `test_repo_manager.py`: Tests for the repository manager
  
- **integration/**: Integration tests that test multiple components together
  - `test_git_integration.py`: Tests for Git integration
  
- **Root tests**:
  - `test_integration.py`: Main integration tests
  - `test_llm_providers.py`: Tests for LLM providers
  - `test_topic_validation.py`: Tests for topic validation

## Running Tests

You can run the tests using the provided `run_tests.sh` script:

```bash
# Make the script executable
chmod +x run_tests.sh

# Run all tests with coverage reporting
./run_tests.sh
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run a specific test file
pytest tests/unit/test_commit_message_fixer.py

# Run a specific test
pytest tests/unit/test_commit_message_fixer.py::test_format_commit_message
```

## Writing Tests

When adding new features, please follow these guidelines for writing tests:

1. **Unit Tests**: Write unit tests for individual functions and classes
   - Place them in the `tests/unit/` directory
   - Name the test file `test_<module_name>.py`
   - Use descriptive test function names: `test_<function_name>_<scenario>`

2. **Integration Tests**: Write integration tests for features that span multiple components
   - Place them in the `tests/integration/` directory
   - Focus on testing the interaction between components

3. **Test Coverage**: Aim for high test coverage
   - Use `pytest --cov=src` to check coverage
   - Aim for at least 80% coverage for critical components

4. **Mocking**: Use mocks for external dependencies
   - Use `pytest-mock` for mocking
   - Mock API calls, file system operations, etc.

## Test Dependencies

The tests require the following dependencies:

- pytest
- pytest-cov
- pytest-mock
- pytest-asyncio

These dependencies are listed in the `requirements.txt` file and will be installed when you run `install_dependencies.sh`.

## Continuous Integration

In the future, we plan to set up continuous integration to automatically run tests on pull requests and commits to the main branch. 