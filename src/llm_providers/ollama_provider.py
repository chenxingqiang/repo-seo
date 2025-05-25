"""
Ollama Language Model Provider for GitHub SEO Optimizer

This provider allows using local language models through Ollama.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional

from . import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama language model provider for local LLMs."""

    def __init__(self,
                 api_base: str = "http://localhost:11434",
                 model: str = "mistral:latest",
                 **kwargs):
        """
        Initialize the Ollama provider.

        Args:
            api_base: Base URL for the Ollama API. Default is "http://localhost:11434".
            model: Model to use for generation. Default is "mistral:latest".
            **kwargs: Additional arguments to pass to the Ollama API.
        """
        self.api_base = api_base
        self.model = model
        self.kwargs = kwargs

    def _generate_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a completion using the Ollama API.

        Args:
            prompt: Prompt to generate completion for.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Generated text.
        """
        try:
            # First check if the model exists
            try:
                model_check = requests.get(f"{self.api_base}/api/tags", timeout=5)
                if model_check.status_code != 200:
                    return f"Error: Ollama API not available at {self.api_base}"

                # Parse the available models
                available_models = []
                models_data = model_check.json()

                # The API response format might vary between Ollama versions
                if "models" in models_data:
                    # Newer Ollama versions
                    available_models = [model.get("name") for model in models_data.get("models", []) if model.get("name")]
                else:
                    # Older Ollama versions
                    available_models = [model.get("name") for model in models_data.get("models", [])] if "models" in models_data else []
                    # If no models found in the expected format, try to extract from the raw response
                    if not available_models and isinstance(models_data, dict):
                        for key in models_data:
                            if isinstance(models_data[key], list):
                                for item in models_data[key]:
                                    if isinstance(item, dict) and "name" in item:
                                        available_models.append(item["name"])

                # If still no models found, try a different approach
                if not available_models:
                    # Try to list models directly
                    try:
                        list_models = requests.get(f"{self.api_base}/api/tags", timeout=5)
                        if list_models.status_code == 200:
                            list_data = list_models.json()
                            if "models" in list_data and isinstance(list_data["models"], list):
                                available_models = [m.get("name", "") for m in list_data["models"] if isinstance(m, dict)]
                    except:
                        pass

                # Check if our model is available
                if self.model not in available_models:
                    # Try to find a suitable alternative
                    alternative_models = []
                    common_models = ["mistral:latest", "llama2:latest", "deepseek-coder", "deepseek-r1:7b", "neural-chat"]

                    for model in common_models:
                        if model in available_models:
                            alternative_models.append(model)

                    # If we found alternatives, suggest them
                    if alternative_models:
                        self.model = alternative_models[0]  # Use the first alternative
                        print(f"Model '{self.model}' not found. Using '{alternative_models[0]}' instead.")
                    elif available_models:
                        # Use the first available model
                        self.model = available_models[0]
                        print(f"Model '{self.model}' not found. Using '{available_models[0]}' instead.")
                    else:
                        return f"Error: Model '{self.model}' not found and no alternatives available."
            except Exception as e:
                # Continue anyway, the model check might fail but the model might still be available
                print(f"Warning: Could not check model availability: {str(e)}")

            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        **self.kwargs
                    }
                },
                timeout=60  # Increase timeout for larger models
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                error_msg = f"Error from Ollama API: {response.status_code}"
                try:
                    error_details = response.json()
                    if isinstance(error_details, dict) and "error" in error_details:
                        error_msg += f" - {error_details['error']}"
                except:
                    error_msg += f" - {response.text}"
                return error_msg
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama API. Make sure Ollama is running."
        except requests.exceptions.Timeout:
            return "Error: Request to Ollama API timed out. The model might be too large or busy."
        except Exception as e:
            return f"Error generating completion with Ollama: {str(e)}"

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
        {readme[:1000]}  # Limit README content to avoid token limits

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
        {readme[:1000]}  # Limit README content to avoid token limits

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
        {content[:1500]}  # Limit README content to avoid token limits

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