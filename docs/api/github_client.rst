GitHub Client API
=================

This module provides the interface for interacting with GitHub repositories.

GitHubClient Class
------------------

.. automodule:: github_client.github_client
   :members:
   :undoc-members:
   :show-inheritance:

Repository Model
----------------

.. automodule:: github_client.models
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: github_client.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from github_client import GitHubClient
   
   # Initialize client
   client = GitHubClient()
   
   # Get repository information
   repo = client.get_repository("owner", "repo-name")
   
   # Update repository description
   client.update_repository(
       owner="owner",
       repo="repo-name",
       description="New description",
       topics=["python", "automation", "seo"]
   )

Batch Operations
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all repositories for a user
   repos = client.list_repositories("username")
   
   # Filter repositories
   repos_without_description = [
       repo for repo in repos 
       if not repo.description
   ]
   
   # Process multiple repositories
   for repo in repos_without_description:
       # Generate and update description
       pass 