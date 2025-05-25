#!/usr/bin/env python3
"""
Analyzer implementations for the GitHub Repository SEO Optimizer.

This module provides concrete implementations of the analyzer interfaces
defined in the analyzers.py module.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

from .analyzers import (
    BaseReadmeAnalyzer, BaseTopicExtractor, BaseRepositoryAnalyzer
)

# Configure logging
logger = logging.getLogger(__name__)

# Optional dependencies
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


# README Analyzer Implementations

class RuleBasedReadmeAnalyzer(BaseReadmeAnalyzer):
    """Rule-based implementation of README analysis."""
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze README content using rule-based approaches.
        
        Args:
            content: README content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not content:
            return {
                "summary": "",
                "topics": [],
                "issues": ["README file is missing or empty"],
                "suggestions": ["Create a README file with essential project information"],
                "score": 0
            }
        
        issues = []
        suggestions = []
        
        # Check README length
        if len(content) < 500:
            issues.append("README is too short (< 500 chars)")
            suggestions.append("Expand your README with more detailed information")
            
        # Check headings
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        if not headings:
            issues.append("No headings found in README")
            suggestions.append("Add headings (## Heading) to structure your README")
        
        # Check for common sections
        common_sections = ["installation", "usage", "features", "contributing", "license"]
        found_sections = [h[1].lower() for h in headings]
        missing_sections = [s for s in common_sections if not any(s in f for f in found_sections)]
        if missing_sections:
            issues.append(f"Missing common sections: {', '.join(missing_sections)}")
            suggestions.append(f"Add sections for: {', '.join(missing_sections)}")
        
        # Extract summary (first paragraph)
        paragraphs = re.split(r'\n\s*\n', content)
        summary = paragraphs[0] if paragraphs else ""
        
        # Calculate score
        score = 100 - (len(issues) * 10)
        score = max(0, min(100, score))
        
        return {
            "summary": summary,
            "topics": self._extract_topics(content),
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from README content using rule-based approaches."""
        # Extract words from headings
        topics = []
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        for _, heading in headings:
            words = re.findall(r'[a-zA-Z0-9]+', heading.lower())
            for word in words:
                if len(word) > 3 and word not in ["this", "that", "with", "from", "then", "than"]:
                    topics.append(word)
        
        # Count word frequency
        word_counter = Counter(topics)
        return [word for word, _ in word_counter.most_common(10)]


