#!/usr/bin/env python3
"""
Core analyzer module for the GitHub Repository SEO Optimizer.

This module provides the base interfaces and abstract classes for all analyzers,
implementing a common architecture to eliminate code duplication.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """Base interface for all analyzers."""
    
    @abstractmethod
    def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """Generic analyze method to be implemented by subclasses."""
        pass


class BaseReadmeAnalyzer(BaseAnalyzer):
    """Interface for README analysis."""
    
    @abstractmethod
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze README content.
        
        Args:
            content: README content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        pass


class BaseTopicExtractor(BaseAnalyzer):
    """Interface for topic extraction."""
    
    @abstractmethod
    def extract(self, content: str) -> List[str]:
        """
        Extract topics from content.
        
        Args:
            content: Text content to extract topics from
            
        Returns:
            List of extracted topics
        """
        pass


class BaseRepositoryAnalyzer(BaseAnalyzer):
    """Interface for repository analysis."""
    
    @abstractmethod
    def analyze(self, repo_name: str, description: str, 
                languages: List[str], topics: List[str], 
                readme: str) -> Dict[str, Any]:
        """
        Analyze a repository.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            languages: List of programming languages
            topics: List of repository topics
            readme: README content
            
        Returns:
            Dictionary with analysis results
        """
        pass


class AnalyzerFactory:
    """Factory for creating appropriate analyzers."""
    
    @staticmethod
    def create_readme_analyzer(analyzer_type: str = "rule", **kwargs) -> BaseReadmeAnalyzer:
        """
        Create a README analyzer.
        
        Args:
            analyzer_type: Type of analyzer ("rule", "nlp", "ai")
            **kwargs: Additional arguments for specific analyzer types
            
        Returns:
            README analyzer instance
        """
        # Implementations will be registered during runtime
        from .analyzers_impl import RuleBasedReadmeAnalyzer, NLPReadmeAnalyzer, AIReadmeAnalyzer
        
        if analyzer_type == "nlp":
            return NLPReadmeAnalyzer(**kwargs)
        elif analyzer_type == "ai":
            return AIReadmeAnalyzer(**kwargs)
        else:
            return RuleBasedReadmeAnalyzer(**kwargs)
    
    @staticmethod
    def create_topic_extractor(extractor_type: str = "rule", **kwargs) -> BaseTopicExtractor:
        """
        Create a topic extractor.
        
        Args:
            extractor_type: Type of extractor ("rule", "nlp", "ai")
            **kwargs: Additional arguments for specific extractor types
            
        Returns:
            Topic extractor instance
        """
        # Implementations will be registered during runtime
        from .analyzers_impl import RuleBasedTopicExtractor, NLPTopicExtractor, AITopicExtractor
        
        if extractor_type == "nlp":
            return NLPTopicExtractor(**kwargs)
        elif extractor_type == "ai":
            return AITopicExtractor(**kwargs)
        else:
            return RuleBasedTopicExtractor(**kwargs)
    
    @staticmethod
    def create_repository_analyzer(analyzer_type: str = "rule", **kwargs) -> BaseRepositoryAnalyzer:
        """
        Create a repository analyzer.
        
        Args:
            analyzer_type: Type of analyzer ("rule", "nlp", "ai")
            **kwargs: Additional arguments for specific analyzer types
            
        Returns:
            Repository analyzer instance
        """
        # Implementations will be registered during runtime
        from .analyzers_impl import RuleBasedRepositoryAnalyzer, NLPRepositoryAnalyzer, AIRepositoryAnalyzer
        
        if analyzer_type == "nlp":
            return NLPRepositoryAnalyzer(**kwargs)
        elif analyzer_type == "ai":
            return AIRepositoryAnalyzer(**kwargs)
        else:
            return RuleBasedRepositoryAnalyzer(**kwargs) 