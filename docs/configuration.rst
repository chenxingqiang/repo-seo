Configuration Guide
===================

This guide covers all configuration options for the GitHub Repository SEO Optimizer.

Environment Variables
---------------------

The tool uses environment variables for sensitive configuration like API keys.

Required Variables
~~~~~~~~~~~~~~~~~~

**GitHub Authentication:**

.. code-block:: bash

   # GitHub CLI must be authenticated
   gh auth login

Optional Variables
~~~~~~~~~~~~~~~~~~

**LLM Provider API Keys:**

.. code-block:: bash

   # OpenAI
   export OPENAI_API_KEY="sk-..."
   
   # Anthropic
   export ANTHROPIC_API_KEY="sk-ant-..."
   
   # Google Gemini
   export GEMINI_API_KEY="..."
   
   # DeepSeek
   export DEEPSEEK_API_KEY="..."
   
   # ZhiPu AI
   export ZHIPU_API_KEY="..."
   
   # QianWen (Alibaba)
   export QIANWEN_API_KEY="..."

Configuration Files
-------------------

.env File
~~~~~~~~~

Create a ``.env`` file in your project root for easier management:

.. code-block:: ini

   # GitHub Repository SEO Optimizer Configuration
   
   # LLM Provider Settings
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4
   OPENAI_TEMPERATURE=0.7
   
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_MODEL=claude-3-sonnet-20240229
   
   GEMINI_API_KEY=...
   DEEPSEEK_API_KEY=...
   ZHIPU_API_KEY=...
   QIANWEN_API_KEY=...
   
   # Ollama Settings (if using local models)
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=llama3
   
   # Processing Settings
   DEFAULT_PROVIDER=local
   BATCH_SIZE=10
   RATE_LIMIT_DELAY=1
   
   # Output Settings
   OUTPUT_FORMAT=json
   LOG_LEVEL=INFO

Loading Configuration
~~~~~~~~~~~~~~~~~~~~~

Use python-dotenv to load the configuration:

.. code-block:: python

   from dotenv import load_dotenv
   import os
   
   # Load .env file
   load_dotenv()
   
   # Access configuration
   api_key = os.getenv("OPENAI_API_KEY")
   default_provider = os.getenv("DEFAULT_PROVIDER", "local")

Command Line Options
--------------------

The tool supports various command-line options that override default settings:

Basic Options
~~~~~~~~~~~~~

.. code-block:: bash

   # Specify username (required)
   python repo_seo.py USERNAME
   
   # Target specific repository
   python repo_seo.py USERNAME --repo REPO_NAME
   
   # Dry run mode (preview changes)
   python repo_seo.py USERNAME --dry-run
   
   # Specify LLM provider
   python repo_seo.py USERNAME --provider openai

Processing Options
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Limit number of repositories
   python repo_seo.py USERNAME --limit 10
   
   # Skip private repositories
   python repo_seo.py USERNAME --skip-private
   
   # Custom output file
   python repo_seo.py USERNAME --output results.json
   
   # Verbose output
   python repo_seo.py USERNAME --verbose

Advanced Options
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Custom configuration file
   python repo_seo.py USERNAME --config custom_config.ini
   
   # Override API endpoint
   python repo_seo.py USERNAME --api-endpoint https://api.github.com
   
   # Set processing timeout
   python repo_seo.py USERNAME --timeout 300

Provider-Specific Configuration
-------------------------------

Each LLM provider can be configured with specific settings:

OpenAI Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   provider = get_provider("openai",
       model="gpt-4",              # or "gpt-3.5-turbo"
       temperature=0.7,            # 0.0 to 1.0
       max_tokens=1000,            # Maximum response length
       top_p=1.0,                  # Nucleus sampling
       frequency_penalty=0.0,      # Reduce repetition
       presence_penalty=0.0        # Encourage new topics
   )

