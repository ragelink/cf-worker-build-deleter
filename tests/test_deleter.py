import json
import os
import unittest
from unittest.mock import patch, MagicMock

import responses

# Import the module to test
from deleter.src.delete_deployments import CloudflareDeploymentDeleter, load_env_file


class TestCloudflareDeploymentDeleter(unittest.TestCase):
    """Tests for the CloudflareDeploymentDeleter class."""

    def setUp(self):
        """Set up test environment."""
        self.account_id = "test_account_123"
        self.project_name = "test-project"
        self.api_token = "test_token_123"
        
        # Create a deleter instance for testing
        self.deleter = CloudflareDeploymentDeleter(
            account_id=self.account_id,
            project_name=self.project_name,
            api_token=self.api_token,
            dry_run=True  # Use dry run for safety
        )
        
        # Base URL for API requests
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects/{self.project_name}"

    def test_init_with_token(self):
        """Test initialization with API token."""
        deleter = CloudflareDeploymentDeleter(
            account_id=self.account_id,
            project_name=self.project_name,
            api_token=self.api_token
        )
        
        self.assertEqual(deleter.account_id, self.account_id)
        self.assertEqual(deleter.project_name, self.project_name)
        self.assertEqual(deleter.api_token, self.api_token)
        self.assertEqual(deleter.headers, {"Authorization": f"Bearer {self.api_token}"})

    def test_init_with_email_key(self):
        """Test initialization with email and API key."""
        email = "test@example.com"
        api_key = "test_key_456"
        
        deleter = CloudflareDeploymentDeleter(
            account_id=self.account_id,
            project_name=self.project_name,
            email=email,
            api_key=api_key
        )
        
        self.assertEqual(deleter.account_id, self.account_id)
        self.assertEqual(deleter.project_name, self.project_name)
        self.assertEqual(deleter.email, email)
        self.assertEqual(deleter.api_key, api_key)
        self.assertEqual(deleter.headers, {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key
        })

    def test_init_without_auth(self):
        """Test initialization without auth credentials."""
        with self.assertRaises(ValueError):
            CloudflareDeploymentDeleter(
                account_id=self.account_id,
                project_name=self.project_name
            )

    @responses.activate
    def test_get_deployments_paginated(self):
        """Test fetching deployments with pagination."""
        # Mock the first page of results
        deployments_url = f"{self.base_url}/deployments"
        mock_deployments_page1 = {
            "success": True,
            "result": [
                {"id": "deployment1", "name": "Test Deployment 1"},
                {"id": "deployment2", "name": "Test Deployment 2"},
            ],
            "result_info": {
                "page": 1,
                "per_page": 2,
                "total_count": 3,
                "total_pages": 2
            }
        }
        
        responses.add(
            responses.GET,
            f"{deployments_url}?page=1&per_page=25",
            json=mock_deployments_page1,
            status=200
        )
        
        # Mock the second page of results
        mock_deployments_page2 = {
            "success": True,
            "result": [
                {"id": "deployment3", "name": "Test Deployment 3"},
            ],
            "result_info": {
                "page": 2,
                "per_page": 2,
                "total_count": 3,
                "total_pages": 2
            }
        }
        
        responses.add(
            responses.GET,
            f"{deployments_url}?page=2&per_page=25",
            json=mock_deployments_page2,
            status=200
        )
        
        # Call the method
        deployments = self.deleter.get_deployments_paginated()
        
        # Validate results
        self.assertEqual(len(deployments), 3)
        self.assertEqual(deployments[0]["id"], "deployment1")
        self.assertEqual(deployments[1]["id"], "deployment2")
        self.assertEqual(deployments[2]["id"], "deployment3")

    @responses.activate
    def test_delete_deployment_success(self):
        """Test successful deployment deletion."""
        deployment_id = "deployment1"
        deployment_url = f"{self.base_url}/deployments/{deployment_id}"
        
        # Mock the delete response
        responses.add(
            responses.DELETE,
            deployment_url,
            json={"success": True, "result": {"id": deployment_id}},
            status=200
        )
        
        # Override dry_run for this test
        self.deleter.dry_run = False
        
        # Call the method
        result = self.deleter.delete_deployment(deployment_id)
        
        # Validate the result
        self.assertTrue(result)

    @responses.activate
    def test_delete_deployment_failure(self):
        """Test failed deployment deletion."""
        deployment_id = "deployment1"
        deployment_url = f"{self.base_url}/deployments/{deployment_id}"
        
        # Mock the delete response for failure
        responses.add(
            responses.DELETE,
            deployment_url,
            json={"success": False, "errors": [{"code": 1000, "message": "Test error"}]},
            status=400
        )
        
        # Override dry_run for this test
        self.deleter.dry_run = False
        
        # Call the method
        result = self.deleter.delete_deployment(deployment_id)
        
        # Validate the result
        self.assertFalse(result)

    @responses.activate
    def test_delete_aliased_deployment(self):
        """Test deleting an aliased deployment."""
        deployment_id = "aliased_deployment"
        deployment_url = f"{self.base_url}/deployments/{deployment_id}"
        
        # Mock the delete response for an aliased deployment
        responses.add(
            responses.DELETE,
            deployment_url,
            json={
                "success": False, 
                "errors": [{"code": 8000035, "message": "Cannot delete aliased deployment"}]
            },
            status=400
        )
        
        # Override dry_run for this test
        self.deleter.dry_run = False
        
        # Call the method
        result = self.deleter.delete_deployment(deployment_id)
        
        # Validate the result - should fail without force
        self.assertFalse(result)
        
        # Now try with force flag
        self.deleter.force = True
        
        # Mock the forced delete URL (with force=true parameter)
        responses.add(
            responses.DELETE,
            f"{deployment_url}?force=true",
            json={"success": True, "result": {"id": deployment_id}},
            status=200
        )
        
        # Call the method again
        result = self.deleter.delete_deployment(deployment_id)
        
        # Validate the result - should succeed with force
        self.assertTrue(result)


class TestEnvFileLoading(unittest.TestCase):
    """Tests for the environment file loading functionality."""

    def test_load_env_file(self):
        """Test loading environment variables from a file."""
        # Create a temporary env file
        with open("test_env_file", "w") as f:
            f.write("# This is a comment\n")
            f.write("CF_API_TOKEN=test_token_from_file\n")
            f.write("CF_ACCOUNT_ID=account_id_from_file\n")
            f.write("\n")  # Empty line
            f.write("CF_PROJECT_NAME=project_name_from_file\n")
        
        # Load the file
        env_vars = load_env_file("test_env_file")
        
        # Verify loaded variables
        self.assertEqual(env_vars["CF_API_TOKEN"], "test_token_from_file")
        self.assertEqual(env_vars["CF_ACCOUNT_ID"], "account_id_from_file")
        self.assertEqual(env_vars["CF_PROJECT_NAME"], "project_name_from_file")
        
        # Clean up
        os.remove("test_env_file")

    def test_load_nonexistent_env_file(self):
        """Test loading from a nonexistent file."""
        # Load a file that doesn't exist
        env_vars = load_env_file("nonexistent_file")
        
        # Verify it returns an empty dict
        self.assertEqual(env_vars, {})


if __name__ == "__main__":
    unittest.main() 