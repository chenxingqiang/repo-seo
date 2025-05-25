Commit Message Fixer Guide
==========================

This guide explains how to use the Commit Message Fixer to automatically format your Git commit messages according to the Conventional Commits standard.

Overview
--------

The Commit Message Fixer is a Git hook that automatically formats your commit messages to follow the `Conventional Commits <https://www.conventionalcommits.org/>`_ specification, ensuring consistent and meaningful commit history.

Installation
------------

Quick Setup
~~~~~~~~~~~

Run the setup script to install the commit hook:

.. code-block:: bash

   python src/setup_commit_hook.py

This will:

1. Make the commit message fixer script executable
2. Install it as a Git commit-msg hook
3. Configure it to run automatically on every commit

Manual Setup
~~~~~~~~~~~~

If you prefer manual installation:

.. code-block:: bash

   # Make the script executable
   chmod +x src/commit_message_fixer.py

   # Create a symbolic link in the hooks directory
   ln -s ../../src/commit_message_fixer.py .git/hooks/commit-msg

Commit Message Format
---------------------

The Conventional Commits format follows this structure:

.. code-block:: text

   <type>(<scope>): <description>

   [optional body]

   [optional footer(s)]

Types
~~~~~

The following types are supported:

.. list-table:: Commit Types
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Description
   * - ``feat``
     - A new feature
   * - ``fix``
     - A bug fix
   * - ``docs``
     - Documentation only changes
   * - ``style``
     - Changes that don't affect code meaning (whitespace, formatting)
   * - ``refactor``
     - Code changes that neither fix bugs nor add features
   * - ``perf``
     - Code changes that improve performance
   * - ``test``
     - Adding or correcting tests
   * - ``build``
     - Changes to build system or dependencies
   * - ``ci``
     - Changes to CI configuration files and scripts
   * - ``chore``
     - Other changes that don't modify src or test files
   * - ``revert``
     - Reverts a previous commit

Examples
~~~~~~~~

Good commit messages:

.. code-block:: text

   feat(auth): add OAuth2 authentication support
   
   fix(api): resolve memory leak in data processing
   
   docs(readme): update installation instructions
   
   refactor(core): simplify error handling logic
   
   test(utils): add unit tests for string helpers

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

Simply commit as usual, and the hook will format your message:

.. code-block:: bash

   # Your input
   git commit -m "add new login feature"
   
   # Automatically formatted to
   feat: add new login feature

With Scope
~~~~~~~~~~

Include a scope to specify the affected area:

.. code-block:: bash

   # Your input
   git commit -m "fix login bug in authentication"
   
   # Automatically formatted to
   fix(auth): fix login bug in authentication

Multi-line Messages
~~~~~~~~~~~~~~~~~~~

For detailed commits with body:

.. code-block:: bash

   git commit

Then in your editor:

.. code-block:: text

   feat(api): implement rate limiting
   
   Add rate limiting to prevent API abuse:
   - 100 requests per minute for authenticated users
   - 20 requests per minute for anonymous users
   - Custom limits for premium accounts
   
   Closes #123

Smart Type Detection
--------------------

The fixer automatically suggests commit types based on file changes:

File-based Detection
~~~~~~~~~~~~~~~~~~~~

