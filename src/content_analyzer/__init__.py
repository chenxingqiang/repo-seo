"""
Content analyzer module for the GitHub Repository SEO Optimizer.

This module provides functionality for analyzing repository content,
including language detection, topic extraction, and README analysis.
"""

import logging
from typing import List, Dict, Tuple, Any

# Re-export functions from analyzer.py
from .analyzer import (
    extract_topics_from_readme,
    extract_topics_from_text,
    analyze_readme_content,
    generate_readme_suggestions
)

# Import factory for analyzer creation
from ..utils.analyzers import AnalyzerFactory

# Configure logging
logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Content analyzer for repository content."""
    
    def __init__(self, analyzer_type: str = "rule"):
        """
        Initialize the content analyzer.
        
        Args:
            analyzer_type: Type of analyzer to use ("rule", "nlp", "ai")
        """
        self.analyzer_type = analyzer_type
        self.readme_analyzer = AnalyzerFactory.create_readme_analyzer(analyzer_type)
        self.topic_extractor = AnalyzerFactory.create_topic_extractor(analyzer_type)
        self.repo_analyzer = AnalyzerFactory.create_repository_analyzer(analyzer_type)
    
    def analyze_readme(self, content: str) -> Tuple[str, List[str], List[str]]:
        """
        Analyze README content to extract summary, topics, and suggestions.

        Args:
            content: The README content to analyze

        Returns:
            Tuple containing (summary, topics, suggestions)
        """
        try:
            result = self.readme_analyzer.analyze(content)
            return (
                result.get("summary", ""),
                result.get("topics", []),
                result.get("suggestions", [])
            )
        except Exception as e:
            logger.error(f"Error analyzing README: {e}")
            return ("", [], [])
    
    def extract_topics(self, content: str) -> List[str]:
        """
        Extract topics from content.

        Args:
            content: The content to extract topics from

        Returns:
            List of extracted topics
        """
        try:
            return self.topic_extractor.extract(content)
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def analyze_repository(self, repo_data: Dict) -> Dict:
        """
        Analyze a repository.

        Args:
            repo_data: Dictionary containing repository data, including:
                - name: Repository name
                - description: Repository description
                - languages: List of programming languages
                - topics: List of repository topics
                - readme: README content

        Returns:
            Dictionary containing analysis results
        """
        try:
            return self.repo_analyzer.analyze(
                repo_name=repo_data.get("name", ""),
                description=repo_data.get("description", ""),
                languages=repo_data.get("languages", []),
                topics=repo_data.get("topics", []),
                readme=repo_data.get("readme", "")
            )
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return {
                "readme": {},
                "description": {},
                "topics": {},
                "score": 0
            }


# For backwards compatibility
def analyze_readme(content: str) -> Tuple[str, List[str], List[str]]:
    """Legacy function for README analysis."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_readme(content)


def extract_topics(content: str) -> List[str]:
    """Legacy function for topic extraction."""
    analyzer = ContentAnalyzer()
    return analyzer.extract_topics(content)


def analyze_repository(repo_data: Dict) -> Dict:
    """Legacy function for repository analysis."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_repository(repo_data)
