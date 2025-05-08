import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile

import responses

# Import modules to test
from deleter.src.delete_deployments import CloudflareDeploymentDeleter, main


class TestIntegration(unittest.TestCase):
    """Integration tests for the Cloudflare Pages Deployment Deleter."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Sample account and project
        self.account_id = "test_account_123"
        self.project_name = "test-project"
        self.api_token = "test_token_123"

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @responses.activate
    @patch('sys.argv', ['delete_deployments.py', '--account-id', 'test_account_123', 
                        '--project-name', 'test-project', '--token', 'test_token_123',
                        '--dry-run', '--verbose'])
    def test_end_to_end_dry_run(self):
        """Test end-to-end process in dry run mode."""
        # Mock the API calls
        base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects/{self.project_name}"
        
        # Mock the deployments endpoint
        mock_deployments = {
            "success": True,
            "result": [
                {"id": "deployment1", "name": "Test Deployment 1", "environment": "production"},
                {"id": "deployment2", "name": "Test Deployment 2", "environment": "preview"},
                {"id": "deployment3", "name": "Test Deployment 3", "environment": "preview"}
            ],
            "result_info": {
                "page": 1,
                "per_page": 25,
                "total_count": 3,
                "total_pages": 1
            }
        }
        
        responses.add(
            responses.GET,
            f"{base_url}/deployments?page=1&per_page=25",
            json=mock_deployments,
            status=200
        )
        
        # Run the main function (dry run mode)
        with patch('sys.stdout') as mock_stdout:
            main()
            
            # Verify the output contains expected messages
            output = ''.join(call.args[0] for call in mock_stdout.write.call_args_list)
            self.assertIn("DRY RUN mode enabled", output)
            self.assertIn("Found 3 deployments", output)
            # In dry run mode, it should not actually try to delete anything
            self.assertIn("[DRY RUN] Would delete deployment", output)

    @responses.activate
    @patch('sys.argv', ['delete_deployments.py', '--account-id', 'test_account_123', 
                        '--project-name', 'test-project', '--token', 'test_token_123'])
    def test_end_to_end_with_real_deletes(self):
        """Test end-to-end process with actual deletions."""
        # Mock the API calls
        base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/pages/projects/{self.project_name}"
        
        # Mock the deployments endpoint
        mock_deployments = {
            "success": True,
            "result": [
                {"id": "deployment1", "name": "Test Deployment 1", "environment": "production"},
                {"id": "deployment2", "name": "Test Deployment 2", "environment": "preview"},
                {"id": "deployment3", "name": "Test Deployment 3", "environment": "preview"}
            ],
            "result_info": {
                "page": 1,
                "per_page": 25,
                "total_count": 3,
                "total_pages": 1
            }
        }
        
        responses.add(
            responses.GET,
            f"{base_url}/deployments?page=1&per_page=25",
            json=mock_deployments,
            status=200
        )
        
        # Mock delete responses
        for i in range(1, 4):
            responses.add(
                responses.DELETE,
                f"{base_url}/deployments/deployment{i}",
                json={"success": True, "result": {"id": f"deployment{i}"}},
                status=200
            )
        
        # Run the main function
        with patch('sys.stdout') as mock_stdout:
            main()
            
            # Verify the output contains expected messages
            output = ''.join(call.args[0] for call in mock_stdout.write.call_args_list)
            self.assertIn("Found 3 deployments", output)
            self.assertIn("Deleted 3", output)
            self.assertIn("100%", output)  # Should show 100% completion

    @responses.activate
    def test_env_file_integration(self):
        """Test integration with environment file loading."""
        # Create a temporary env file
        env_file_path = os.path.join(self.temp_dir.name, 'test_envfile')
        with open(env_file_path, 'w') as f:
            f.write("CF_ACCOUNT_ID=file_account_id\n")
            f.write("CF_PROJECT_NAME=file_project_name\n")
            f.write("CF_API_TOKEN=file_api_token\n")
        
        # Mock the API calls
        base_url = "https://api.cloudflare.com/client/v4/accounts/file_account_id/pages/projects/file_project_name"
        
        # Mock the deployments endpoint
        mock_deployments = {
            "success": True,
            "result": [
                {"id": "deployment1", "name": "Test Deployment 1", "environment": "production"},
            ],
            "result_info": {
                "page": 1,
                "per_page": 25,
                "total_count": 1,
                "total_pages": 1
            }
        }
        
        responses.add(
            responses.GET,
            f"{base_url}/deployments?page=1&per_page=25",
            json=mock_deployments,
            status=200
        )
        
        # Mock delete response
        responses.add(
            responses.DELETE,
            f"{base_url}/deployments/deployment1",
            json={"success": True, "result": {"id": "deployment1"}},
            status=200
        )
        
        # Run the main function with env file
        with patch('sys.argv', ['delete_deployments.py', '--env-file', env_file_path, '--dry-run']):
            with patch('sys.stdout') as mock_stdout:
                main()
                
                # Verify the output contains expected messages
                output = ''.join(call.args[0] for call in mock_stdout.write.call_args_list)
                self.assertIn("Found 1 deployments", output)


if __name__ == "__main__":
    unittest.main() 