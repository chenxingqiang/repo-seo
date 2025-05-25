LLM Providers Guide
===================

This guide provides detailed information about all supported Language Model (LLM) providers in the GitHub Repository SEO Optimizer.

Overview
--------

The tool supports 8 different LLM providers, each with its own strengths:

.. list-table:: LLM Providers Comparison
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Provider
     - API Key Required
     - Cost
     - Quality
     - Speed
   * - Local
     - No
     - Free
     - Basic
     - Fast
   * - OpenAI
     - Yes
     - Paid
     - Excellent
     - Fast
   * - Anthropic
     - Yes
     - Paid
     - Excellent
     - Fast
   * - Gemini
     - Yes
     - Free tier available
     - Very Good
     - Fast
   * - Ollama
     - No
     - Free
     - Good
     - Depends on hardware
   * - DeepSeek
     - Yes
     - Paid
     - Very Good
     - Fast
   * - ZhiPu
     - Yes
     - Paid
     - Good
     - Fast
   * - QianWen
     - Yes
     - Paid
     - Good
     - Fast

Local Provider
--------------

The local provider uses rule-based algorithms and doesn't require any API keys.

**Advantages:**

* No API key required
* No cost
* Fast processing
* Privacy-focused (no data sent externally)

**Limitations:**

* Basic quality compared to AI models
* Limited understanding of context
* Rule-based generation

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider local

OpenAI Provider
---------------

Uses OpenAI's GPT models for high-quality content generation.

**Setup:**

1. Get an API key from `OpenAI Platform <https://platform.openai.com/api-keys>`_
2. Set the environment variable:

   .. code-block:: bash

      export OPENAI_API_KEY="sk-..."

**Configuration:**

.. code-block:: python

   # In your code
   provider = get_provider("openai", model="gpt-4")  # or "gpt-3.5-turbo"

**Models Available:**

* ``gpt-4``: Most capable, higher cost
* ``gpt-3.5-turbo``: Good balance of quality and cost
* ``gpt-4-turbo``: Latest model with better performance

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider openai

Anthropic Provider
------------------

Uses Anthropic's Claude models for sophisticated content generation.

**Setup:**

1. Get an API key from `Anthropic Console <https://console.anthropic.com/>`_
2. Set the environment variable:

   .. code-block:: bash

      export ANTHROPIC_API_KEY="sk-ant-..."

**Models Available:**

* ``claude-3-opus-20240229``: Most capable
* ``claude-3-sonnet-20240229``: Balanced performance
* ``claude-3-haiku-20240307``: Fastest and most affordable

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider anthropic

Google Gemini Provider
----------------------

Uses Google's Gemini models for content generation.

**Setup:**

1. Get an API key from `Google AI Studio <https://makersuite.google.com/app/apikey>`_
2. Set the environment variable:

   .. code-block:: bash

      export GEMINI_API_KEY="..."

**Models Available:**

* ``gemini-pro``: General purpose model
* ``gemini-pro-vision``: Multimodal capabilities

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider gemini

Ollama Provider
---------------

Uses locally running models through Ollama.

**Setup:**

1. Install Ollama from `ollama.ai <https://ollama.ai/>`_
2. Pull a model:

   .. code-block:: bash

      ollama pull llama3
      ollama pull mistral
      ollama pull codellama

3. Start Ollama service:

   .. code-block:: bash

      ollama serve

**Available Models:**

* ``llama3``: Meta's latest model
* ``mistral``: Fast and efficient
* ``codellama``: Optimized for code
* ``phi``: Microsoft's small model

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider ollama

DeepSeek Provider
-----------------

Uses DeepSeek's models optimized for code and technical content.

**Setup:**

1. Get an API key from `DeepSeek Platform <https://platform.deepseek.com/>`_
2. Set the environment variable:

   .. code-block:: bash

      export DEEPSEEK_API_KEY="..."

**Models Available:**

* ``deepseek-coder``: Optimized for code understanding
* ``deepseek-chat``: General purpose

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider deepseek

ZhiPu Provider
--------------

