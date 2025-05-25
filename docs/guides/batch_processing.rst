Batch Processing Guide
======================

This guide covers how to efficiently process multiple GitHub repositories using the SEO Optimizer.

Overview
--------

Batch processing allows you to optimize multiple repositories at once, saving time and ensuring consistency across your GitHub profile or organization.

Basic Batch Processing
----------------------

Simple Batch Operations
~~~~~~~~~~~~~~~~~~~~~~~

Process all repositories for a user:

.. code-block:: bash

   # Process all public repositories
   python repo_seo.py username

   # Include private repositories
   python repo_seo.py username --include-private

   # Limit the number of repositories
   python repo_seo.py username --limit 50

Filtering Options
~~~~~~~~~~~~~~~~~

Target specific types of repositories:

.. code-block:: bash

   # Only repositories without descriptions
   python repo_seo.py username --filter no-description

   # Only repositories with few topics (less than 3)
   python repo_seo.py username --filter needs-topics

   # Only recently updated repositories
   python repo_seo.py username --filter recent --days 30

   # Combine filters
   python repo_seo.py username --filter no-description,needs-topics

Advanced Batch Processing
-------------------------

Processing by Language
~~~~~~~~~~~~~~~~~~~~~~

Optimize repositories based on their primary language:

.. code-block:: bash

   # Only Python repositories
   python repo_seo.py username --language python

   # Only JavaScript/TypeScript repositories
   python repo_seo.py username --language javascript,typescript

   # Exclude specific languages
   python repo_seo.py username --exclude-language java,c++

Processing Organizations
~~~~~~~~~~~~~~~~~~~~~~~~

Process repositories for an entire organization:

.. code-block:: bash

   # Process organization repositories
   python repo_seo.py --org organization-name

   # Only process team repositories
   python repo_seo.py --org organization-name --team team-name

   # Process multiple organizations
   python repo_seo.py --org org1,org2,org3

Batch Configuration
-------------------

Configuration File
~~~~~~~~~~~~~~~~~~

Create a batch configuration file (``batch_config.yaml``):

.. code-block:: yaml

   # Batch processing configuration
   batch:
     # Maximum repositories to process
     limit: 100
     
     # Processing delay between repositories (seconds)
     delay: 2
     
     # Skip repositories that were recently processed
     skip_recent_hours: 24
     
     # Filters
     filters:
       - no-description
       - needs-topics
     
     # Languages to include
     languages:
       - python
       - javascript
       - typescript
     
     # Repositories to exclude
     exclude:
       - test-repo
       - deprecated-project
     
   # Provider configuration
   provider:
     name: openai
     model: gpt-3.5-turbo
     temperature: 0.7
   
   # Output configuration
   output:
     format: json
     directory: ./batch_results
     separate_files: true

Using the configuration:

.. code-block:: bash

   python repo_seo.py username --config batch_config.yaml

Parallel Processing
~~~~~~~~~~~~~~~~~~~

Enable parallel processing for faster execution:

.. code-block:: bash

   # Process with 4 workers
   python repo_seo.py username --parallel 4

   # Auto-detect optimal worker count
   python repo_seo.py username --parallel auto

Progress Tracking
-----------------

Real-time Progress
~~~~~~~~~~~~~~~~~~

Monitor batch processing progress:

.. code-block:: bash

   # Show progress bar
   python repo_seo.py username --progress

   # Verbose output with details
   python repo_seo.py username --verbose

   # Save progress to file
   python repo_seo.py username --progress-file batch_progress.log

Resume Interrupted Batches
~~~~~~~~~~~~~~~~~~~~~~~~~~

Resume processing from where it stopped:

.. code-block:: bash

   # Create checkpoint file
   python repo_seo.py username --checkpoint batch_checkpoint.json

   # Resume from checkpoint
   python repo_seo.py username --resume batch_checkpoint.json

Batch Results
-------------

Output Formats
~~~~~~~~~~~~~~

Choose how to save batch results:

.. code-block:: bash

   # Single JSON file (default)
   python repo_seo.py username --output results.json

   # Separate files per repository
   python repo_seo.py username --output-dir ./results --separate

   # CSV format for analysis
   python repo_seo.py username --output results.csv --format csv

   # Markdown report
   python repo_seo.py username --output report.md --format markdown

Result Analysis
~~~~~~~~~~~~~~~

Analyze batch processing results:

