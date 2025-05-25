#!/usr/bin/env python3
"""
SEO generator implementation for the GitHub Repository SEO Optimizer.

This module provides functionality for generating SEO content for repositories,
including descriptions, topics, and README files.
"""

import re
import logging
from typing import Dict, List, Any, Optional

from ..llm_providers import get_provider, BaseProvider
from ..content_analyzer import ContentAnalyzer, extract_topics_from_text

# Configure logging
logger = logging.getLogger(__name__)


class SEOGenerator:
    """SEO generator for repository content."""
    
    def __init__(self, provider_name: str = "local", **provider_kwargs):
        """Initialize the SEO generator.
        
        Args:
            provider_name: The name of the LLM provider to use.
            **provider_kwargs: Additional arguments to pass to the provider.
        """
        self.provider_name = provider_name
        self.provider_kwargs = provider_kwargs
        self.provider = get_provider(provider_name, **provider_kwargs)
        self.analyzer = ContentAnalyzer()
    
    def generate_description(self, repo_name: str, languages: List[str], 
                            topics: List[str], readme: str) -> str:
        """Generate a description for a repository.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A string containing the generated description.
        """
        try:
            return self.provider.generate_description(
                repo_name=repo_name,
                languages=languages,
                topics=topics,
                readme=readme
            )
        except Exception as e:
            logger.error(f"Error generating description with provider '{self.provider_name}': {e}")
            # Fall back to rule-based description generation
            return generate_description(repo_name, languages, topics, readme)
    
    def generate_topics(self, repo_name: str, languages: List[str], 
                       current_topics: List[str], readme: str) -> List[str]:
        """Generate topics for a repository.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            current_topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A list of strings containing the generated topics.
        """
        try:
            return self.provider.generate_topics(
                repo_name=repo_name,
                languages=languages,
                current_topics=current_topics,
                readme=readme
            )
        except Exception as e:
            logger.error(f"Error generating topics with provider '{self.provider_name}': {e}")
            # Fall back to rule-based topic generation
            return generate_topics(repo_name, languages, current_topics, readme)
    
    def generate_readme(self, repo_name: str, languages: List[str], 
                       topics: List[str], description: str, 
                       existing_readme: Optional[str] = None) -> str:
        """Generate a README file for a repository.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of topics for the repository.
            description: The description of the repository.
            existing_readme: The content of the existing README file, if any.
            
        Returns:
            A string containing the generated README content.
        """
        try:
            return self.provider.generate_readme(
                repo_name=repo_name,
                languages=languages,
                topics=topics,
                description=description,
                existing_readme=existing_readme
            )
        except Exception as e:
            logger.error(f"Error generating README with provider '{self.provider_name}': {e}")
            # Fall back to rule-based README generation
            return generate_readme(repo_name, languages, topics, description, existing_readme)
    
    def optimize_repository(self, repo_name: str, languages: List[str], 
                           current_topics: List[str], current_description: str, 
                           readme: str) -> Dict[str, Any]:
        """Optimize a repository's SEO content.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            current_topics: List of current topics for the repository.
            current_description: The current description of the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A dictionary containing the optimized content.
        """
        # Analyze the repository content
        analysis = self.analyzer.analyze_repository(
            repo_name=repo_name,
            description=current_description,
            languages=languages,
            topics=current_topics,
            readme=readme
        )
        
        # Generate a new description if needed
        new_description = current_description
        if not current_description or len(current_description) < 30:
            new_description = self.generate_description(
                repo_name=repo_name,
                languages=languages,
                topics=current_topics,
                readme=readme
            )
        
        # Generate new topics
        new_topics = self.generate_topics(
            repo_name=repo_name,
            languages=languages,
            current_topics=current_topics,
            readme=readme
        )
        
        # Generate a new README if needed
        new_readme = readme
        if not readme or len(readme) < 100:
            new_readme = self.generate_readme(
                repo_name=repo_name,
                languages=languages,
                topics=new_topics,
                description=new_description,
                existing_readme=readme
            )
        
        return {
            "name": repo_name,
            "languages": languages,
            "current_description": current_description,
            "new_description": new_description,
            "current_topics": current_topics,
            "new_topics": new_topics,
            "current_readme": readme,
            "new_readme": new_readme,
            "analysis": analysis,
            "changes": {
                "description": new_description != current_description,
                "topics": set(new_topics) != set(current_topics),
                "readme": new_readme != readme
            }
        }


def generate_description(repo_name: str, languages: List[str], 
                        topics: List[str], readme: str) -> str:
    """Generate a description for a repository using rule-based approaches.
    
    Args:
        repo_name: The name of the repository.
        languages: List of programming languages used in the repository.
        topics: List of topics for the repository.
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
    if len(first_line) >= 30:
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
    max_length = 250
    if len(description) > max_length:
        description = description[:max_length - 3] + "..."
    
    return description


def generate_topics(repo_name: str, languages: List[str], 
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
    
    # Extract topics from README
    if readme:
        readme_topics = extract_topics_from_text(readme)
        topics.update(readme_topics)
    
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
    max_topics = 20
    topics_list = list(topics)
    if len(topics_list) > max_topics:
        # Keep current topics and add new ones up to the limit
        result = current_topics.copy()
        for topic in topics_list:
            if topic not in result:
                result.append(topic)
                if len(result) >= max_topics:
                    break
        return result
    
    return list(topics)


def generate_readme(repo_name: str, languages: List[str], 
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
            color = get_language_color(lang)
            readme += f"![{lang}](https://img.shields.io/badge/-{lang}-{color}?style=flat-square&logo={lang.lower()})\n"
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


def get_language_color(language: str) -> str:
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