class NLPReadmeAnalyzer(BaseReadmeAnalyzer):
    """NLP-based implementation of README analysis."""
    
    def __init__(self):
        """Initialize the NLP README analyzer."""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available, falling back to rule-based analysis")
            self.fallback = RuleBasedReadmeAnalyzer()
        else:
            self.nlp = spacy.load("en_core_web_sm")
            self.fallback = None
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze README content using NLP techniques.
        
        Args:
            content: README content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if self.fallback:
            return self.fallback.analyze(content)
        
        if not content:
            return {
                "summary": "",
                "topics": [],
                "entities": [],
                "issues": ["README file is missing or empty"],
                "suggestions": ["Create a README file with essential project information"],
                "score": 0
            }
        
        # Process content with spaCy
        doc = self.nlp(content[:10000])  # Limit content length for processing
        
        # Extract main sentences for summary
        sentences = [sent.text.strip() for sent in doc.sents]
        summary = " ".join(sentences[:3]) if sentences else ""
        
        # Extract named entities
        entities = []
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON", "WORK_OF_ART"]:
                entities.append({"text": ent.text, "type": ent.label_})
        
        # Check for issues
        issues = []
        suggestions = []
        
        if len(content) < 500:
            issues.append("README is too short (< 500 chars)")
            suggestions.append("Expand your README with more detailed information")
        
        # Check readability
        word_count = len([token.text for token in doc if not token.is_punct and not token.is_space])
        sentence_count = len(sentences)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        if avg_sentence_length > 25:
            issues.append("Sentences are too long (avg > 25 words)")
            suggestions.append("Simplify sentences for better readability")
        
        # Calculate score
        score = 100 - (len(issues) * 10)
        score = max(0, min(100, score))
        
        # Extract topics
        if KEYBERT_AVAILABLE:
            keyword_model = KeyBERT()
            keywords = keyword_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                use_maxsum=True,
                nr_candidates=20,
                top_n=10
            )
            topics = [keyword[0] for keyword in keywords]
        else:
            topics = self._extract_topics_fallback(content)
        
        return {
            "summary": summary,
            "topics": topics,
            "entities": entities,
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def _extract_topics_fallback(self, content: str) -> List[str]:
        """Extract topics using a fallback method when KeyBERT is not available."""
        rule_analyzer = RuleBasedReadmeAnalyzer()
        return rule_analyzer._extract_topics(content)


class AIReadmeAnalyzer(BaseReadmeAnalyzer):
    """AI-based implementation of README analysis."""
    
    def __init__(self, provider_name: str = "local", **provider_kwargs):
        """
        Initialize the AI README analyzer.
        
        Args:
            provider_name: LLM provider name
            **provider_kwargs: Additional arguments for the LLM provider
        """
        try:
            from ..llm_providers import get_provider
            self.provider = get_provider(provider_name, **provider_kwargs)
            self.fallback = None
        except (ImportError, ValueError):
            logger.warning("LLM provider not available, falling back to NLP analysis")
            self.fallback = NLPReadmeAnalyzer()
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze README content using AI techniques.
        
        Args:
            content: README content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if self.fallback:
            return self.fallback.analyze(content)
        
        try:
            return self.provider.analyze_readme(content)
        except Exception as e:
            logger.error(f"Error using LLM provider for README analysis: {e}")
            return NLPReadmeAnalyzer().analyze(content)


# Topic Extractor Implementations

class RuleBasedTopicExtractor(BaseTopicExtractor):
    """Rule-based implementation of topic extraction."""
    
    def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        实现抽象方法。调用 extract 方法，并将结果转换为标准格式。
        
        Returns:
            字典，包含提取的主题
        """
        content = kwargs.get("content", "")
        if not content and args:
            content = args[0]
        
        topics = self.extract(content)
        return {
            "topics": topics,
            "count": len(topics),
            "score": 100 if topics else 0
        }
    
    def extract(self, content: str) -> List[str]:
        """
        Extract topics from content using rule-based approaches.
        
        Args:
            content: Content to extract topics from
            
        Returns:
            List of extracted topics
        """
        if not content:
            return []
        
        # Extract words from headings
        topics = []
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        for _, heading in headings:
            words = re.findall(r'[a-zA-Z0-9]+', heading.lower())
            for word in words:
                if len(word) > 3 and word not in ["this", "that", "with", "from", "then", "than"]:
                    topics.append(word)
        
        # Extract words from first paragraph
        paragraphs = re.split(r'\n\s*\n', content)
        if paragraphs:
            first_para = paragraphs[0]
            words = re.findall(r'[a-zA-Z0-9]+', first_para.lower())
            for word in words:
                if len(word) > 3 and word not in ["this", "that", "with", "from", "then", "than"]:
                    topics.append(word)
        
        # Count word frequency
        word_counter = Counter(topics)
        return [word for word, _ in word_counter.most_common(10)]


class NLPTopicExtractor(BaseTopicExtractor):
    """NLP-based implementation of topic extraction."""
    
    def __init__(self):
        """Initialize the NLP topic extractor."""
        if not KEYBERT_AVAILABLE:
            logger.warning("KeyBERT not available, falling back to rule-based extraction")
            self.fallback = RuleBasedTopicExtractor()
        else:
            self.keyword_model = KeyBERT()
            self.fallback = None
    
    def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        实现抽象方法。调用 extract 方法，并将结果转换为标准格式。
        
        Returns:
            字典，包含提取的主题
        """
        content = kwargs.get("content", "")
        if not content and args:
            content = args[0]
        
        topics = self.extract(content)
        return {
            "topics": topics,
            "count": len(topics),
            "score": 100 if topics else 0
        }
    
    def extract(self, content: str) -> List[str]:
        """
        Extract topics from content using NLP techniques.
        
        Args:
            content: Content to extract topics from
            
        Returns:
            List of extracted topics
        """
        if self.fallback:
            return self.fallback.extract(content)
        
        if not content:
            return []
        
        try:
            keywords = self.keyword_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                use_maxsum=True,
                nr_candidates=20,
                top_n=10
            )
            return [keyword[0] for keyword in keywords]
        except Exception as e:
            logger.error(f"Error using KeyBERT for topic extraction: {e}")
            return RuleBasedTopicExtractor().extract(content)


