"""
Tests for the topic validation functionality.
"""

import unittest
import sys
import os
import re

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the validate_github_topic function from repo_seo.py
from src.repo_seo import validate_github_topic


class TestTopicValidation(unittest.TestCase):
    """Test the GitHub topic validation functionality."""
    
    def test_valid_topics(self):
        """Test that valid topics are preserved."""
        valid_topics = [
            "python",
            "machine-learning",
            "data-science",
            "api",
            "cli",
            "automation",
            "github",
            "seo"
        ]
        
        for topic in valid_topics:
            validated = validate_github_topic(topic)
            self.assertEqual(validated, topic, f"Valid topic '{topic}' was modified to '{validated}'")
    
    def test_spaces_converted_to_hyphens(self):
        """Test that spaces are converted to hyphens."""
        test_cases = [
            ("machine learning", "machine-learning"),
            ("data science", "data-science"),
            ("github seo", "github-seo"),
            ("  extra  spaces  ", "extra-spaces")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic with spaces '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_uppercase_converted_to_lowercase(self):
        """Test that uppercase letters are converted to lowercase."""
        test_cases = [
            ("Python", "python"),
            ("MachineLearning", "machinelearning"),
            ("GitHub", "github"),
            ("SEO", "seo")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Uppercase topic '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_invalid_characters_removed(self):
        """Test that invalid characters are removed."""
        test_cases = [
            ("python!", "python"),
            ("machine@learning", "machinelearning"),
            ("data.science", "datascience"),
            ("github#seo", "githubseo"),
            ("api_v2", "api-v2"),  # Underscores should be converted to hyphens
            ("c++", "c"),
            ("c#", "c")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic with invalid chars '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_consecutive_hyphens_collapsed(self):
        """Test that consecutive hyphens are collapsed into a single hyphen."""
        test_cases = [
            ("machine--learning", "machine-learning"),
            ("data---science", "data-science"),
            ("github----seo", "github-seo")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic with consecutive hyphens '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_leading_trailing_hyphens_removed(self):
        """Test that leading and trailing hyphens are removed."""
        test_cases = [
            ("-python", "python"),
            ("machine-learning-", "machine-learning"),
            ("-data-science-", "data-science")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic with leading/trailing hyphens '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_must_start_with_letter_or_number(self):
        """Test that topics must start with a letter or number."""
        test_cases = [
            ("-python", "python"),  # Leading hyphen removed
            ("_machine", "machine"),  # Leading underscore removed
            ("!data", "data"),  # Leading special char removed
            ("", "")  # Empty string remains empty
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic not starting with letter/number '{input_topic}' was not correctly converted to '{expected_output}'")
    
    def test_maximum_length(self):
        """Test that topics are truncated to maximum length (35 characters)."""
        long_topic = "a" * 40
        expected_output = "a" * 35
        
        validated = validate_github_topic(long_topic)
        self.assertEqual(validated, expected_output, 
                        f"Long topic was not correctly truncated to 35 characters")
    
    def test_comma_handling(self):
        """Test that topics with commas are rejected."""
        test_cases = [
            ("python,javascript", ""),
            ("machine,learning", ""),
            ("data,science", "")
        ]
        
        for input_topic, expected_output in test_cases:
            validated = validate_github_topic(input_topic)
            self.assertEqual(validated, expected_output, 
                            f"Topic with commas '{input_topic}' was not correctly rejected")
    
    def test_none_or_empty_input(self):
        """Test that None or empty input returns empty string."""
        self.assertEqual(validate_github_topic(None), "")
        self.assertEqual(validate_github_topic(""), "")
        self.assertEqual(validate_github_topic("   "), "")


if __name__ == "__main__":
    unittest.main() 