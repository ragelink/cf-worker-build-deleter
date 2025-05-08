import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Use sys.path manipulation to import the wrapper script
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import delete_deployments


class TestWrapper(unittest.TestCase):
    """Tests for the wrapper script."""

    @patch('delete_deployments.os.path.dirname')
    @patch('delete_deployments.os.path.abspath')
    @patch('delete_deployments.os.path.join')
    @patch('delete_deployments.sys.path.insert')
    @patch('delete_deployments.os.path.isabs')
    @patch('delete_deployments.os.path.abspath')
    @patch('delete_deployments.main')
    def test_main_wrapper(self, mock_main, mock_abspath, mock_isabs, mock_insert, mock_join, mock_dir_abspath, mock_dirname):
        """Test the main wrapper function."""
        # Setup the mocks
        mock_dirname.return_value = '/fake/path'
        mock_dir_abspath.return_value = '/fake/abs/path'
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_isabs.return_value = True  # Simulate absolute path
        
        # Setup system arguments
        with patch('sys.argv', ['delete_deployments.py', '--account-id', 'test_account']):
            # Call the wrapper function
            delete_deployments.main_wrapper()
            
            # Verify sys.path was manipulated
            self.assertTrue(mock_insert.called)
            
            # Verify main was called
            mock_main.assert_called_once()

    @patch('delete_deployments.os.path.dirname')
    @patch('delete_deployments.os.path.abspath')
    @patch('delete_deployments.os.path.join')
    @patch('delete_deployments.sys.path.insert')
    @patch('delete_deployments.os.path.isabs')
    @patch('delete_deployments.os.path.abspath')
    def test_env_file_path_conversion(self, mock_abspath, mock_isabs, mock_insert, mock_join, mock_dir_abspath, mock_dirname):
        """Test the conversion of relative env file paths to absolute paths."""
        # Setup the mocks
        mock_dirname.return_value = '/fake/path'
        mock_dir_abspath.return_value = '/fake/abs/path'
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_isabs.return_value = False  # Simulate relative path
        mock_abspath.return_value = '/fake/abs/env/file/path'
        
        # Setup system arguments with a relative env file path
        with patch('sys.argv', ['delete_deployments.py', '--env-file', 'relative/path/to/envfile']):
            # Patch the import and main function calls
            with patch('delete_deployments.main'):
                # Call the wrapper function
                delete_deployments.main_wrapper()
                
                # Verify the path was converted to absolute
                mock_isabs.assert_called_with('relative/path/to/envfile')
                mock_abspath.assert_called_with('relative/path/to/envfile')
                
                # Check that sys.argv was updated
                self.assertEqual(sys.argv[1], '--env-file')
                self.assertEqual(sys.argv[2], '/fake/abs/env/file/path')

    @patch('delete_deployments.os.path.dirname')
    @patch('delete_deployments.os.path.abspath')
    @patch('delete_deployments.os.path.join')
    @patch('delete_deployments.sys.path.insert')
    @patch('delete_deployments.os.path.isabs')
    @patch('delete_deployments.print')
    @patch('delete_deployments.sys.exit')
    def test_import_error_handling(self, mock_exit, mock_print, mock_isabs, mock_insert, mock_join, mock_dir_abspath, mock_dirname):
        """Test handling of import errors."""
        # Setup the mocks
        mock_dirname.return_value = '/fake/path'
        mock_dir_abspath.return_value = '/fake/abs/path'
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_isabs.return_value = True
        
        # Simulate import errors for all import paths
        with patch('delete_deployments.sys.path.insert'):
            # First, make the preferred import fail
            with patch('delete_deployments.__import__', side_effect=ImportError("Test error")):
                # Then make the direct import fail
                with patch('delete_deployments.__builtins__.__import__', side_effect=ImportError("Test error")):
                    # Finally make the legacy import fail
                    with patch('delete_deployments.__builtins__.__import__', side_effect=ImportError("Test error")):
                        # Call the wrapper function
                        delete_deployments.main_wrapper()
                        
                        # Verify error was printed and exit was called
                        self.assertTrue(mock_print.called)
                        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main() 