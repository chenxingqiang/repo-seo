"""
Integration tests for the GitHub Repository SEO Optimizer.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from repo_seo.py
from src.repo_seo import (
    validate_github_topic,
    optimize_repository,
    get_repo_details,
    get_repo_languages,
    get_repo_topics,
    get_repo_readme
)


class MockResponse:
    """Mock response object for testing."""

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data


class TestIntegration(unittest.TestCase):
    """Integration tests for the GitHub Repository SEO Optimizer."""

    @patch('repo_seo.run_command')
    def test_get_repo_details(self, mock_run_command):
        """Test getting repository details."""
        # Mock the run_command function
        mock_run_command.return_value = (
            '{"name": "test-repo", "description": "Test description", "url": "https://github.com/test/test-repo"}',
            "",
            0
        )

        # Call the function
        result = get_repo_details("test", "test-repo")

        # Check the result
        self.assertEqual(result["name"], "test-repo")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["url"], "https://github.com/test/test-repo")

        # Verify the command that was run
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        self.assertEqual(args[0], "gh")
        self.assertEqual(args[1], "repo")
        self.assertEqual(args[2], "view")
        self.assertEqual(args[3], "test/test-repo")

    @patch('repo_seo.run_command')
    def test_get_repo_languages(self, mock_run_command):
        """Test getting repository languages."""
        # Mock the run_command function
        mock_run_command.return_value = (
            '{"Python": 80.5, "JavaScript": 19.5}',
            "",
            0
        )

        # Call the function
        result = get_repo_languages("test", "test-repo")

        # Check the result
        self.assertEqual(result["Python"], 80.5)
        self.assertEqual(result["JavaScript"], 19.5)

        # Verify the command that was run
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        self.assertEqual(args[0], "gh")
        self.assertEqual(args[1], "api")
        self.assertEqual(args[2], "repos/test/test-repo/languages")

    @patch('repo_seo.run_command')
    def test_get_repo_topics(self, mock_run_command):
        """Test getting repository topics."""
        # Mock the run_command function
        mock_run_command.return_value = (
            '{"names": ["python", "seo", "github"]}',
            "",
            0
        )

        # Call the function
        result = get_repo_topics("test", "test-repo")

        # Check the result
        self.assertEqual(result, ["python", "seo", "github"])

        # Verify the command that was run
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        self.assertEqual(args[0], "gh")
        self.assertEqual(args[1], "api")
        self.assertEqual(args[2], "repos/test/test-repo/topics")

    @patch('repo_seo.run_command')
    def test_get_repo_readme(self, mock_run_command):
        """Test getting repository README."""
        # Mock the run_command function
        mock_run_command.return_value = (
            "# Test Repo\n\nThis is a test repository.",
            "",
            0
        )

        # Call the function
        result = get_repo_readme("test", "test-repo")

        # Check the result
        self.assertEqual(result, "# Test Repo\n\nThis is a test repository.")

        # Verify the command that was run
        mock_run_command.assert_called_once()
        args = mock_run_command.call_args[0][0]
        self.assertEqual(args[0], "gh")
        self.assertEqual(args[1], "api")
        self.assertEqual(args[2], "repos/test/test-repo/readme")

    @patch('repo_seo.get_repo_details')
    @patch('repo_seo.get_repo_languages')
    @patch('repo_seo.get_repo_topics')
    @patch('repo_seo.get_repo_readme')
    @patch('repo_seo.update_repo_description')
    @patch('repo_seo.update_repo_topics')
    @patch('repo_seo.create_or_update_readme')
    @patch('repo_seo.get_provider')
    def test_optimize_repository_with_local_provider(
        self, mock_get_provider, mock_create_readme, mock_update_topics,
        mock_update_desc, mock_get_readme, mock_get_topics,
        mock_get_langs, mock_get_details
    ):
        """Test optimizing a repository with the local provider."""
        # Mock the repository data
        mock_get_details.return_value = {
            "name": "test-repo",
            "description": "Old description",
            "url": "https://github.com/test/test-repo"
        }
        mock_get_langs.return_value = {"Python": 80.5, "JavaScript": 19.5}
        mock_get_topics.return_value = ["python", "github"]
        mock_get_readme.return_value = "# Test Repo\n\nThis is a test repository."

        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_description.return_value = "New SEO-friendly description"
        mock_provider.generate_topics.return_value = ["python", "github", "seo", "automation"]
        mock_get_provider.return_value = mock_provider

        # Mock the update functions
        mock_update_desc.return_value = True
        mock_update_topics.return_value = True
        mock_create_readme.return_value = False

        # Import the function here to ensure the mocks are applied
        from src.repo_seo import optimize_repository

        # Call the function
        result = optimize_repository("test", "test-repo", dry_run=False, llm_provider="local")

        # Check that the provider was called correctly
        mock_get_provider.assert_called_once_with("local")
        
        # Check that the description generator was called correctly
        mock_provider.generate_description.assert_called_once()
        desc_args = mock_provider.generate_description.call_args[1]
        self.assertEqual(desc_args["repo_name"], "test-repo")
        self.assertEqual(desc_args["languages"], ["Python", "JavaScript"])
        self.assertEqual(desc_args["topics"], ["python", "github"])
        self.assertEqual(desc_args["readme"], "# Test Repo\n\nThis is a test repository.")

        # Check that the topics generator was called correctly
        mock_provider.generate_topics.assert_called_once()
        topics_args = mock_provider.generate_topics.call_args[1]
        self.assertEqual(topics_args["repo_name"], "test-repo")
        self.assertEqual(topics_args["languages"], ["Python", "JavaScript"])
        self.assertEqual(topics_args["current_topics"], ["python", "github"])
        self.assertEqual(topics_args["readme"], "# Test Repo\n\nThis is a test repository.")

        # Check that the update functions were called correctly
        mock_update_desc.assert_called_once_with("test", "test-repo", "New SEO-friendly description")

        # Check the result
        self.assertEqual(result["repository"], "test-repo")
        self.assertEqual(result["description"]["before"], "Old description")
        self.assertEqual(result["description"]["after"], "New SEO-friendly description")
        self.assertEqual(result["topics"]["before"], ["python", "github"])
        self.assertTrue(all(topic in result["topics"]["after"] for topic in ["python", "github", "seo", "automation"]))

    @patch('repo_seo.get_repo_details')
    @patch('repo_seo.get_repo_languages')
    @patch('repo_seo.get_repo_topics')
    @patch('repo_seo.get_repo_readme')
    @patch('repo_seo.get_provider')
    def test_optimize_repository_dry_run(
        self, mock_get_provider, mock_get_readme, mock_get_topics,
        mock_get_langs, mock_get_details
    ):
        """Test optimizing a repository in dry run mode."""
        # Mock the repository data
        mock_get_details.return_value = {
            "name": "test-repo",
            "description": "Old description",
            "url": "https://github.com/test/test-repo"
        }
        mock_get_langs.return_value = {"Python": 80.5, "JavaScript": 19.5}
        mock_get_topics.return_value = ["python", "github"]
        mock_get_readme.return_value = "# Test Repo\n\nThis is a test repository."

        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.generate_description.return_value = "New SEO-friendly description"
        mock_provider.generate_topics.return_value = ["python", "github", "seo", "automation"]
        mock_get_provider.return_value = mock_provider

        # Import the function here to ensure the mocks are applied
        from src.repo_seo import optimize_repository

        # Call the function in dry run mode
        result = optimize_repository("test", "test-repo", dry_run=True, llm_provider="local")

        # Check the result
        self.assertEqual(result["repository"], "test-repo")
        self.assertEqual(result["description"]["before"], "Old description")
        self.assertEqual(result["description"]["after"], "New SEO-friendly description")
        self.assertEqual(result["topics"]["before"], ["python", "github"])
        self.assertTrue(all(topic in result["topics"]["after"] for topic in ["python", "github", "seo", "automation"]))
        self.assertFalse(result["readme"]["updated"])


if __name__ == "__main__":
    unittest.main()