#!/usr/bin/env python3
"""
Content analyzer implementation for the GitHub Repository SEO Optimizer.

This module provides functionality for analyzing repository content,
including language detection, topic extraction, and README analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# Import analyzer factory
from ..utils.analyzers import AnalyzerFactory

# Configure logging
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.debug("spaCy not available, falling back to rule-based analysis")

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    logger.debug("KeyBERT not available, falling back to rule-based analysis")


class ContentAnalyzer:
    """Content analyzer for repository content."""
    
    def __init__(self, use_spacy: bool = True, use_keybert: bool = True):
        """Initialize the content analyzer.
        
        Args:
            use_spacy: Whether to use spaCy for analysis.
            use_keybert: Whether to use KeyBERT for keyword extraction.
        """
        # Determine analyzer type based on available dependencies
        if use_spacy and SPACY_AVAILABLE and use_keybert and KEYBERT_AVAILABLE:
            analyzer_type = "nlp"
        else:
            analyzer_type = "rule"
        
        # Create analyzers using the factory
        self.readme_analyzer = AnalyzerFactory.create_readme_analyzer(analyzer_type)
        self.topic_extractor = AnalyzerFactory.create_topic_extractor(analyzer_type)
        self.repo_analyzer = AnalyzerFactory.create_repository_analyzer(analyzer_type)
    
    def analyze_repository(self, repo_name: str, description: str, 
                          languages: List[str], topics: List[str], 
                          readme: str) -> Dict[str, Any]:
        """Analyze a repository.
        
        Args:
            repo_name: The name of the repository.
            description: The description of the repository.
            languages: List of programming languages used in the repository.
            topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.repo_analyzer.analyze(
            repo_name=repo_name,
            description=description,
            languages=languages,
            topics=topics,
            readme=readme
        )
    
    def analyze_readme(self, readme: str) -> Dict[str, Any]:
        """Analyze the content of a README file.
        
        Args:
            readme: The content of the repository's README file.
            
        Returns:
            Dictionary containing analysis results.
        """
        return self.readme_analyzer.analyze(readme)
    
    def extract_topics(self, content: str) -> List[str]:
        """Extract topics from content.
        
        Args:
            content: The content to extract topics from.
            
        Returns:
            List of extracted topics.
        """
        return self.topic_extractor.extract(content)


# Stand-alone functions for backwards compatibility

def extract_topics_from_readme(readme: str) -> List[str]:
    """Extract topics from README content.
    
    Args:
        readme: The README content to extract topics from.
        
    Returns:
        List of extracted topics.
    """
    extractor = AnalyzerFactory.create_topic_extractor("rule")
    return extractor.extract(readme)


def extract_topics_from_text(text: str) -> List[str]:
    """Extract topics from text content.
    
    Args:
        text: The text content to extract topics from.
        
    Returns:
        List of extracted topics.
    """
    extractor = AnalyzerFactory.create_topic_extractor("rule")
    return extractor.extract(text)


def analyze_readme_content(readme: str) -> Dict[str, Any]:
    """Analyze README content.
    
    Args:
        readme: The README content to analyze.
        
    Returns:
        Dictionary containing analysis results.
    """
    analyzer = AnalyzerFactory.create_readme_analyzer("rule")
    return analyzer.analyze(readme)


def generate_readme_suggestions(readme: str) -> List[str]:
    """Generate suggestions for improving README content.
    
    Args:
        readme: The README content to analyze.
        
    Returns:
        List of suggestions.
    """
    result = analyze_readme_content(readme)
    return result.get("suggestions", []) 