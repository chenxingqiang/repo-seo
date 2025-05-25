"""
DeepSeek Language Model Provider for GitHub SEO Optimizer

This provider allows using DeepSeek's models.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional

from . import LLMProvider


class DeepSeekProvider(LLMProvider):
    """DeepSeek language model provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat", **kwargs):
        """
        Initialize the DeepSeek provider.

        Args:
            api_key: DeepSeek API key. If not provided, will try to get from environment.
            model: Model to use for generation. Default is "deepseek-chat".
            **kwargs: Additional arguments to pass to the DeepSeek API.
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided and not found in environment")

        self.model = model
        self.api_base = kwargs.pop("api_base", "https://api.deepseek.com/v1")
        self.kwargs = kwargs

    def _generate_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a completion using the DeepSeek API.

        Args:
            prompt: Prompt to generate completion for.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Generated text.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that specializes in GitHub repository SEO optimization."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                **self.kwargs
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                error_msg = f"Error from DeepSeek API: {response.status_code}"
                try:
                    error_details = response.json()
                    if isinstance(error_details, dict) and "error" in error_details:
                        error_msg += f" - {error_details['error']}"
                except:
                    error_msg += f" - {response.text}"
                return error_msg
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to DeepSeek API."
        except requests.exceptions.Timeout:
            return "Error: Request to DeepSeek API timed out."
        except Exception as e:
            return f"Error generating completion with DeepSeek: {str(e)}"

    def generate_description(self, repo_name: str, languages: List[str],
                           topics: List[str], readme: str) -> str:
        """
        Generate an SEO-friendly description for a repository.

        Args:
            repo_name: Name of the repository.
            languages: List of programming languages used in the repository.
            topics: List of current repository topics.
            readme: README content.

        Returns:
            SEO-friendly description.
        """
        prompt = f"""
        Generate a concise, SEO-friendly description for a GitHub repository with the following details:

        Repository Name: {repo_name}
        Programming Languages: {', '.join(languages)}
        Current Topics: {', '.join(topics)}

        README Content:
        {readme[:2000]}  # Limit README content to avoid token limits

        The description should:
        1. Be 1-2 sentences (maximum 160 characters)
        2. Include key technologies and purpose
        3. Be clear and informative
        4. Use relevant keywords naturally

        Return only the description text without quotes or additional commentary.
        """

        description = self._generate_completion(prompt, max_tokens=200)

        # Ensure description is not too long
        if len(description) > 160:
            description = description[:157] + "..."

        return description

    def generate_topics(self, repo_name: str, languages: List[str],
                      current_topics: List[str], readme: str) -> List[str]:
        """
        Generate SEO-friendly topics for a repository.

        Args:
            repo_name: Name of the repository.
            languages: List of programming languages used in the repository.
            current_topics: List of current repository topics.
            readme: README content.

        Returns:
            List of SEO-friendly topics.
        """
        prompt = f"""
        Generate a list of SEO-friendly topics for a GitHub repository with the following details:

        Repository Name: {repo_name}
        Programming Languages: {', '.join(languages)}
        Current Topics: {', '.join(current_topics)}

        README Content:
        {readme[:2000]}  # Limit README content to avoid token limits

        The topics should:
        1. Be relevant to the repository content and purpose
        2. Include key technologies, frameworks, and concepts
        3. Follow GitHub topic guidelines (lowercase, hyphenated, no spaces)
        4. Maximum 20 topics total

        Return the topics as a JSON array of strings, without any additional text.
        Example: ["python", "machine-learning", "data-science"]
        """

        response = self._generate_completion(prompt, max_tokens=300)

        # Try to parse the response as JSON
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            # Try to find a JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                topics = json.loads(json_str)
            else:
                # Fallback: split by commas and clean up
                topics = [t.strip().strip('"\'').lower() for t in response.split(',')]

            # Ensure topics is a list of strings
            if not isinstance(topics, list):
                return current_topics

            # Filter out non-string topics
            topics = [t for t in topics if isinstance(t, str)]

            # Combine with current topics
            all_topics = list(set(topics + current_topics))

            # Limit to 20 topics
            return all_topics[:20]
        except Exception as e:
            print(f"Error parsing topics: {str(e)}")
            return current_topics

    def analyze_readme(self, content: str) -> Dict[str, Any]:
        """
        Analyze README content to extract summary, topics, and named entities.

        Args:
            content: README content.

        Returns:
            Dictionary containing summary, topics, and named entities.
        """
        prompt = f"""
        Analyze the following GitHub repository README content and extract:
        1. A brief summary (1-2 sentences)
        2. Key topics/technologies mentioned
        3. Named entities (libraries, frameworks, tools mentioned)

        README Content:
        {content[:3000]}  # Limit README content to avoid token limits

        Return the results as a JSON object with the following structure:
        {{
            "summary": "Brief summary of the repository",
            "topics": ["topic1", "topic2", "topic3"],
            "entities": ["entity1", "entity2", "entity3"]
        }}
        """

        response = self._generate_completion(prompt, max_tokens=500)

        # Try to parse the response as JSON
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            # Try to find a JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                result = json.loads(json_str)
            else:
                # Fallback: create a basic structure
                result = {
                    "summary": "",
                    "topics": [],
                    "entities": []
                }

            # Ensure required keys are present
            if "summary" not in result:
                result["summary"] = ""
            if "topics" not in result:
                result["topics"] = []
            if "entities" not in result:
                result["entities"] = []

            return result
        except Exception as e:
            print(f"Error parsing README analysis: {str(e)}")
            return {
                "summary": "",
                "topics": [],
                "entities": []
            }