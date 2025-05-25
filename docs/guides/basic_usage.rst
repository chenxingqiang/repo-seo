Basic Usage Guide
=================

This guide covers the fundamental usage patterns of the GitHub Repository SEO Optimizer.

Getting Started
---------------

The GitHub Repository SEO Optimizer is designed to be simple to use while providing powerful features for optimizing your GitHub repositories.

Prerequisites
~~~~~~~~~~~~~

Before using the tool, ensure you have:

1. Python 3.8 or higher installed
2. GitHub CLI authenticated (``gh auth login``)
3. Required dependencies installed (``pip install -r requirements.txt``)

Basic Workflow
--------------

The typical workflow for using the tool consists of:

1. **Analyze**: Examine repositories to identify optimization opportunities
2. **Generate**: Create optimized descriptions and topics
3. **Review**: Preview the proposed changes
4. **Apply**: Update the repositories with optimizations

Step 1: Analyze Your Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by analyzing your repositories:

.. code-block:: bash

   # Analyze all repositories for a user
   python repo_seo.py username --dry-run

   # Analyze a specific repository
   python repo_seo.py username --repo repository-name --dry-run

The ``--dry-run`` flag lets you see what changes would be made without applying them.

Step 2: Choose Your Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Select an appropriate LLM provider based on your needs:

.. code-block:: bash

   # Use the local provider (no API key needed)
   python repo_seo.py username --provider local

   # Use OpenAI for higher quality
   python repo_seo.py username --provider openai

   # Use Anthropic for sophisticated analysis
   python repo_seo.py username --provider anthropic

Step 3: Apply Optimizations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you're satisfied with the proposed changes:

.. code-block:: bash

   # Apply optimizations to all repositories
   python repo_seo.py username

   # Apply to specific repository
   python repo_seo.py username --repo repository-name

Common Scenarios
----------------

Optimizing New Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you create a new repository, optimize it immediately:

.. code-block:: bash

   # Create repository with GitHub CLI
   gh repo create my-new-repo --public

   # Optimize it
   python repo_seo.py username --repo my-new-repo

Batch Processing Multiple Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Process multiple repositories efficiently:

.. code-block:: bash

   # Process first 20 repositories
   python repo_seo.py username --limit 20

   # Process only public repositories
   python repo_seo.py username --skip-private

Updating Existing Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Re-optimize repositories after major updates:

.. code-block:: bash

   # Check current SEO status
   gh repo view username/repo-name --json description,repositoryTopics

   # Re-optimize
   python repo_seo.py username --repo repo-name

Working with Different Languages
--------------------------------

The tool automatically detects repository languages and optimizes accordingly:

Python Projects
~~~~~~~~~~~~~~~

For Python projects, the tool will:

* Identify Python-specific frameworks (Django, Flask, FastAPI)
* Suggest relevant Python ecosystem topics
* Generate descriptions highlighting Python features

.. code-block:: bash

   python repo_seo.py username --repo my-python-project

JavaScript/TypeScript Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For JavaScript/TypeScript projects:

* Detect frontend frameworks (React, Vue, Angular)
* Identify Node.js usage
* Suggest web development topics

.. code-block:: bash

   python repo_seo.py username --repo my-js-project

Multi-Language Projects
~~~~~~~~~~~~~~~~~~~~~~~

For projects with multiple languages:

* Analyze the primary language
* Consider all languages in topic generation
* Create comprehensive descriptions

Output and Results
------------------

Understanding Output Files
~~~~~~~~~~~~~~~~~~~~~~~~~~

The tool generates JSON output files with optimization results:

.. code-block:: json

   {
     "repository": "example-repo",
     "url": "https://github.com/username/example-repo",
     "description": {
       "before": "Old description",
       "after": "New SEO-optimized description"
     },
     "topics": {
       "before": ["old-topic"],
       "after": ["python", "api", "rest", "automation"]
     },
     "optimization_score": 85
   }

Interpreting Results
~~~~~~~~~~~~~~~~~~~~

* **Description Changes**: Compare before/after to see improvements
* **Topic Suggestions**: New topics for better discoverability
* **Optimization Score**: Overall SEO improvement (0-100)

Best Practices
--------------

1. Regular Optimization
~~~~~~~~~~~~~~~~~~~~~~~

* Optimize new repositories immediately after creation
* Re-optimize after major updates or refactoring
* Review optimizations quarterly

2. Provider Selection
~~~~~~~~~~~~~~~~~~~~~

* Use **local** provider for quick, basic optimizations
* Use **OpenAI/Anthropic** for important or complex repositories
* Use **Ollama** for privacy-sensitive projects

3. Topic Management
~~~~~~~~~~~~~~~~~~~

* Keep topics relevant and specific
* Limit to 5-10 most important topics
* Update topics as project evolves

4. Description Writing
~~~~~~~~~~~~~~~~~~~~~~

* Keep descriptions concise (under 150 characters)
* Include key technologies and purpose
* Make it searchable and clear

Troubleshooting Common Issues
-----------------------------

No Changes Detected
~~~~~~~~~~~~~~~~~~~

If the tool reports no changes needed:

.. code-block:: bash

   # Force regeneration with different provider
   python repo_seo.py username --repo repo-name --provider openai

   # Check current optimization status
   gh repo view username/repo-name --json description,repositoryTopics

API Rate Limits
~~~~~~~~~~~~~~~

If you hit GitHub API rate limits:

.. code-block:: bash

   # Check rate limit status
   gh api rate_limit

   # Process fewer repositories
   python repo_seo.py username --limit 5

   # Add delay between operations
   python repo_seo.py username --delay 2

Provider Errors
~~~~~~~~~~~~~~~

If LLM providers fail:

.. code-block:: bash

   # Fall back to local provider
   python repo_seo.py username --provider local

   # Check API key configuration
   echo $OPENAI_API_KEY

Advanced Usage
--------------

Custom Output Formats
~~~~~~~~~~~~~~~~~~~~~

Save results in different formats:

.. code-block:: bash

   # Custom output file
   python repo_seo.py username --output my-seo-results.json

   # Generate report
   python repo_seo.py username --report

Filtering Repositories
~~~~~~~~~~~~~~~~~~~~~~

Target specific types of repositories:

.. code-block:: bash

   # Only process repositories with no description
   python repo_seo.py username --filter no-description

   # Only process repositories with few topics
   python repo_seo.py username --filter needs-topics

Integration with CI/CD
~~~~~~~~~~~~~~~~~~~~~~

Integrate SEO optimization into your workflow:

.. code-block:: yaml

   # GitHub Actions example
   name: Optimize Repository SEO
   on:
     repository_dispatch:
       types: [created]
   
   jobs:
     optimize:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Optimize SEO
           run: |
             python repo_seo.py ${{ github.repository_owner }} \
               --repo ${{ github.event.repository.name }}

Next Steps
----------

After mastering basic usage:

* Explore :doc:`llm_providers` for provider-specific features
* Learn about :doc:`batch_processing` for large-scale operations
* Set up :doc:`commit_fixer` for better commit messages
* Read the :doc:`/api/modules` for programmatic usage 