.. list-table:: Auto-detection Rules
   :header-rows: 1
   :widths: 40 60

   * - File Pattern
     - Suggested Type
   * - ``test_*.py``, ``*_test.py``, ``*.test.js``
     - ``test``
   * - ``README*``, ``*.md``, ``docs/*``
     - ``docs``
   * - ``*.css``, ``*.scss``, ``*.style.*``
     - ``style``
   * - ``Dockerfile``, ``docker-compose.yml``
     - ``build``
   * - ``.github/workflows/*``, ``*.yml`` (CI files)
     - ``ci``
   * - ``package.json``, ``requirements.txt``
     - ``build``

Content-based Detection
~~~~~~~~~~~~~~~~~~~~~~~

The fixer also analyzes commit message content:

.. code-block:: text

   # Input: "fixed the login bug"
   # Detected: "fix" keyword → type: fix
   
   # Input: "added new feature for users"
   # Detected: "added" keyword → type: feat
   
   # Input: "updated documentation"
   # Detected: "documentation" keyword → type: docs

Branch Naming Convention
------------------------

The tool also validates branch names:

Valid Formats
~~~~~~~~~~~~~

.. code-block:: text

   <number>-<type>-<description>

Examples:

.. code-block:: text

   123-feat-user-authentication
   456-fix-memory-leak
   789-docs-api-guide

Invalid branch names will trigger a warning but won't block commits.

Configuration
-------------

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

Create a ``.commitlintrc.json`` file in your project root:

.. code-block:: json

   {
     "types": [
       "feat", "fix", "docs", "style", "refactor",
       "perf", "test", "build", "ci", "chore", "revert"
     ],
     "scope": {
       "required": false,
       "allowed": ["api", "auth", "core", "ui", "docs"]
     },
     "subject": {
       "minLength": 10,
       "maxLength": 72
     }
   }

Disable for Specific Commits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To bypass the hook temporarily:

.. code-block:: bash

   git commit -m "your message" --no-verify

Advanced Features
-----------------

Emoji Support
~~~~~~~~~~~~~

Enable emoji prefixes for visual clarity:

.. code-block:: bash

   # Set environment variable
   export COMMIT_FIXER_EMOJI=true

Result:

.. code-block:: text

   ✨ feat(auth): add OAuth2 support
   🐛 fix(api): resolve memory leak
   📚 docs(readme): update installation
   ♻️ refactor(core): simplify logic

Jira/Issue Integration
~~~~~~~~~~~~~~~~~~~~~~

Automatically append issue numbers:

.. code-block:: bash

   # On branch: 123-feat-login
   git commit -m "add login feature"
   
   # Result: feat: add login feature (#123)

Team Conventions
~~~~~~~~~~~~~~~~

Enforce team-specific rules:

.. code-block:: python

   # In .git/hooks/commit-msg (custom section)
   
   # Require scope for features and fixes
   if commit_type in ['feat', 'fix'] and not scope:
       print("ERROR: Scope required for feat and fix commits")
       sys.exit(1)
   
   # Require issue reference
   if not re.search(r'#\d+', message):
       print("WARNING: No issue reference found")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Hook not running:**

.. code-block:: bash

   # Check if hook is executable
   ls -la .git/hooks/commit-msg
   
   # Make it executable
   chmod +x .git/hooks/commit-msg

**Python not found:**

.. code-block:: bash

   # Update shebang in commit_message_fixer.py
   #!/usr/bin/env python3

**Encoding issues:**

Ensure your Git is configured for UTF-8:

.. code-block:: bash

   git config --global i18n.commitencoding utf-8

Debugging
~~~~~~~~~

Enable debug mode for detailed output:

.. code-block:: bash

   export COMMIT_FIXER_DEBUG=true
   git commit -m "test message"

Integration with Other Tools
----------------------------

VS Code Integration
~~~~~~~~~~~~~~~~~~~

Install the "Conventional Commits" extension for VS Code to get commit message suggestions in the editor.

Pre-commit Framework
~~~~~~~~~~~~~~~~~~~~

Add to ``.pre-commit-config.yaml``:

.. code-block:: yaml

   repos:
     - repo: local
       hooks:
         - id: commit-message-fixer
           name: Fix commit messages
           entry: python src/commit_message_fixer.py
           language: python
           stages: [commit-msg]

CI/CD Integration
~~~~~~~~~~~~~~~~~

Validate commit messages in CI:

.. code-block:: yaml

   # GitHub Actions example
   - name: Validate commits
     run: |
       git log --format=%s -n 10 | python scripts/validate_commits.py

Best Practices
--------------

1. **Be Specific**: Use clear, descriptive messages
2. **Use Present Tense**: "add feature" not "added feature"
3. **Keep It Short**: Subject line under 72 characters
4. **Reference Issues**: Include issue numbers when applicable
5. **Group Related Changes**: One commit per logical change
6. **Use Scope Wisely**: Scope should be a noun describing a section

Examples of Good vs Bad
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Commit Message Examples
   :header-rows: 1
   :widths: 50 50

   * - ❌ Bad
     - ✅ Good
   * - "fix bug"
     - "fix(auth): resolve login timeout issue"
   * - "update stuff"
     - "refactor(api): simplify request handling"
   * - "WIP"
     - "feat(ui): add user profile page [WIP]"
   * - "misc changes"
     - "chore: update dependencies and format code"

Next Steps
----------

* Set up :doc:`/development/contributing` guidelines for your team
* Configure :doc:`/guides/batch_processing` to check commit quality
* Learn about :doc:`/api/modules` for programmatic commit analysis 