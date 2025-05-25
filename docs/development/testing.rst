Testing Guide
=============

This guide covers testing practices for the GitHub Repository SEO Optimizer project.

Test Structure
--------------

The test suite is organized as follows:

.. code-block:: text

   tests/
   ├── unit/                 # Unit tests for individual components
   │   ├── test_providers.py
   │   ├── test_github_client.py
   │   ├── test_seo_generator.py
   │   └── test_content_analyzer.py
   ├── integration/          # Integration tests
   │   ├── test_workflow.py
   │   └── test_api_integration.py
   ├── fixtures/            # Test data and fixtures
   └── conftest.py         # Pytest configuration

Running Tests
-------------

Basic Commands
~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run with verbose output
   pytest -v

   # Run specific test file
   pytest tests/unit/test_providers.py

   # Run specific test
   pytest tests/unit/test_providers.py::test_openai_provider

Coverage Reports
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run with coverage
   pytest --cov=src

   # Generate HTML coverage report
   pytest --cov=src --cov-report=html

   # View coverage report
   open htmlcov/index.html

Test Categories
~~~~~~~~~~~~~~~

Run specific categories of tests:

.. code-block:: bash

   # Unit tests only
   pytest tests/unit/

   # Integration tests only
   pytest tests/integration/

   # Fast tests only
   pytest -m "not slow"

   # Skip tests requiring API keys
   pytest -m "not requires_api_key"

Writing Tests
-------------

Unit Tests
~~~~~~~~~~

Example unit test:

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch
   from llm_providers import OpenAIProvider

   class TestOpenAIProvider:
       """Test OpenAI provider functionality."""
       
       @pytest.fixture
       def provider(self):
           """Create provider instance."""
           return OpenAIProvider(api_key="test-key")
       
       def test_generate_description(self, provider):
           """Test description generation."""
           # Arrange
           repo_data = {
               "name": "test-repo",
               "language": "Python",
               "readme": "# Test Repository"
           }
           
           # Mock API response
           with patch('openai.ChatCompletion.create') as mock_create:
               mock_create.return_value = {
                   "choices": [{
                       "message": {
                           "content": "A test repository for Python"
                       }
                   }]
               }
               
               # Act
               result = provider.generate_description(repo_data)
               
               # Assert
               assert result == "A test repository for Python"
               mock_create.assert_called_once()

Integration Tests
~~~~~~~~~~~~~~~~~

Example integration test:

.. code-block:: python

   import pytest
   from repo_seo import RepoSEOOptimizer

   @pytest.mark.integration
   class TestWorkflow:
       """Test complete optimization workflow."""
       
       @pytest.mark.requires_api_key
       def test_full_optimization(self, github_token):
           """Test full repository optimization."""
           # Arrange
           optimizer = RepoSEOOptimizer(
               provider="local",
               github_token=github_token
           )
           
           # Act
           result = optimizer.optimize_repository(
               owner="test-owner",
               repo="test-repo",
               dry_run=True
           )
           
           # Assert
           assert result.success
           assert result.description
           assert len(result.topics) > 0

Test Fixtures
~~~~~~~~~~~~~

Common fixtures in ``conftest.py``:

.. code-block:: python

   import pytest
   import os

   @pytest.fixture
   def github_token():
       """Provide GitHub token for tests."""
       token = os.getenv("GITHUB_TOKEN")
       if not token:
           pytest.skip("GitHub token not available")
       return token

   @pytest.fixture
   def sample_repo_data():
       """Sample repository data."""
       return {
           "name": "awesome-project",
           "description": "A project",
           "language": "Python",
           "topics": ["python"],
           "stars": 100,
           "readme_content": "# Awesome Project\n..."
       }

   @pytest.fixture
   def mock_github_client():
       """Mock GitHub client."""
       client = Mock()
       client.get_repository.return_value = {
           "name": "test-repo",
           "description": "Test description"
       }
       return client

Mocking External Services
-------------------------

GitHub API
~~~~~~~~~~

.. code-block:: python

   from unittest.mock import patch

   @patch('github_client.GitHubClient')
   def test_with_mock_github(mock_client):
       """Test with mocked GitHub client."""
       # Configure mock
       mock_instance = mock_client.return_value
       mock_instance.get_repository.return_value = {
           "name": "repo",
           "topics": ["python", "testing"]
       }
       
       # Use in test
       # ...

LLM Providers
~~~~~~~~~~~~~

.. code-block:: python

   @patch('openai.ChatCompletion.create')
   def test_openai_mock(mock_create):
       """Test with mocked OpenAI."""
       mock_create.return_value = {
           "choices": [{
               "message": {"content": "Generated content"}
           }]
       }
       
       # Test code using OpenAI
       # ...

Test Markers
------------

Available markers:

.. code-block:: python

   # Slow tests
   @pytest.mark.slow
   def test_large_batch_processing():
       pass

   # Tests requiring API keys
   @pytest.mark.requires_api_key
   def test_openai_integration():
       pass

   # Skip on CI
   @pytest.mark.skipif(
       os.getenv("CI") == "true",
       reason="Skip on CI"
   )
   def test_local_only():
       pass

   # Expected failures
   @pytest.mark.xfail(
       reason="Feature not implemented yet"
   )
   def test_future_feature():
       pass

Performance Testing
-------------------

Benchmark Tests
~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest

   @pytest.mark.benchmark
   def test_performance(benchmark):
       """Test performance of SEO generation."""
       def generate_seo():
           # Code to benchmark
           pass
       
       result = benchmark(generate_seo)
       assert result

Load Testing
~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.slow
   def test_batch_performance():
       """Test batch processing performance."""
       import time
       
       start = time.time()
       # Process 100 repositories
       duration = time.time() - start
       
       assert duration < 60  # Should complete in 1 minute

Debugging Tests
---------------

Useful debugging techniques:

.. code-block:: bash

   # Run with print statements
   pytest -s

   # Drop into debugger on failure
   pytest --pdb

   # Show local variables on failure
   pytest -l

   # Run last failed tests
   pytest --lf

   # Run tests matching pattern
   pytest -k "test_provider"

Continuous Integration
----------------------

GitHub Actions configuration:

.. code-block:: yaml

   name: Tests
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.8, 3.9, "3.10", "3.11"]
       
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: ${{ matrix.python-version }}
       - name: Install dependencies
         run: |
           pip install -r requirements.txt
           pip install -r requirements-dev.txt
       - name: Run tests
         run: |
           pytest --cov=src --cov-report=xml
       - name: Upload coverage
         uses: codecov/codecov-action@v1

Best Practices
--------------

1. **Test Independence**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mock External Services**: Don't make real API calls
5. **Test Edge Cases**: Include boundary conditions
6. **Keep Tests Fast**: Mock slow operations
7. **Use Fixtures**: Share common setup code
8. **Test One Thing**: Each test should verify one behavior 