class AITopicExtractor(BaseTopicExtractor):
    """AI-based implementation of topic extraction."""
    
    def __init__(self, provider_name: str = "local", **provider_kwargs):
        """
        Initialize the AI topic extractor.
        
        Args:
            provider_name: LLM provider name
            **provider_kwargs: Additional arguments for the LLM provider
        """
        try:
            from ..llm_providers import get_provider
            self.provider = get_provider(provider_name, **provider_kwargs)
            self.fallback = None
        except (ImportError, ValueError):
            logger.warning("LLM provider not available, falling back to NLP extraction")
            self.fallback = NLPTopicExtractor()
    
    def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        实现抽象方法。调用 extract 方法，并将结果转换为标准格式。
        
        Returns:
            字典，包含提取的主题
        """
        content = kwargs.get("content", "")
        if not content and args:
            content = args[0]
        
        topics = self.extract(content)
        return {
            "topics": topics,
            "count": len(topics),
            "score": 100 if topics else 0
        }
    
    def extract(self, content: str) -> List[str]:
        """
        Extract topics from content using AI techniques.
        
        Args:
            content: Content to extract topics from
            
        Returns:
            List of extracted topics
        """
        if self.fallback:
            return self.fallback.extract(content)
        
        try:
            return self.provider.generate_topics(
                repo_name="",  # Not needed for direct content analysis
                languages=[],  # Not needed for direct content analysis
                current_topics=[],  # Not needed for direct content analysis
                readme=content
            )
        except Exception as e:
            logger.error(f"Error using LLM provider for topic extraction: {e}")
            return NLPTopicExtractor().extract(content)


# Repository Analyzer Implementations

class RuleBasedRepositoryAnalyzer(BaseRepositoryAnalyzer):
    """Rule-based implementation of repository analysis."""
    
    def __init__(self):
        """Initialize the rule-based repository analyzer."""
        self.readme_analyzer = RuleBasedReadmeAnalyzer()
        self.topic_extractor = RuleBasedTopicExtractor()
    
    def analyze(self, repo_name: str, description: str, 
                languages: List[str], topics: List[str], 
                readme: str) -> Dict[str, Any]:
        """
        Analyze a repository using rule-based approaches.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            languages: List of programming languages
            topics: List of repository topics
            readme: README content
            
        Returns:
            Dictionary with analysis results
        """
        results = {}
        
        # Analyze README
        readme_analysis = self.readme_analyzer.analyze(readme)
        results["readme"] = readme_analysis
        
        # Analyze description
        description_issues = []
        description_suggestions = []
        
        if not description:
            description_issues.append("Repository description is missing")
            description_suggestions.append("Add a concise description explaining the purpose of your project")
        elif len(description) < 20:
            description_issues.append("Repository description is too short")
            description_suggestions.append("Expand your description to better explain your project")
        elif len(description) > 250:
            description_issues.append("Repository description is too long")
            description_suggestions.append("Shorten your description to be more concise (< 250 chars)")
        
        results["description"] = {
            "content": description,
            "issues": description_issues,
            "suggestions": description_suggestions,
            "score": 100 - (len(description_issues) * 25)
        }
        
        # Analyze topics
        topic_issues = []
        topic_suggestions = []
        
        if not topics:
            topic_issues.append("No topics defined for the repository")
            topic_suggestions.append("Add relevant topics to improve discoverability")
        elif len(topics) < 5:
            topic_issues.append("Too few topics defined (< 5)")
            topic_suggestions.append("Add more relevant topics to improve discoverability")
        
        # Suggest additional topics
        extracted_topics = self.topic_extractor.extract(readme)
        suggested_topics = [t for t in extracted_topics if t not in topics]
        
        results["topics"] = {
            "current": topics,
            "suggested": suggested_topics[:5],
            "issues": topic_issues,
            "suggestions": topic_suggestions,
            "score": 100 - (len(topic_issues) * 25)
        }
        
        # Calculate overall score
        readme_score = readme_analysis.get("score", 0)
        description_score = results["description"].get("score", 0)
        topics_score = results["topics"].get("score", 0)
        
        results["score"] = (readme_score + description_score + topics_score) / 3
        
        return results


class NLPRepositoryAnalyzer(BaseRepositoryAnalyzer):
    """NLP-based implementation of repository analysis."""
    
    def __init__(self):
        """Initialize the NLP repository analyzer."""
        if not SPACY_AVAILABLE or not KEYBERT_AVAILABLE:
            logger.warning("Required NLP libraries not available, falling back to rule-based analysis")
            self.fallback = RuleBasedRepositoryAnalyzer()
        else:
            self.readme_analyzer = NLPReadmeAnalyzer()
            self.topic_extractor = NLPTopicExtractor()
            self.fallback = None
    
    def analyze(self, repo_name: str, description: str, 
                languages: List[str], topics: List[str], 
                readme: str) -> Dict[str, Any]:
        """
        Analyze a repository using NLP techniques.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            languages: List of programming languages
            topics: List of repository topics
            readme: README content
            
        Returns:
            Dictionary with analysis results
        """
        if self.fallback:
            return self.fallback.analyze(repo_name, description, languages, topics, readme)
        
        results = {}
        
        # Analyze README
        readme_analysis = self.readme_analyzer.analyze(readme)
        results["readme"] = readme_analysis
        
        # Analyze description (same as rule-based for now)
        description_issues = []
        description_suggestions = []
        
        if not description:
            description_issues.append("Repository description is missing")
            description_suggestions.append("Add a concise description explaining the purpose of your project")
        elif len(description) < 20:
            description_issues.append("Repository description is too short")
            description_suggestions.append("Expand your description to better explain your project")
        elif len(description) > 250:
            description_issues.append("Repository description is too long")
            description_suggestions.append("Shorten your description to be more concise (< 250 chars)")
        
        results["description"] = {
            "content": description,
            "issues": description_issues,
            "suggestions": description_suggestions,
            "score": 100 - (len(description_issues) * 25)
        }
        
        # Analyze topics
        topic_issues = []
        topic_suggestions = []
        
        if not topics:
            topic_issues.append("No topics defined for the repository")
            topic_suggestions.append("Add relevant topics to improve discoverability")
        elif len(topics) < 5:
            topic_issues.append("Too few topics defined (< 5)")
            topic_suggestions.append("Add more relevant topics to improve discoverability")
        
        # Suggest additional topics
        extracted_topics = self.topic_extractor.extract(readme)
        suggested_topics = [t for t in extracted_topics if t not in topics]
        
        results["topics"] = {
            "current": topics,
            "suggested": suggested_topics[:5],
            "issues": topic_issues,
            "suggestions": topic_suggestions,
            "score": 100 - (len(topic_issues) * 25)
        }
        
        # Calculate overall score
        readme_score = readme_analysis.get("score", 0)
        description_score = results["description"].get("score", 0)
        topics_score = results["topics"].get("score", 0)
        
        results["score"] = (readme_score + description_score + topics_score) / 3
        
        return results


class AIRepositoryAnalyzer(BaseRepositoryAnalyzer):
    """AI-based implementation of repository analysis."""
    
    def __init__(self, provider_name: str = "local", **provider_kwargs):
        """
        Initialize the AI repository analyzer.
        
        Args:
            provider_name: LLM provider name
            **provider_kwargs: Additional arguments for the LLM provider
        """
        try:
            from ..llm_providers import get_provider
            self.provider = get_provider(provider_name, **provider_kwargs)
            self.readme_analyzer = AIReadmeAnalyzer(provider_name, **provider_kwargs)
            self.fallback = None
        except (ImportError, ValueError):
            logger.warning("LLM provider not available, falling back to NLP analysis")
            self.fallback = NLPRepositoryAnalyzer()
    
    def analyze(self, repo_name: str, description: str, 
                languages: List[str], topics: List[str], 
                readme: str) -> Dict[str, Any]:
        """
        Analyze a repository using AI techniques.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            languages: List of programming languages
            topics: List of repository topics
            readme: README content
            
        Returns:
            Dictionary with analysis results
        """
        if self.fallback:
            return self.fallback.analyze(repo_name, description, languages, topics, readme)
        
        try:
            # For AI providers, we could utilize more capabilities of the LLM
            # But we'll need to implement this in a structured way within the provider interface
            
            # For now, just use the components separately
            results = {}
            
            # Analyze README
            readme_analysis = self.readme_analyzer.analyze(readme)
            results["readme"] = readme_analysis
            
            # Generate topics
            suggested_topics = self.provider.generate_topics(
                repo_name=repo_name,
                languages=languages,
                current_topics=topics,
                readme=readme
            )
            
            # Analyze description
            # This might need to be added to the BaseProvider interface
            
            # For now, use the same rule-based approach
            description_issues = []
            description_suggestions = []
            
            if not description:
                description_issues.append("Repository description is missing")
                description_suggestions.append("Add a concise description explaining the purpose of your project")
            elif len(description) < 20:
                description_issues.append("Repository description is too short")
                description_suggestions.append("Expand your description to better explain your project")
            elif len(description) > 250:
                description_issues.append("Repository description is too long")
                description_suggestions.append("Shorten your description to be more concise (< 250 chars)")
            
            results["description"] = {
                "content": description,
                "issues": description_issues,
                "suggestions": description_suggestions,
                "score": 100 - (len(description_issues) * 25)
            }
            
            # Analyze topics
            topic_issues = []
            topic_suggestions = []
            
            if not topics:
                topic_issues.append("No topics defined for the repository")
                topic_suggestions.append("Add relevant topics to improve discoverability")
            elif len(topics) < 5:
                topic_issues.append("Too few topics defined (< 5)")
                topic_suggestions.append("Add more relevant topics to improve discoverability")
            
            results["topics"] = {
                "current": topics,
                "suggested": [t for t in suggested_topics if t not in topics][:5],
                "issues": topic_issues,
                "suggestions": topic_suggestions,
                "score": 100 - (len(topic_issues) * 25)
            }
            
            # Calculate overall score
            readme_score = readme_analysis.get("score", 0)
            description_score = results["description"].get("score", 0)
            topics_score = results["topics"].get("score", 0)
            
            results["score"] = (readme_score + description_score + topics_score) / 3
            
            return results
            
        except Exception as e:
            logger.error(f"Error using LLM provider for repository analysis: {e}")
            return NLPRepositoryAnalyzer().analyze(repo_name, description, languages, topics, readme) 