"""
GitHub Repository SEO Optimizer

A comprehensive tool to optimize GitHub repositories for better discoverability
through improved descriptions, topics, and documentation using AI/LLM providers.
"""

__version__ = "0.1.0"
__author__ = "Chen Xingqiang"
__email__ = "chenxingqiang@turingai.cc"
__license__ = "MIT"

# Core imports
from .analyzer import RepoAnalyzer
from .ai_client import AIClient

# Version info
VERSION_INFO = tuple(map(int, __version__.split('.')))

__all__ = [
    "RepoAnalyzer",
    "AIClient",
    "__version__",
    "VERSION_INFO",
] 