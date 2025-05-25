Contributing Guide
==================

Thank you for your interest in contributing to GitHub Repository SEO Optimizer! This guide will help you get started.

Code of Conduct
---------------

Please read and follow our `Code of Conduct <https://github.com/chenxingqiang/repo-seo/blob/main/CODE_OF_CONDUCT.md>`_ to ensure a welcoming environment for all contributors.

Getting Started
---------------

1. Fork the Repository
~~~~~~~~~~~~~~~~~~~~~~

Fork the repository on GitHub and clone your fork locally:

.. code-block:: bash

   git clone https://github.com/YOUR_USERNAME/repo-seo.git
   cd repo-seo

2. Set Up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtual environment and install dependencies:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

3. Install Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pre-commit install

Development Workflow
--------------------

1. Create a Branch
~~~~~~~~~~~~~~~~~~

Create a new branch for your feature or fix:

.. code-block:: bash

   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix

2. Make Your Changes
~~~~~~~~~~~~~~~~~~~~

* Write clean, readable code
* Follow the existing code style
* Add docstrings to all functions and classes
* Update tests as needed

3. Run Tests
~~~~~~~~~~~~

Ensure all tests pass:

.. code-block:: bash

   # Run all tests
   python -m pytest

   # Run specific test file
   python -m pytest tests/test_specific.py

   # Run with coverage
   python -m pytest --cov=src

4. Check Code Quality
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run linting
   flake8 src tests

   # Run type checking
   mypy src

   # Format code
   black src tests

5. Commit Your Changes
~~~~~~~~~~~~~~~~~~~~~~

Use conventional commits format:

.. code-block:: bash

   git commit -m "feat: add new provider for XYZ"
   git commit -m "fix: resolve issue with rate limiting"
   git commit -m "docs: update installation guide"

6. Push and Create PR
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git push origin feature/your-feature-name

Then create a Pull Request on GitHub.

Contribution Guidelines
-----------------------

Code Style
~~~~~~~~~~

* Follow PEP 8
* Use type hints where possible
* Maximum line length: 88 characters (Black default)
* Use descriptive variable names

Documentation
~~~~~~~~~~~~~

* Update documentation for new features
* Add docstrings following Google style:

.. code-block:: python

   def function_name(param1: str, param2: int) -> bool:
       """Brief description of function.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
           
       Raises:
           ValueError: When param1 is empty
       """

Testing
~~~~~~~

* Write tests for new features
* Maintain or improve code coverage
* Use pytest fixtures for common setups
* Mock external API calls

Example test:

.. code-block:: python

   def test_new_feature():
       """Test description."""
       # Arrange
       input_data = {"key": "value"}
       
       # Act
       result = new_feature(input_data)
       
       # Assert
       assert result == expected_value

Pull Request Process
--------------------

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Testing**: Describe how you tested your changes
4. **Screenshots**: Include if applicable
5. **Related Issues**: Link any related issues

PR Template:

.. code-block:: markdown

   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests added/updated

Areas for Contribution
----------------------

Good First Issues
~~~~~~~~~~~~~~~~~

Look for issues labeled ``good first issue`` on GitHub.

Feature Requests
~~~~~~~~~~~~~~~~

* New LLM provider integrations
* Additional output formats
* Performance improvements
* UI/UX enhancements

Documentation
~~~~~~~~~~~~~

* Improve existing documentation
* Add more examples
* Translate documentation
* Create video tutorials

Testing
~~~~~~~

* Increase test coverage
* Add integration tests
* Test edge cases
* Performance benchmarks

Release Process
---------------

Maintainers follow this process:

1. Update version in ``setup.py``
2. Update ``CHANGELOG.rst``
3. Create release PR
4. Tag release after merge
5. Build and publish to PyPI

Questions?
----------

* Open a `Discussion <https://github.com/chenxingqiang/repo-seo/discussions>`_
* Join our community chat
* Email the maintainers

Thank you for contributing! 🎉 