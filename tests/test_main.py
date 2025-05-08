import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import responses

from deleter.src.delete_deployments import main


class TestMain(unittest.TestCase):
    """Tests for the main function."""

    @patch('deleter.src.delete_deployments.CloudflareDeploymentDeleter')
    @patch('sys.argv', ['delete_deployments.py', '--account-id', 'test_account', '--project-name', 'test_project', '--token', 'test_token', '--dry-run'])
    def test_main_with_args(self, mock_deleter):
        """Test the main function with command line arguments."""
        # Setup the mock
        mock_instance = MagicMock()
        mock_deleter.return_value = mock_instance
        
        # Run the main function
        main()
        
        # Verify the deleter was created with correct parameters
        mock_deleter.assert_called_once_with(
            account_id='test_account',
            project_name='test_project',
            api_token='test_token',
            email=None,
            api_key=None,
            env=None,
            dry_run=True,
            verbose=False,
            force=False,
            limit=50
        )
        
        # Verify the run method was called
        mock_instance.run.assert_called_once()

    @patch('deleter.src.delete_deployments.CloudflareDeploymentDeleter')
    @patch('os.environ', {
        'CF_ACCOUNT_ID': 'env_account',
        'CF_PROJECT_NAME': 'env_project',
        'CF_API_TOKEN': 'env_token'
    })
    @patch('sys.argv', ['delete_deployments.py'])
    def test_main_with_env_vars(self, mock_deleter):
        """Test the main function with environment variables."""
        # Setup the mock
        mock_instance = MagicMock()
        mock_deleter.return_value = mock_instance
        
        # Run the main function
        main()
        
        # Verify the deleter was created with correct parameters
        mock_deleter.assert_called_once_with(
            account_id='env_account',
            project_name='env_project',
            api_token='env_token',
            email=None,
            api_key=None,
            env=None,
            dry_run=False,
            verbose=False,
            force=False,
            limit=50
        )
        
        # Verify the run method was called
        mock_instance.run.assert_called_once()

    @patch('deleter.src.delete_deployments.load_env_file')
    @patch('deleter.src.delete_deployments.CloudflareDeploymentDeleter')
    @patch('sys.argv', ['delete_deployments.py', '--env-file', 'test_env_file'])
    def test_main_with_env_file(self, mock_deleter, mock_load_env_file):
        """Test the main function with an environment file."""
        # Setup the mocks
        mock_instance = MagicMock()
        mock_deleter.return_value = mock_instance
        
        # Mock the environment file loading
        mock_load_env_file.return_value = {
            'CF_ACCOUNT_ID': 'file_account',
            'CF_PROJECT_NAME': 'file_project',
            'CF_API_TOKEN': 'file_token'
        }
        
        # Run the main function
        main()
        
        # Verify env file was loaded
        mock_load_env_file.assert_called_once_with('test_env_file')
        
        # Verify the deleter was created with correct parameters
        mock_deleter.assert_called_once_with(
            account_id='file_account',
            project_name='file_project',
            api_token='file_token',
            email=None,
            api_key=None,
            env=None,
            dry_run=False,
            verbose=False,
            force=False,
            limit=50
        )
        
        # Verify the run method was called
        mock_instance.run.assert_called_once()

    @patch('sys.exit')
    @patch('sys.argv', ['delete_deployments.py'])  # No args, no env vars
    def test_main_missing_required_args(self, mock_exit):
        """Test the main function with missing required arguments."""
        # Clean environment for test
        with patch.dict(os.environ, {}, clear=True):
            # Run the main function
            main()
            
            # Verify sys.exit was called with error code
            mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main() 