Troubleshooting Guide
=====================

This guide helps you resolve common issues with the GitHub Repository SEO Optimizer.

Installation Issues
-------------------

pip installation fails
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``pip install`` command fails with dependency errors.

**Solution**:

1. Ensure you have Python 3.8 or higher:

   .. code-block:: bash

      python --version

2. Upgrade pip:

   .. code-block:: bash

      pip install --upgrade pip

3. Install in a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install github-repo-seo-optimizer

GitHub CLI not found
~~~~~~~~~~~~~~~~~~~~

**Problem**: Error message "GitHub CLI (gh) not found".

**Solution**:

Install GitHub CLI based on your operating system:

* **macOS**: ``brew install gh``
* **Windows**: ``winget install --id GitHub.cli``
* **Linux**: See `GitHub CLI installation guide <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>`_

Authentication Issues
---------------------

GitHub authentication failed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: "Authentication failed" or "Bad credentials" error.

**Solution**:

1. Re-authenticate with GitHub CLI:

   .. code-block:: bash

      gh auth logout
      gh auth login

2. Choose the correct authentication method (browser recommended)
3. Ensure you have the necessary permissions (repo scope)

API key not working
~~~~~~~~~~~~~~~~~~~

**Problem**: LLM provider returns "Invalid API key" error.

**Solution**:

1. Verify the environment variable is set:

   .. code-block:: bash

      echo $OPENAI_API_KEY  # Or other provider key

2. Check the API key is valid in the provider's dashboard
3. Ensure no extra spaces or quotes in the key
4. Try setting the key directly in the command:

   .. code-block:: bash

      OPENAI_API_KEY="your-key" python repo_seo.py username

Runtime Errors
--------------

Rate limit exceeded
~~~~~~~~~~~~~~~~~~~

**Problem**: "API rate limit exceeded" error from GitHub.

**Solution**:

1. Wait for the rate limit to reset (usually 1 hour)
2. Use the ``--delay`` option to slow down requests:

   .. code-block:: bash

      python repo_seo.py username --delay 2

3. Process fewer repositories at once:

   .. code-block:: bash

      python repo_seo.py username --limit 10

No changes detected
~~~~~~~~~~~~~~~~~~~

**Problem**: Tool runs but doesn't make any changes.

**Solution**:

1. Check if repositories already have good descriptions and topics
2. Try a different LLM provider for better results
3. Use ``--force`` to regenerate even if content exists
4. Check the dry-run output:

   .. code-block:: bash

      python repo_seo.py username --dry-run

Memory errors with large repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: "MemoryError" when processing large repositories.

**Solution**:

1. Limit the README content size in configuration
2. Process repositories individually instead of batch
3. Use a provider with smaller context requirements (e.g., local provider)

Provider-Specific Issues
------------------------

OpenAI timeout errors
~~~~~~~~~~~~~~~~~~~~~

**Problem**: OpenAI API calls timeout.

**Solution**:

1. Increase timeout in configuration:

   .. code-block:: yaml

      provider:
        name: openai
        timeout: 60

2. Use a faster model (gpt-3.5-turbo instead of gpt-4)
3. Reduce the amount of context sent

Ollama connection refused
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: "Connection refused" when using Ollama.

**Solution**:

1. Ensure Ollama is running:

   .. code-block:: bash

      ollama serve

2. Check Ollama is listening on the correct port (default: 11434)
3. Pull the required model:

   .. code-block:: bash

      ollama pull llama2

Local provider poor quality
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Local provider generates low-quality descriptions.

**Solution**:

1. Use local provider for initial filtering only
2. Switch to an AI provider for important repositories
3. Customize the local provider templates

Common Error Messages
---------------------

"Repository not found"
~~~~~~~~~~~~~~~~~~~~~~

**Causes**:

* Repository name is misspelled
* Repository is private and you lack access
* Repository was deleted or renamed

**Solution**: Verify the repository exists and you have access.

"Insufficient permissions"
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Causes**:

* GitHub token lacks necessary scopes
* You're not the repository owner
* Organization restrictions

**Solution**: Ensure your GitHub authentication has ``repo`` scope.

"Invalid configuration"
~~~~~~~~~~~~~~~~~~~~~~~

**Causes**:

* Syntax error in YAML configuration file
* Invalid provider name
* Missing required fields

**Solution**: Validate your configuration file and check the documentation.

Getting Help
------------

If you're still experiencing issues:

1. Check the `GitHub Issues <https://github.com/chenxingqiang/repo-seo/issues>`_
2. Enable debug logging:

   .. code-block:: bash

      python repo_seo.py username --debug

3. Create a new issue with:
   
   * Your Python version
   * Operating system
   * Complete error message
   * Steps to reproduce

4. Join our community discussions for help 