.. GitHub Repository SEO Optimizer documentation master file, created by
   sphinx-quickstart on Thu Jan 23 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GitHub Repository SEO Optimizer Documentation
=============================================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/chenxingqiang/repo-seo/blob/main/LICENSE
   :alt: License

Welcome to the documentation for the GitHub Repository SEO Optimizer!

**GitHub Repository SEO Optimizer** is a powerful tool designed to enhance the discoverability of GitHub repositories through automated optimization of descriptions, topics, and documentation.

Key Features
------------

* **Automated SEO Optimization**: Analyzes repositories and generates optimized descriptions and topics
* **Multiple LLM Providers**: Supports 8 different language model providers including OpenAI, Anthropic, and local models
* **Batch Processing**: Process multiple repositories at once
* **Commit Message Standardization**: Automatically formats commit messages to follow conventional standards
* **Multi-language Support**: Documentation available in English and Chinese

Quick Start
-----------

.. code-block:: bash

   # Install the package
   pip install github-repo-seo-optimizer

   # Optimize a single repository
   python repo_seo.py username --repo repository-name

   # Optimize all repositories for a user
   python repo_seo.py username

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guides/basic_usage
   guides/llm_providers
   guides/batch_processing
   guides/commit_fixer

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/llm_providers
   api/github_client
   api/seo_generator

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/contributing
   development/testing
   development/architecture

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   changelog
   faq
   troubleshooting

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Support
-------

* **GitHub Issues**: `Report bugs or request features <https://github.com/chenxingqiang/repo-seo/issues>`_
* **Documentation**: `Read the full documentation <https://repo-seo.readthedocs.io>`_
* **Source Code**: `View on GitHub <https://github.com/chenxingqiang/repo-seo>`_

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

