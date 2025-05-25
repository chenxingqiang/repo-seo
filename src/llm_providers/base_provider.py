#!/usr/bin/env python3
"""
Base provider class for LLM providers.

This module defines the base interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseProvider(ABC):
    """Base class for LLM providers.
    
    All LLM providers must inherit from this class and implement its methods.
    """
    
    @abstractmethod
    def generate_description(self, repo_name: str, languages: List[str], 
                            topics: List[str], readme: str) -> str:
        """Generate a description for a repository.
        
        Args:
            repo_name: The name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of current topics for the repository.
            readme: The content of the repository's README file.
            
        Returns:
            A string containing the generated description.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def analyze_readme(self, readme: str) -> Dict[str, Any]:
        """Analyze the content of a README file.
        
        Args:
            readme: The content of the repository's README file.
            
        Returns:
            A dictionary containing the analysis results, which may include:
            - summary: A summary of the README content.
            - topics: A list of topics extracted from the README.
            - entities: A list of named entities extracted from the README.
            - sentiment: The sentiment of the README content.
            - readability: The readability score of the README content.
            - suggestions: Suggestions for improving the README content.
        """
        pass
    
    @abstractmethod
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
        pass
    
    def validate_api_key(self) -> bool:
        """Validate the API key for the provider.
        
        Returns:
            True if the API key is valid, False otherwise.
        """
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model used by the provider.
        
        Returns:
            A dictionary containing information about the model, which may include:
            - name: The name of the model.
            - version: The version of the model.
            - provider: The name of the provider.
            - capabilities: A list of capabilities of the model.
        """
        return {
            "name": "base",
            "version": "0.1.0",
            "provider": "base",
            "capabilities": []
        } 