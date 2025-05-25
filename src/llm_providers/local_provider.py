#!/usr/bin/env python3
"""
Local provider implementation for the GitHub Repository SEO Optimizer.

This module provides a rule-based implementation of the BaseProvider interface
that doesn't require any external API keys.
"""

import re
import random
from typing import Dict, List, Any, Optional
from collections import Counter

from .base_provider import BaseProvider


class LocalProvider(BaseProvider):
    """Local provider implementation that uses rule-based approaches.
    
    This provider doesn't require any external API keys and uses simple
    rule-based approaches to generate content.
    """
    
    def __init__(self):
        """Initialize the local provider."""
        self.max_topics = 10
        self.min_description_length = 50
        self.max_description_length = 250
    
    def generate_description(self, repo_name: str, languages: List[str], 
                            topics: List[str], readme: str) -> str:
        """Generate a description for a repository using rule-based approaches.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A string containing the generated description.
        """
        # Extract the first non-empty line from the README
        first_line = ""
        if readme:
            lines = readme.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Skip empty lines and lines that are just headers
                if line and not line.startswith('#') and not line.startswith('---'):
                    first_line = line
                    break
        
        # Clean up the first line
        first_line = re.sub(r'[#*_]', '', first_line)  # Remove markdown formatting
        
        # If we have a good first line, use it as the basis for the description
        if len(first_line) >= self.min_description_length:
            description = first_line
        else:
            # Otherwise, construct a description from the repository name and languages
            repo_name_clean = repo_name.replace('-', ' ').replace('_', ' ').title()
            
            if languages:
                primary_language = languages[0]
                description = f"A {primary_language} project for {repo_name_clean}"
                
                if len(languages) > 1:
                    other_languages = ", ".join(languages[1:3])  # Limit to 2 additional languages
                    description += f" using {other_languages}"
            else:
                description = f"A project for {repo_name_clean}"
            
            # Add topics if available
            if topics:
                topic_str = ", ".join(topics[:3])  # Limit to 3 topics
                description += f" focused on {topic_str}"
        
        # Ensure the description is not too long
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length - 3] + "..."
        
        return description
    
    def generate_topics(self, repo_name: str, languages: List[str], 
                       current_topics: List[str], readme: str) -> List[str]:
        """Generate topics for a repository using rule-based approaches.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            current_topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A list of strings containing the generated topics.
        """
        topics = set(current_topics)
        
        # Add repository name components as topics
        name_parts = re.findall(r'[a-zA-Z0-9]+', repo_name.lower())
        for part in name_parts:
            if len(part) > 2 and part not in ['the', 'and', 'for', 'with']:
                topics.add(part)
        
        # Add languages as topics
        for lang in languages:
            topics.add(lang.lower())
        
        # Extract potential topics from README
        if readme:
            # Extract words from headers
            headers = re.findall(r'#+\s+(.+)', readme)
            for header in headers:
                words = re.findall(r'[a-zA-Z0-9]+', header.lower())
                for word in words:
                    if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']:
                        topics.add(word)
            
            # Extract common words from README
            words = re.findall(r'[a-zA-Z0-9]+', readme.lower())
            word_counts = Counter(words)
            common_words = [word for word, count in word_counts.most_common(20) 
                           if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']]
            
            for word in common_words[:5]:  # Limit to 5 common words
                topics.add(word)
        
        # Add some common GitHub topics based on the repository context
        common_topics = [
            "github", "repository", "project", "code", "open-source",
            "development", "programming", "software", "tool", "utility",
            "library", "framework", "api", "app", "application",
            "automation", "cli", "command-line", "web", "data",
            "analysis", "machine-learning", "ai", "documentation"
        ]
        
        # Add relevant common topics
        for topic in common_topics:
            if topic in readme.lower() or any(topic in t for t in current_topics):
                topics.add(topic)
        
        # Ensure we don't have too many topics
        topics_list = list(topics)
        if len(topics_list) > self.max_topics:
            # Keep current topics and add new ones up to the limit
            result = current_topics.copy()
            for topic in topics_list:
                if topic not in result:
                    result.append(topic)
                    if len(result) >= self.max_topics:
                        break
            return result
        
        return list(topics)
    
    def analyze_readme(self, readme: str) -> Dict[str, Any]:
        """Analyze the content of a README file using rule-based approaches.
        
        Args:
            readme: The content of the repository's README file.
            
        Returns:
            A dictionary containing the analysis results.
        """
        if not readme:
            return {
                "summary": "",
                "topics": [],
                "entities": [],
                "sentiment": "neutral",
                "readability": "unknown",
                "suggestions": ["Add a README file to your repository."]
            }
        
        # Extract the first paragraph as a summary
        summary = ""
        paragraphs = re.split(r'\n\s*\n', readme)
        for paragraph in paragraphs:
            # Skip headers and empty paragraphs
            if paragraph and not paragraph.strip().startswith('#') and len(paragraph) > 30:
                # Clean up markdown formatting
                summary = re.sub(r'[#*_]', '', paragraph.strip())
                break
        
        # If no good paragraph was found, use the first header
        if not summary:
            headers = re.findall(r'#\s+(.+)', readme)
            if headers:
                summary = headers[0]
        
        # Extract potential topics from README
        topics = []
        headers = re.findall(r'#+\s+(.+)', readme)
        for header in headers:
            words = re.findall(r'[a-zA-Z0-9]+', header.lower())
            for word in words:
                if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']:
                    if word not in topics:
                        topics.append(word)
        
        # Extract common words from README as additional topics
        words = re.findall(r'[a-zA-Z0-9]+', readme.lower())
        word_counts = Counter(words)
        common_words = [word for word, count in word_counts.most_common(10) 
                       if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']]
        
        for word in common_words:
            if word not in topics:
                topics.append(word)
        
        # Extract potential named entities (very basic approach)
        entities = []
        # Look for capitalized words that aren't at the start of sentences
        capitalized_words = re.findall(r'(?<!\.\s)[A-Z][a-zA-Z]+', readme)
        for word in capitalized_words:
            if word not in entities and word not in ['I', 'The', 'A', 'An', 'This', 'That']:
                entities.append(word)
        
        # Basic readability assessment
        avg_sentence_length = 0
        sentences = re.split(r'[.!?]+', readme)
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        readability = "good"
        if avg_sentence_length > 25:
            readability = "complex"
        elif avg_sentence_length < 10:
            readability = "simple"
        
        # Basic sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'awesome', 'best', 'better', 'improved']
        negative_words = ['bad', 'poor', 'terrible', 'worst', 'difficult', 'hard', 'complex', 'issue', 'problem']
        
        positive_count = sum(1 for word in positive_words if word in readme.lower())
        negative_count = sum(1 for word in negative_words if word in readme.lower())
        
        sentiment = "neutral"
        if positive_count > negative_count * 2:
            sentiment = "positive"
        elif negative_count > positive_count * 2:
            sentiment = "negative"
        
        # Generate suggestions
        suggestions = []
        
        if len(readme) < 500:
            suggestions.append("Add more content to your README file.")
        
        if not re.search(r'#+\s+Installation', readme, re.IGNORECASE):
            suggestions.append("Add an Installation section to your README.")
        
        if not re.search(r'#+\s+Usage', readme, re.IGNORECASE):
            suggestions.append("Add a Usage section to your README.")
        
        if not re.search(r'#+\s+Contributing', readme, re.IGNORECASE):
            suggestions.append("Add a Contributing section to your README.")
        
        if not re.search(r'#+\s+License', readme, re.IGNORECASE):
            suggestions.append("Add a License section to your README.")
        
        return {
            "summary": summary,
            "topics": topics[:10],  # Limit to 10 topics
            "entities": entities[:10],  # Limit to 10 entities
            "sentiment": sentiment,
            "readability": readability,
            "suggestions": suggestions
        }
    
    def generate_readme(self, repo_name: str, languages: List[str], 
                       topics: List[str], description: str, 
                       existing_readme: Optional[str] = None) -> str:
        """Generate a README file for a repository using rule-based approaches.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of topics for the repository.
            description: The description of the repository.
            existing_readme: The content of the existing README file, if any.
            
        Returns:
            A string containing the generated README content.
        """
        # If there's an existing README, use it as a base
        if existing_readme and len(existing_readme) > 100:
            return existing_readme
        
        # Clean up repository name for display
        display_name = repo_name.replace('-', ' ').replace('_', ' ').title()
        
        # Generate a basic README template
        readme = f"# {display_name}\n\n"
        
        # Add description
        readme += f"{description}\n\n"
        
        # Add badges for languages
        if languages:
            readme += "## Languages\n\n"
            for lang in languages:
                readme += f"![{lang}](https://img.shields.io/badge/-{lang}-{self._get_language_color(lang)}?style=flat-square&logo={lang.lower()})\n"
            readme += "\n"
        
        # Add installation section
        readme += "## Installation\n\n"
        
        if "python" in [lang.lower() for lang in languages]:
            readme += "```bash\n"
            readme += f"# Clone the repository\ngit clone https://github.com/username/{repo_name}.git\ncd {repo_name}\n\n"
            readme += "# Install dependencies\npip install -r requirements.txt\n"
            readme += "```\n\n"
        else:
            readme += "```bash\n"
            readme += f"# Clone the repository\ngit clone https://github.com/username/{repo_name}.git\ncd {repo_name}\n"
            readme += "```\n\n"
        
        # Add usage section
        readme += "## Usage\n\n"
        readme += "```bash\n"
        
        if "python" in [lang.lower() for lang in languages]:
            readme += f"python main.py\n"
        elif "javascript" in [lang.lower() for lang in languages] or "typescript" in [lang.lower() for lang in languages]:
            readme += f"npm start\n"
        elif "java" in [lang.lower() for lang in languages]:
            readme += f"java -jar {repo_name}.jar\n"
        elif "go" in [lang.lower() for lang in languages]:
            readme += f"go run main.go\n"
        elif "rust" in [lang.lower() for lang in languages]:
            readme += f"cargo run\n"
        else:
            readme += f"# Add usage instructions here\n"
        
        readme += "```\n\n"
        
        # Add features section
        readme += "## Features\n\n"
        for i in range(min(5, len(topics))):
            readme += f"- {topics[i].replace('-', ' ').replace('_', ' ').title()}\n"
        readme += "\n"
        
        # Add contributing section
        readme += "## Contributing\n\n"
        readme += "Contributions are welcome! Please feel free to submit a Pull Request.\n\n"
        
        # Add license section
        readme += "## License\n\n"
        readme += "This project is licensed under the MIT License - see the LICENSE file for details.\n"
        
        return readme
    
    def _get_language_color(self, language: str) -> str:
        """Get a color for a programming language.
        
        Args:
            language: The programming language.
            
        Returns:
            A color code for the language.
        """
        colors = {
            "Python": "3776AB",
            "JavaScript": "F7DF1E",
            "TypeScript": "3178C6",
            "Java": "007396",
            "C++": "00599C",
            "C#": "239120",
            "PHP": "777BB4",
            "Ruby": "CC342D",
            "Go": "00ADD8",
            "Rust": "DEA584",
            "Swift": "FA7343",
            "Kotlin": "0095D5",
            "Dart": "0175C2",
            "HTML": "E34F26",
            "CSS": "1572B6",
            "Shell": "4EAA25",
        }
        
        return colors.get(language, "555555")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model used by the provider.
        
        Returns:
            A dictionary containing information about the model.
        """
        return {
            "name": "local-rule-based",
            "version": "1.0.0",
            "provider": "local",
            "capabilities": [
                "description_generation",
                "topic_generation",
                "readme_analysis",
                "readme_generation"
            ]
        } 