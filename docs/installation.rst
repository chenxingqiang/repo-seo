Installation Guide
==================

This guide will help you install the GitHub Repository SEO Optimizer on your system.

Requirements
------------

Before installing, ensure you have the following prerequisites:

* Python 3.8 or higher
* pip (Python package installer)
* Git
* GitHub CLI (gh) - `Installation guide <https://cli.github.com/manual/installation>`_

System Requirements
~~~~~~~~~~~~~~~~~~~

* **Operating System**: Windows, macOS, or Linux
* **Memory**: At least 4GB RAM recommended
* **Disk Space**: 500MB free space

Installation Methods
--------------------

Using pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install the GitHub Repository SEO Optimizer is using pip:

.. code-block:: bash

   pip install github-repo-seo-optimizer

From Source
~~~~~~~~~~~

To install from source, follow these steps:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/chenxingqiang/repo-seo.git
      cd repo-seo

2. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

3. Install the package:

   .. code-block:: bash

      pip install -e .

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development purposes, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/chenxingqiang/repo-seo.git
   cd repo-seo
   pip install -r requirements-dev.txt
   pip install -e .

GitHub CLI Setup
----------------

The GitHub Repository SEO Optimizer requires GitHub CLI to be installed and authenticated.

1. Install GitHub CLI:

   * **macOS**: ``brew install gh``
   * **Windows**: ``winget install --id GitHub.cli``
   * **Linux**: See `official installation guide <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>`_

2. Authenticate with GitHub:

   .. code-block:: bash

      gh auth login

3. Verify authentication:

   .. code-block:: bash

      gh auth status

API Keys Configuration
----------------------

To use different LLM providers, you'll need to configure API keys:

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in your project root:

.. code-block:: bash

   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here

   # Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here

   # Google Gemini
   GEMINI_API_KEY=your_gemini_api_key_here

   # DeepSeek
   DEEPSEEK_API_KEY=your_deepseek_api_key_here

   # ZhiPu
   ZHIPU_API_KEY=your_zhipu_api_key_here

   # QianWen
   QIANWEN_API_KEY=your_qianwen_api_key_here

Or export them in your shell:

.. code-block:: bash

   export OPENAI_API_KEY="your_openai_api_key_here"
   export ANTHROPIC_API_KEY="your_anthropic_api_key_here"

Verifying Installation
----------------------

To verify the installation was successful:

1. Check the version:

   .. code-block:: bash

      python -c "import repo_seo; print(repo_seo.__version__)"

2. Run a test command:

   .. code-block:: bash

      python repo_seo.py --help

3. Test LLM providers:

   .. code-block:: bash

      python test_providers.py local

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'repo_seo'**
   Make sure you've installed the package correctly and are in the right Python environment.

**GitHub CLI not found**
   Ensure GitHub CLI is installed and available in your PATH.

**API Key errors**
   Double-check that your API keys are correctly set in environment variables.

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the :doc:`troubleshooting` guide
2. Search `existing issues <https://github.com/chenxingqiang/repo-seo/issues>`_
3. Create a new issue with detailed information about your problem

Next Steps
----------

After successful installation:

* Read the :doc:`quickstart` guide
* Configure your :doc:`configuration`
* Explore :doc:`guides/llm_providers` 