Anthropic Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   provider = get_provider("anthropic",
       model="claude-3-sonnet-20240229",
       max_tokens=1000,
       temperature=0.7,
       top_p=1.0,
       top_k=40                    # Top-k sampling
   )

Ollama Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   provider = get_provider("ollama",
       model="llama3",             # Model name
       host="http://localhost:11434",  # Ollama server
       timeout=120,                # Request timeout
       num_predict=1000,           # Max tokens
       temperature=0.7
   )

Logging Configuration
---------------------

Configure logging for debugging and monitoring:

Basic Logging
~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   # Set log level
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

Advanced Logging
~~~~~~~~~~~~~~~~

Create a ``logging.conf`` file:

.. code-block:: ini

   [loggers]
   keys=root,repo_seo
   
   [handlers]
   keys=console,file
   
   [formatters]
   keys=detailed
   
   [logger_root]
   level=WARNING
   handlers=console
   
   [logger_repo_seo]
   level=DEBUG
   handlers=console,file
   qualname=repo_seo
   propagate=0
   
   [handler_console]
   class=StreamHandler
   level=INFO
   formatter=detailed
   args=(sys.stdout,)
   
   [handler_file]
   class=FileHandler
   level=DEBUG
   formatter=detailed
   args=('repo_seo.log', 'a')
   
   [formatter_detailed]
   format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
   datefmt=%Y-%m-%d %H:%M:%S

Load the configuration:

.. code-block:: python

   import logging.config
   
   logging.config.fileConfig('logging.conf')
   logger = logging.getLogger('repo_seo')

Performance Tuning
------------------

Optimize performance for large-scale operations:

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Process repositories in batches
   BATCH_SIZE = 10
   RATE_LIMIT_DELAY = 1  # seconds between batches
   
   for i in range(0, len(repos), BATCH_SIZE):
       batch = repos[i:i + BATCH_SIZE]
       process_batch(batch)
       time.sleep(RATE_LIMIT_DELAY)

Caching
~~~~~~~

Enable caching to avoid redundant API calls:

.. code-block:: python

   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_cached_description(repo_name, provider):
       return provider.generate_description(...)

Parallel Processing
~~~~~~~~~~~~~~~~~~~

Use multiprocessing for faster processing:

.. code-block:: python

   from multiprocessing import Pool
   
   def process_repo(repo):
       # Process single repository
       pass
   
   with Pool(processes=4) as pool:
       results = pool.map(process_repo, repositories)

Security Best Practices
-----------------------

1. **Never commit API keys**: Use environment variables or .env files
2. **Use GitHub tokens with minimal permissions**: Only grant necessary scopes
3. **Rotate API keys regularly**: Update keys periodically
4. **Monitor API usage**: Track usage to detect anomalies
5. **Use secure connections**: Always use HTTPS for API calls

Example: Secure Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from cryptography.fernet import Fernet
   
   # Encrypt sensitive data
   def encrypt_api_key(api_key):
       key = Fernet.generate_key()
       f = Fernet(key)
       encrypted = f.encrypt(api_key.encode())
       return key, encrypted
   
   # Store encrypted keys
   key, encrypted_api_key = encrypt_api_key(os.getenv("OPENAI_API_KEY"))
   
   # Decrypt when needed
   f = Fernet(key)
   api_key = f.decrypt(encrypted_api_key).decode()

Configuration Templates
-----------------------

Development Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   # .env.development
   DEFAULT_PROVIDER=local
   LOG_LEVEL=DEBUG
   DRY_RUN=true
   OUTPUT_FORMAT=pretty

Production Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   # .env.production
   DEFAULT_PROVIDER=openai
   LOG_LEVEL=WARNING
   DRY_RUN=false
   OUTPUT_FORMAT=json
   RATE_LIMIT_DELAY=2
   ERROR_RETRY_COUNT=3

Testing Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   # .env.test
   DEFAULT_PROVIDER=mock
   LOG_LEVEL=DEBUG
   TEST_MODE=true
   MOCK_API_RESPONSES=true 