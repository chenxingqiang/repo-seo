SEO Generator API
=================

This module handles the generation of SEO-optimized content for repositories.

SEOGenerator Class
------------------

.. automodule:: seo_generator.seo_generator
   :members:
   :undoc-members:
   :show-inheritance:

SEO Models
----------

.. automodule:: seo_generator.models
   :members:
   :undoc-members:
   :show-inheritance:

Optimization Strategies
-----------------------

.. automodule:: seo_generator.strategies
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic SEO Generation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from seo_generator import SEOGenerator
   from llm_providers import OpenAIProvider
   
   # Initialize generator with provider
   provider = OpenAIProvider(api_key="your-key")
   generator = SEOGenerator(provider)
   
   # Generate SEO content
   seo_content = generator.generate(
       repo_name="awesome-project",
       current_description="A project",
       readme_content="# Awesome Project\n...",
       language="Python",
       stars=100
   )
   
   print(seo_content.description)
   print(seo_content.topics)

Custom Strategies
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Use custom optimization strategy
   from seo_generator.strategies import KeywordStrategy
   
   strategy = KeywordStrategy(
       focus_keywords=["machine-learning", "ai", "python"]
   )
   
   generator = SEOGenerator(
       provider=provider,
       strategy=strategy
   )
   
   # Generate with custom strategy
   seo_content = generator.generate(repo_data) 