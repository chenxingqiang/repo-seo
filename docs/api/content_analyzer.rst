Content Analyzer API
====================

This module analyzes repository content to extract meaningful information for SEO optimization.

ContentAnalyzer Class
---------------------

.. automodule:: content_analyzer.analyzer
   :members:
   :undoc-members:
   :show-inheritance:

Analysis Models
---------------

.. automodule:: content_analyzer.models
   :members:
   :undoc-members:
   :show-inheritance:

Extractors
----------

.. automodule:: content_analyzer.extractors
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Analysis
~~~~~~~~~~~~~~

.. code-block:: python

   from content_analyzer import ContentAnalyzer
   
   # Initialize analyzer
   analyzer = ContentAnalyzer()
   
   # Analyze repository content
   analysis = analyzer.analyze(
       readme_content="# My Project\n...",
       file_structure=["src/", "tests/", "docs/"],
       languages={"Python": 80, "JavaScript": 20}
   )
   
   print(analysis.main_topics)
   print(analysis.suggested_keywords)
   print(analysis.content_quality_score)

Advanced Analysis
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze with custom extractors
   from content_analyzer.extractors import (
       TechnologyExtractor,
       FrameworkExtractor,
       PurposeExtractor
   )
   
   analyzer = ContentAnalyzer(
       extractors=[
           TechnologyExtractor(),
           FrameworkExtractor(),
           PurposeExtractor()
       ]
   )
   
   # Deep analysis
   deep_analysis = analyzer.deep_analyze(
       repo_path="/path/to/repo",
       include_code_analysis=True,
       include_dependency_analysis=True
   ) 