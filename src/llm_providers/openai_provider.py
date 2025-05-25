#!/usr/bin/env python3
"""
OpenAI provider implementation for the GitHub Repository SEO Optimizer.

This module provides an implementation of the BaseProvider interface
that uses the OpenAI API to generate content.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from .base_provider import BaseProvider

# Configure logging
logger = logging.getLogger(__name__)

# Try to import the OpenAI library
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install it with: pip install openai>=1.0.0")


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation that uses the OpenAI API.
    
    This provider requires an OpenAI API key to be set in the
    OPENAI_API_KEY environment variable.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", 
                temperature: float = 0.7, max_tokens: int = 500):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: The OpenAI API key, or None to use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI library not available. Install it with: pip install openai>=1.0.0"
            )
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set the OPENAI_API_KEY environment variable."
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize the OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    def generate_description(self, repo_name: str, languages: List[str], 
                            topics: List[str], readme: str) -> str:
        """Generate a description for a repository using the OpenAI API.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A string containing the generated description.
        """
        # Prepare the prompt
        prompt = f"""
        Generate a concise and SEO-friendly description for a GitHub repository.
        
        Repository Name: {repo_name}
        Programming Languages: {', '.join(languages)}
        Topics: {', '.join(topics)}
        
        README Content:
        {readme[:2000]}  # Limit README content to avoid token limits
        
        The description should be:
        - Clear and concise (50-250 characters)
        - Highlight the main purpose and features of the repository
        - Include relevant keywords for SEO
        - Be written in a professional tone
        
        Return ONLY the description text, without any additional commentary.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SEO-friendly descriptions for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extract the description from the response
        description = response.choices[0].message.content.strip()
        
        # Ensure the description is not too long
        max_length = 250
        if len(description) > max_length:
            description = description[:max_length - 3] + "..."
        
        return description
    
    def generate_topics(self, repo_name: str, languages: List[str], 
                       current_topics: List[str], readme: str) -> List[str]:
        """Generate topics for a repository using the OpenAI API.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            current_topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A list of strings containing the generated topics.
        """
        # Prepare the prompt
        prompt = f"""
        Generate a list of SEO-friendly topics for a GitHub repository.
        
        Repository Name: {repo_name}
        Programming Languages: {', '.join(languages)}
        Current Topics: {', '.join(current_topics)}
        
        README Content:
        {readme[:2000]}  # Limit README content to avoid token limits
        
        The topics should:
        - Be relevant to the repository content
        - Include programming languages and frameworks used
        - Include the main functionality or purpose
        - Be good for discoverability on GitHub
        - Follow GitHub's topic guidelines (lowercase, hyphenated, no spaces)
        
        Return ONLY a JSON array of topic strings, without any additional commentary.
        Example: ["python", "machine-learning", "data-science", "neural-networks", "deep-learning"]
        
        Generate 10-20 topics.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SEO-friendly topics for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extract the topics from the response
        content = response.choices[0].message.content.strip()
        
        # Try to parse the JSON array
        try:
            # Find the JSON array in the response
            start_idx = content.find("[")
            end_idx = content.rfind("]") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                topics = json.loads(json_str)
                
                # Ensure all topics are strings
                topics = [str(topic).lower() for topic in topics]
                
                # Remove duplicates
                topics = list(dict.fromkeys(topics))
                
                # Limit to 20 topics
                return topics[:20]
            else:
                # If no JSON array is found, split by commas or newlines
                if "," in content:
                    topics = [t.strip().lower() for t in content.split(",")]
                else:
                    topics = [t.strip().lower() for t in content.split("\n") if t.strip()]
                
                # Remove duplicates
                topics = list(dict.fromkeys(topics))
                
                # Limit to 20 topics
                return topics[:20]
        except Exception as e:
            logger.error(f"Error parsing topics from OpenAI response: {e}")
            logger.debug(f"Response content: {content}")
            
            # Fall back to simple parsing
            topics = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # Remove quotes, brackets, and other non-alphanumeric characters
                    line = line.replace('"', '').replace("'", "").replace("[", "").replace("]", "")
                    topics.extend([t.strip().lower() for t in line.split(",") if t.strip()])
            
            # Remove duplicates
            topics = list(dict.fromkeys(topics))
            
            # Limit to 20 topics
            return topics[:20]
    
    def analyze_readme(self, readme: str) -> Dict[str, Any]:
        """Analyze the content of a README file using the OpenAI API.
        
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
        
        # Prepare the prompt
        prompt = f"""
        Analyze the following GitHub repository README content:
        
        {readme[:3000]}  # Limit README content to avoid token limits
        
        Provide the following analysis:
        1. A brief summary of the repository (2-3 sentences)
        2. A list of relevant topics extracted from the README
        3. A list of named entities (technologies, frameworks, libraries, etc.)
        4. The overall sentiment of the README (positive, neutral, negative)
        5. The readability assessment (simple, good, complex)
        6. Suggestions for improving the README
        
        Return the analysis as a JSON object with the following structure:
        {{
            "summary": "Brief summary of the repository",
            "topics": ["topic1", "topic2", "topic3", ...],
            "entities": ["entity1", "entity2", "entity3", ...],
            "sentiment": "positive|neutral|negative",
            "readability": "simple|good|complex",
            "suggestions": ["suggestion1", "suggestion2", ...]
        }}
        
        Return ONLY the JSON object, without any additional commentary.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes GitHub repository README content."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Extract the analysis from the response
        content = response.choices[0].message.content.strip()
        
        # Try to parse the JSON object
        try:
            # Find the JSON object in the response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Ensure all required fields are present
                analysis.setdefault("summary", "")
                analysis.setdefault("topics", [])
                analysis.setdefault("entities", [])
                analysis.setdefault("sentiment", "neutral")
                analysis.setdefault("readability", "good")
                analysis.setdefault("suggestions", [])
                
                return analysis
            else:
                logger.error("No JSON object found in OpenAI response")
                logger.debug(f"Response content: {content}")
                
                # Fall back to empty analysis
                return {
                    "summary": "",
                    "topics": [],
                    "entities": [],
                    "sentiment": "neutral",
                    "readability": "good",
                    "suggestions": []
                }
        except Exception as e:
            logger.error(f"Error parsing analysis from OpenAI response: {e}")
            logger.debug(f"Response content: {content}")
            
            # Fall back to empty analysis
            return {
                "summary": "",
                "topics": [],
                "entities": [],
                "sentiment": "neutral",
                "readability": "good",
                "suggestions": []
            }
    
    def generate_readme(self, repo_name: str, languages: List[str], 
                       topics: List[str], description: str, 
                       existing_readme: Optional[str] = None) -> str:
        """Generate a README file for a repository using the OpenAI API.
        
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
        
        # Prepare the prompt
        prompt = f"""
        Generate a comprehensive README.md file for a GitHub repository.
        
        Repository Name: {repo_name}
        Programming Languages: {', '.join(languages)}
        Topics: {', '.join(topics)}
        Description: {description}
        
        The README should include:
        1. A clear title and description
        2. Badges for the programming languages used
        3. Installation instructions
        4. Usage examples
        5. Features list
        6. Contributing guidelines
        7. License information
        
        Format the README using proper Markdown syntax.
        Include code blocks with appropriate language tags.
        Make the README visually appealing and well-structured.
        
        Return ONLY the README content in Markdown format, without any additional commentary.
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates comprehensive README files for GitHub repositories."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=1500  # Increase token limit for README generation
        )
        
        # Extract the README from the response
        readme = response.choices[0].message.content.strip()
        
        return readme
    
    def validate_api_key(self) -> bool:
        """Validate the API key for the provider.
        
        Returns:
            True if the API key is valid, False otherwise.
        """
        try:
            # Make a simple API call to validate the key
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Error validating OpenAI API key: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model used by the provider.
        
        Returns:
            A dictionary containing information about the model.
        """
        return {
            "name": self.model,
            "version": "1.0.0",
            "provider": "openai",
            "capabilities": [
                "description_generation",
                "topic_generation",
                "readme_analysis",
                "readme_generation"
            ]
        } 