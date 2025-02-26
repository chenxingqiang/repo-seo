import logging
from typing import List, Dict

class SEOGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_description_length = 300
        self.max_keywords = 10

    def generate_keywords(self, analyzed_data: Dict) -> List[str]:
        """
        Generate SEO keywords based on analyzed repository data.

        Args:
            analyzed_data: Dictionary containing analyzed repository data

        Returns:
            List of SEO keywords
        """
        try:
            keywords = set()

            # Add programming language if available
            if analyzed_data.get("language"):
                keywords.add(analyzed_data["language"].lower())

            # Add extracted topics
            keywords.update([topic.lower() for topic in analyzed_data.get("topics", [])])

            # Add repository name words (excluding common words)
            name_words = analyzed_data.get("name", "").replace("-", " ").replace("_", " ").split()
            keywords.update([word.lower() for word in name_words if len(word) > 2])

            # Sort and limit keywords
            sorted_keywords = sorted(list(keywords))[:self.max_keywords]

            return sorted_keywords
        except Exception as e:
            self.logger.error(f"Error generating keywords: {str(e)}")
            return []

    def generate_description(self, analyzed_data: Dict) -> str:
        """
        Generate SEO-optimized description based on analyzed repository data.

        Args:
            analyzed_data: Dictionary containing analyzed repository data

        Returns:
            SEO-optimized description
        """
        try:
            name = analyzed_data.get("name", "")
            language = analyzed_data.get("language", "")
            topics = analyzed_data.get("topics", [])
            original_description = analyzed_data.get("description", "")

            # Start with the original description if available
            if original_description:
                description = original_description
            else:
                description = f"A {language} repository" if language else "A repository"

            # Add topics if available
            if topics:
                topic_str = ", ".join(topics[:5])  # Limit to top 5 topics
                description = f"{description} focusing on {topic_str}"

            # Add language if not mentioned
            if language and language.lower() not in description.lower():
                description = f"{description}. Built with {language}"

            # Truncate if too long
            if len(description) > self.max_description_length:
                description = description[:self.max_description_length].rsplit(" ", 1)[0] + "..."

            return description
        except Exception as e:
            self.logger.error(f"Error generating description: {str(e)}")
            return ""

    def optimize_repository(self, analyzed_data: Dict) -> Dict:
        """
        Generate SEO optimizations for a repository.

        Args:
            analyzed_data: Dictionary containing analyzed repository data

        Returns:
            Dictionary with SEO optimizations
        """
        try:
            keywords = self.generate_keywords(analyzed_data)
            description = self.generate_description(analyzed_data)

            return {
                "name": analyzed_data.get("name", ""),
                "original_description": analyzed_data.get("description", ""),
                "seo_description": description,
                "seo_keywords": keywords
            }
        except Exception as e:
            self.logger.error(f"Error optimizing repository: {str(e)}")
            return {}