Uses ZhiPu AI's GLM models (Chinese company).

**Setup:**

1. Get an API key from `ZhiPu AI <https://open.bigmodel.cn/>`_
2. Set the environment variable:

   .. code-block:: bash

      export ZHIPU_API_KEY="..."

**Models Available:**

* ``glm-4``: Latest model
* ``glm-3-turbo``: Faster variant

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider zhipu

QianWen Provider
----------------

Uses Alibaba's QianWen (通义千问) models.

**Setup:**

1. Get an API key from `Alibaba Cloud <https://dashscope.aliyun.com/>`_
2. Set the environment variable:

   .. code-block:: bash

      export QIANWEN_API_KEY="..."

**Models Available:**

* ``qwen-turbo``: Fast model
* ``qwen-plus``: Enhanced capabilities
* ``qwen-max``: Most capable

**Usage:**

.. code-block:: bash

   python repo_seo.py username --provider qianwen

Choosing the Right Provider
---------------------------

Consider these factors when choosing a provider:

**For Best Quality:**
   Choose OpenAI (GPT-4) or Anthropic (Claude-3-Opus)

**For Cost Efficiency:**
   Use Local provider or Ollama with local models

**For Privacy:**
   Use Local provider or Ollama (data stays on your machine)

**For Speed:**
   Local provider is fastest, followed by API-based providers

**For Chinese Content:**
   Consider ZhiPu or QianWen providers

**For Code-Heavy Repositories:**
   DeepSeek or OpenAI perform well with code understanding

Provider-Specific Tips
----------------------

OpenAI Tips
~~~~~~~~~~~

* Use ``gpt-3.5-turbo`` for cost-effective processing
* Set temperature to 0.7 for balanced creativity
* Monitor token usage to control costs

Anthropic Tips
~~~~~~~~~~~~~~

* Claude excels at following complex instructions
* Good for repositories requiring nuanced descriptions
* Consider using system prompts for consistency

Ollama Tips
~~~~~~~~~~~

* Pre-download models for faster processing
* Use GPU acceleration if available
* Consider ``mistral`` for speed, ``llama3`` for quality

Error Handling
--------------

Common errors and solutions:

**API Key Errors:**

.. code-block:: text

   Error: Invalid API key

Solution: Check your environment variable is set correctly

**Rate Limiting:**

.. code-block:: text

   Error: Rate limit exceeded

Solution: Add delays between requests or upgrade your plan

**Model Not Found:**

.. code-block:: text

   Error: Model not found

Solution: Check the model name is correct for your provider

**Connection Errors:**

.. code-block:: text

   Error: Connection refused

Solution: For Ollama, ensure the service is running

Advanced Configuration
----------------------

Custom Provider Settings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.llm_providers import get_provider

   # Custom temperature
   provider = get_provider("openai", 
                          model="gpt-4",
                          temperature=0.8)

   # Custom max tokens
   provider = get_provider("anthropic",
                          model="claude-3-sonnet-20240229",
                          max_tokens=1000)

Fallback Providers
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       provider = get_provider("openai")
   except Exception:
       # Fallback to local provider
       provider = get_provider("local")

Batch Processing Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For batch processing, consider:

1. Using cheaper models for bulk operations
2. Implementing rate limiting
3. Caching results to avoid duplicate API calls
4. Using local provider for initial filtering

Performance Benchmarks
----------------------

Approximate processing times for 100 repositories:

* **Local**: 2-3 minutes
* **OpenAI GPT-3.5**: 5-10 minutes
* **OpenAI GPT-4**: 10-15 minutes
* **Anthropic Claude**: 8-12 minutes
* **Ollama (local)**: 15-30 minutes (depends on hardware)

Cost Estimates
--------------

For 100 repositories (approximate):

* **Local**: Free
* **OpenAI GPT-3.5**: $0.50 - $1.00
* **OpenAI GPT-4**: $5.00 - $10.00
* **Anthropic Claude**: $3.00 - $8.00
* **Gemini**: Free tier usually sufficient
* **Ollama**: Free (local compute) 