.. code-block:: python

   import json
   import pandas as pd
   
   # Load results
   with open('batch_results.json', 'r') as f:
       results = json.load(f)
   
   # Convert to DataFrame
   df = pd.DataFrame(results)
   
   # Analysis examples
   print(f"Total repositories processed: {len(df)}")
   print(f"Successfully optimized: {df['status'].eq('success').sum()}")
   print(f"Failed: {df['status'].eq('error').sum()}")
   
   # Topics analysis
   topics_added = df['topics_added'].sum()
   print(f"Total topics added: {topics_added}")

Error Handling
--------------

Handling Failures
~~~~~~~~~~~~~~~~~

Configure how to handle errors during batch processing:

.. code-block:: bash

   # Continue on errors (default)
   python repo_seo.py username --on-error continue

   # Stop on first error
   python repo_seo.py username --on-error stop

   # Retry failed repositories
   python repo_seo.py username --retry-failed 3

Error Logging
~~~~~~~~~~~~~

Detailed error logging for troubleshooting:

.. code-block:: bash

   # Log errors to file
   python repo_seo.py username --error-log batch_errors.log

   # Include debug information
   python repo_seo.py username --debug

Rate Limiting
~~~~~~~~~~~~~

Handle API rate limits gracefully:

.. code-block:: bash

   # Automatic rate limit handling
   python repo_seo.py username --respect-rate-limit

   # Custom delay between requests
   python repo_seo.py username --delay 5

   # Exponential backoff on rate limit
   python repo_seo.py username --backoff exponential

Performance Optimization
------------------------

Caching
~~~~~~~

Enable caching to avoid redundant API calls:

.. code-block:: bash

   # Enable caching
   python repo_seo.py username --cache

   # Set cache directory
   python repo_seo.py username --cache-dir ./cache

   # Cache expiration (hours)
   python repo_seo.py username --cache-expire 24

Batch Strategies
~~~~~~~~~~~~~~~~

Different strategies for different scenarios:

**Quick Scan Strategy**

For initial assessment:

.. code-block:: bash

   python repo_seo.py username \
     --provider local \
     --limit 1000 \
     --parallel 8 \
     --cache

**Quality Optimization Strategy**

For important repositories:

.. code-block:: bash

   python repo_seo.py username \
     --provider openai \
     --filter important \
     --delay 3 \
     --retry-failed 3

**Incremental Updates Strategy**

For regular maintenance:

.. code-block:: bash

   python repo_seo.py username \
     --filter updated-since-last-run \
     --checkpoint daily_checkpoint.json \
     --cache

Automation
----------

Scheduled Batch Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up automated batch processing:

**Using cron (Linux/macOS):**

.. code-block:: bash

   # Add to crontab
   0 2 * * * /usr/bin/python /path/to/repo_seo.py username --config batch_config.yaml

**Using Task Scheduler (Windows):**

Create a scheduled task to run the batch process.

**Using GitHub Actions:**

.. code-block:: yaml

   name: Weekly SEO Optimization
   on:
     schedule:
       - cron: '0 2 * * 0'  # Every Sunday at 2 AM
   
   jobs:
     optimize:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.9'
         - name: Install dependencies
           run: pip install -r requirements.txt
         - name: Run batch optimization
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
           run: |
             python repo_seo.py ${{ github.repository_owner }} \
               --config .github/batch_config.yaml

Best Practices
--------------

1. **Start Small**: Test with a few repositories before processing all
2. **Use Dry Run**: Always preview changes with ``--dry-run`` first
3. **Monitor Progress**: Use progress tracking for large batches
4. **Handle Errors**: Implement proper error handling and logging
5. **Respect Rate Limits**: Use delays and rate limit handling
6. **Cache Results**: Enable caching to reduce API calls
7. **Regular Updates**: Schedule regular batch updates
8. **Backup First**: Consider backing up repository metadata

Example Workflows
-----------------

Initial Organization Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Analyze current state
   python repo_seo.py --org my-org --dry-run --output initial_analysis.json

   # 2. Process high-priority repositories
   python repo_seo.py --org my-org --filter important --provider openai

   # 3. Process remaining repositories
   python repo_seo.py --org my-org --filter needs-optimization --provider local

Monthly Maintenance
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Process new repositories
   python repo_seo.py username --filter created-this-month

   # 2. Update recently modified repositories
   python repo_seo.py username --filter updated-this-month

   # 3. Review and update popular repositories
   python repo_seo.py username --filter high-stars --provider openai

Next Steps
----------

* Learn about :doc:`/api/modules` for programmatic batch processing
* Explore :doc:`llm_providers` for provider-specific batch features
* Read about :doc:`/development/architecture` for custom batch strategies 