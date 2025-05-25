Frequently Asked Questions
==========================

This page answers common questions about the GitHub Repository SEO Optimizer.

General Questions
-----------------

What is GitHub Repository SEO Optimizer?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub Repository SEO Optimizer is a tool that automatically improves the discoverability of GitHub repositories by optimizing their descriptions, topics, and documentation using AI-powered analysis.

Why do I need to optimize my GitHub repositories?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizing your repositories helps:

* Increase visibility in GitHub search results
* Attract more contributors and users
* Better communicate your project's purpose
* Improve professional presentation

Is it safe to use?
~~~~~~~~~~~~~~~~~~~

Yes, the tool is safe to use:

* It only modifies repository metadata (description and topics)
* All changes can be previewed with ``--dry-run``
* It doesn't modify your code or commit history
* You maintain full control over what changes are applied

Installation & Setup
--------------------

Do I need API keys?
~~~~~~~~~~~~~~~~~~~

* **No** for basic usage with the local provider
* **Yes** for advanced AI providers (OpenAI, Anthropic, etc.)
* GitHub CLI authentication is always required

Which Python version is required?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3.8 or higher is required. Check your version:

.. code-block:: bash

   python --version

How do I authenticate with GitHub?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use GitHub CLI:

.. code-block:: bash

   gh auth login

Follow the prompts to authenticate via browser or token.

Usage Questions
---------------

How do I preview changes without applying them?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--dry-run`` flag:

.. code-block:: bash

   python repo_seo.py username --dry-run

Can I optimize private repositories?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, but they're skipped by default. To include them:

.. code-block:: bash

   python repo_seo.py username --include-private

How do I optimize only specific repositories?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--repo`` flag:

.. code-block:: bash

   python repo_seo.py username --repo specific-repo-name

What's the difference between LLM providers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Provider Comparison
   :header-rows: 1

   * - Provider
     - Quality
     - Cost
     - Privacy
   * - Local
     - Basic
     - Free
     - High (no data sent)
   * - OpenAI
     - Excellent
     - Paid
     - Data sent to OpenAI
   * - Anthropic
     - Excellent
     - Paid
     - Data sent to Anthropic
   * - Ollama
     - Good
     - Free
     - High (runs locally)

Troubleshooting
---------------

"GitHub CLI not found" error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install GitHub CLI:

* **macOS**: ``brew install gh``
* **Windows**: ``winget install --id GitHub.cli``
* **Linux**: See `GitHub CLI installation <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>`_

"Rate limit exceeded" error
~~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub has API rate limits. Solutions:

1. Wait for the limit to reset (usually 1 hour)
2. Process fewer repositories at once
3. Add delays between operations:

   .. code-block:: bash

      python repo_seo.py username --delay 2

"Invalid API key" error
~~~~~~~~~~~~~~~~~~~~~~~~

Check your API key:

1. Verify the environment variable is set correctly
2. Ensure the API key is valid and active
3. Check you're using the correct provider name

No changes detected
~~~~~~~~~~~~~~~~~~~

This can happen when:

1. Repositories are already well-optimized
2. The provider couldn't generate better content
3. Try a different provider for better results

Best Practices
--------------

How often should I run the optimizer?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **New repositories**: Immediately after creation
* **Active projects**: Monthly or after major updates
* **Stable projects**: Quarterly

Should I use different providers for different repos?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, consider:

* **Local provider**: Quick optimization for many repos
* **AI providers**: Important or complex projects
* **Ollama**: Privacy-sensitive projects

How many topics should a repository have?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Minimum**: 3-5 topics for basic discoverability
* **Optimal**: 5-10 relevant topics
* **Maximum**: GitHub allows up to 20 topics

Advanced Usage
--------------

Can I automate the optimization process?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, see :doc:`guides/batch_processing` for automation options including:

* Cron jobs
* GitHub Actions
* CI/CD integration

Can I customize the optimization rules?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, through:

* Configuration files
* Custom providers
* API usage

See :doc:`configuration` for details.

Can I use this for an organization?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes:

.. code-block:: bash

   python repo_seo.py --org organization-name

How do I contribute to the project?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See the `Contributing Guide <https://github.com/chenxingqiang/repo-seo/blob/main/CONTRIBUTING.md>`_ for details.

API & Integration
-----------------

Can I use this programmatically?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, see :doc:`api/modules` for API documentation.

Can I integrate with CI/CD?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, example GitHub Actions workflow:

.. code-block:: yaml

   - name: Optimize Repository SEO
     run: |
       pip install github-repo-seo-optimizer
       python repo_seo.py ${{ github.repository_owner }} \
         --repo ${{ github.event.repository.name }}

Does it work with GitLab or Bitbucket?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, only GitHub is supported. Other platforms may be added in future versions.

Getting Help
------------

Where can I get more help?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check the :doc:`troubleshooting` guide
2. Search `GitHub Issues <https://github.com/chenxingqiang/repo-seo/issues>`_
3. Create a new issue with details
4. Join our `Discord community <https://discord.gg/repo-seo>`_ (if available)

How do I report bugs?
~~~~~~~~~~~~~~~~~~~~~

Create an issue on GitHub with:

1. Your Python version
2. Operating system
3. Complete error message
4. Steps to reproduce

How do I request features?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open a feature request issue describing:

1. The problem you're trying to solve
2. Your proposed solution
3. Any alternatives you've considered 