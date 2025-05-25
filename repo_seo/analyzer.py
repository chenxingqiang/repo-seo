"""
Repository analyzer module for repo-seo tool.
Enhanced with AI-powered analysis capabilities.
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from collections import Counter

# Import new analyzer framework
try:
    from src.utils.analyzers import AnalyzerFactory
    ANALYZER_FRAMEWORK_AVAILABLE = True
except ImportError:
    ANALYZER_FRAMEWORK_AVAILABLE = False

from .ai_client import AIClient


class RepoAnalyzer:
    """Analyzes GitHub repositories for SEO optimization opportunities."""
    
    def __init__(self, repo_info: Dict, local_path: Optional[str] = None, ai_client: Optional[AIClient] = None):
        """
        Initialize the repository analyzer.
        
        Args:
            repo_info: Dictionary containing repository metadata
            local_path: Path to local repository clone (optional)
            ai_client: AI client for enhanced analysis (optional)
        """
        self.repo_info = repo_info
        self.local_path = local_path
        self.ai_client = ai_client
        
        # Create analyzer components using factory if available
        if ANALYZER_FRAMEWORK_AVAILABLE:
            analyzer_type = "ai" if ai_client else "rule"
            self.readme_analyzer = AnalyzerFactory.create_readme_analyzer(analyzer_type)
            self.topic_extractor = AnalyzerFactory.create_topic_extractor(analyzer_type)
            self.repo_analyzer = AnalyzerFactory.create_repository_analyzer(analyzer_type)
        else:
            self.readme_analyzer = None
            self.topic_extractor = None
            self.repo_analyzer = None
    
    def analyze(self, deep: bool = False) -> Dict:
        """
        Perform comprehensive SEO analysis on the repository.
        
        Args:
            deep: Whether to perform deep analysis using AI
            
        Returns:
            Dictionary containing analysis results
        """
        # Use the new repository analyzer if available
        if ANALYZER_FRAMEWORK_AVAILABLE and self.repo_analyzer:
            # Extract needed information from repo_info
            return self.repo_analyzer.analyze(
                repo_name=self.repo_info.get("name", ""),
                description=self.repo_info.get("description", ""),
                languages=self.repo_info.get("languages", []),
                topics=self.repo_info.get("topics", []),
                readme=self.repo_info.get("readme", "")
            )
        
        # Fallback to the original implementation
        results = {
            "metadata": self.analyze_metadata(),
            "readme": self.analyze_readme(),
            "keywords": self.extract_keywords(),
            "topics": self.analyze_topics(),
            "description": self.analyze_description(),
            "code_quality": self.analyze_code_quality() if self.local_path else None,
            "score": 0  # Will be calculated based on all factors
        }
        
        # Deep analysis with AI if requested
        if deep and self.ai_client:
            ai_results = self.perform_ai_analysis()
            # Merge AI results with base results
            for key, value in ai_results.items():
                if key in results and isinstance(results[key], dict) and isinstance(value, dict):
                    results[key].update(value)
                else:
                    results[key] = value
        
        # Calculate final score
        results["score"] = self.calculate_score(results)
        
        return results
    
    def analyze_metadata(self) -> Dict:
        """
        Analyze repository metadata.
        
        Returns:
            Dictionary containing metadata analysis results
        """
        # Extract essential metadata
        name = self.repo_info.get("name", "")
        owner = self.repo_info.get("owner", {}).get("login", "")
        created_at = self.repo_info.get("created_at", "")
        updated_at = self.repo_info.get("updated_at", "")
        languages = self.repo_info.get("languages", [])
        stars = self.repo_info.get("stargazers_count", 0)
        forks = self.repo_info.get("forks_count", 0)
        
        # Analyze completeness
        issues = []
        if not languages:
            issues.append("No programming languages detected")
        
        return {
            "name": name,
            "owner": owner,
            "created_at": created_at,
            "updated_at": updated_at,
            "languages": languages,
            "stars": stars,
            "forks": forks,
            "issues": issues,
            "completeness": 100 - (len(issues) * 25)
        }
    
    def analyze_readme(self) -> Dict:
        """
        Analyze repository README.
        
        Returns:
            Dictionary containing README analysis results
        """
        # Use the new readme analyzer if available
        if ANALYZER_FRAMEWORK_AVAILABLE and self.readme_analyzer:
            return self.readme_analyzer.analyze(self.repo_info.get("readme", ""))
        
        # Fallback to the original implementation
        readme = self.repo_info.get("readme", "")
        if not readme:
            return {
                "exists": False,
                "length": 0,
                "sections": [],
                "issues": ["README file is missing"],
                "suggestions": ["Create a README file with essential project information"],
                "score": 0
            }
        
        # Basic analysis
        lines = readme.split("\n")
        word_count = len(re.findall(r'\w+', readme))
        
        # Identify sections
        sections = []
        section_pattern = re.compile(r'^(#+)\s+(.+)$', re.MULTILINE)
        for match in section_pattern.finditer(readme):
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()
            sections.append({
                "level": heading_level,
                "text": heading_text
            })
        
        # Check for essential sections
        essential_sections = ["installation", "usage", "features", "contributing", "license"]
        section_names = [s["text"].lower() for s in sections]
        missing_sections = [s for s in essential_sections if not any(s in sn for sn in section_names)]
        
        # Identify issues
        issues = []
        if len(lines) < 10:
            issues.append("README is too short")
        if not sections:
            issues.append("README has no sections")
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
        
        # Generate suggestions
        suggestions = []
        if len(lines) < 10:
            suggestions.append("Expand your README with more detailed information")
        if not sections:
            suggestions.append("Add sections to your README using headings (## Heading)")
        for section in missing_sections:
            suggestions.append(f"Add a {section} section")
        
        # Calculate score
        score = 100
        score -= len(issues) * 20
        score = max(0, min(100, score))
        
        return {
            "exists": True,
            "length": len(lines),
            "word_count": word_count,
            "sections": [s["text"] for s in sections],
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def extract_keywords(self) -> Dict:
        """
        Extract keywords from repository content.
        
        Returns:
            Dictionary containing extracted keywords
        """
        # Use the new topic extractor if available
        if ANALYZER_FRAMEWORK_AVAILABLE and self.topic_extractor:
            readme = self.repo_info.get("readme", "")
            description = self.repo_info.get("description", "")
            content = f"{description}\n\n{readme}" if description else readme
            
            keywords = self.topic_extractor.extract(content)
            return {
                "from_readme": keywords,
                "score": 100 if keywords else 0
            }
        
        # Fallback to original implementation
        readme = self.repo_info.get("readme", "")
        description = self.repo_info.get("description", "")
        
        if not readme and not description:
            return {
                "from_readme": [],
                "from_description": [],
                "score": 0
            }
        
        # Extract keywords from README
        readme_keywords = []
        if readme:
            # Extract from headings
            headings = re.findall(r'^#+\s+(.+)$', readme, re.MULTILINE)
            for heading in headings:
                words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', heading.lower())
                for word in words:
                    if len(word) > 3 and word not in ["this", "that", "with", "from"]:
                        readme_keywords.append(word)
            
            # Extract from content
            content_words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', readme.lower())
            word_counts = Counter(content_words)
            for word, count in word_counts.most_common(20):
                if len(word) > 3 and word not in ["this", "that", "with", "from"]:
                    if word not in readme_keywords:
                        readme_keywords.append(word)
        
        # Extract keywords from description
        desc_keywords = []
        if description:
            words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', description.lower())
            for word in words:
                if len(word) > 3 and word not in ["this", "that", "with", "from"]:
                    desc_keywords.append(word)
        
        # Score based on keyword presence
        score = 100 if readme_keywords or desc_keywords else 0
        
        return {
            "from_readme": readme_keywords[:10],
            "from_description": desc_keywords[:5],
            "score": score
        }
    
    def analyze_topics(self) -> Dict:
        """
        Analyze repository topics.
        
        Returns:
            Dictionary containing topics analysis results
        """
        topics = self.repo_info.get("topics", [])
        
        issues = []
        suggestions = []
        
        if not topics:
            issues.append("No topics defined")
            suggestions.append("Add relevant topics to improve discoverability")
        elif len(topics) < 5:
            issues.append("Few topics defined (recommended: 5+)")
            suggestions.append("Add more relevant topics to improve discoverability")
        
        # Calculate score
        score = 100
        if not topics:
            score = 0
        elif len(topics) < 5:
            score = 60
        
        return {
            "current": topics,
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def analyze_description(self) -> Dict:
        """
        Analyze repository description.
        
        Returns:
            Dictionary containing description analysis results
        """
        description = self.repo_info.get("description", "")
        
        issues = []
        suggestions = []
        
        if not description:
            issues.append("Repository description is missing")
            suggestions.append("Add a concise description explaining the purpose of your project")
        elif len(description) < 20:
            issues.append("Repository description is too short")
            suggestions.append("Expand your description to better explain your project")
        elif len(description) > 250:
            issues.append("Repository description is too long")
            suggestions.append("Shorten your description to be more concise (< 250 chars)")
        
        # Calculate score
        score = 100
        if not description:
            score = 0
        elif len(description) < 20:
            score = 40
        elif len(description) > 250:
            score = 70
        
        return {
            "content": description,
            "length": len(description) if description else 0,
            "issues": issues,
            "suggestions": suggestions,
            "score": score
        }
    
    def analyze_code_quality(self) -> Dict:
        """
        Analyze code quality metrics.
        
        Returns:
            Dictionary containing code quality analysis results
        """
        if not self.local_path or not os.path.exists(self.local_path):
            return {
                "issues": ["Local repository path not available"],
                "score": 0
            }
        
        issues = []
        metrics = {
            "lines_of_code": 0,
            "files_analyzed": 0,
            "directories": 0
        }
        
        # Basic code metrics
        for root, dirs, files in os.walk(self.local_path):
            # Skip hidden directories and .git
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            metrics["directories"] += 1
            
            for file in files:
                # Skip hidden files, binaries, etc.
                if file.startswith('.') or os.path.splitext(file)[1] in ['.jpg', '.png', '.gif', '.pdf']:
                    continue
                
                metrics["files_analyzed"] += 1
                
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        metrics["lines_of_code"] += len(lines)
                except Exception:
                    pass
        
        # Calculate score based on project size
        score = 100
        if metrics["files_analyzed"] == 0:
            issues.append("No source files found")
            score = 0
        elif metrics["lines_of_code"] < 100:
            issues.append("Limited code content")
            score = 60
        
        return {
            "metrics": metrics,
            "issues": issues,
            "score": score
        }
    
    def perform_ai_analysis(self) -> Dict:
        """
        Perform AI-enhanced analysis using the AI client.
        
        Returns:
            Dictionary containing AI analysis results
        """
        if not self.ai_client:
            return {}
        
        try:
            return self.ai_client.analyze_repository(self.repo_info)
        except Exception as e:
            return {
                "ai_error": str(e),
                "ai_analysis": {
                    "status": "failed",
                    "message": "AI analysis failed, falling back to basic analysis"
                }
            }
    
    def calculate_score(self, results: Dict) -> int:
        """
        Calculate overall repository score.
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Score between 0-100
        """
        scores = []
        
        # Readme score
        if "readme" in results and isinstance(results["readme"], dict):
            scores.append(results["readme"].get("score", 0))
        
        # Description score
        if "description" in results and isinstance(results["description"], dict):
            scores.append(results["description"].get("score", 0))
        
        # Topics score
        if "topics" in results and isinstance(results["topics"], dict):
            scores.append(results["topics"].get("score", 0))
        
        # Code quality score (if available)
        if "code_quality" in results and isinstance(results["code_quality"], dict):
            scores.append(results["code_quality"].get("score", 0))
        
        # Calculate average
        if scores:
            return round(sum(scores) / len(scores))
        return 0 