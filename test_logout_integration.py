"""
Integration tests for logout functionality.

These tests verify the complete logout flow including session cleanup
and proper redirection behavior.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import yaml

from auth.authentication_manager import AuthenticationManager
from auth.app_wrapper import AppWrapper


class TestLogoutIntegration(unittest.TestCase):
    """Integration tests for logout functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_credentials.yaml")
        
        # Sample configuration for testing
        self.test_config = {
            'credentials': {
                'usernames': {
                    'testuser': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'password': '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'test_signature_key',
                'name': 'test_auth_cookie'
            }
        }
        
        # Write test config to file
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_complete_logout_flow(self, mock_authenticate, mock_st):
        """Test complete logout flow from authenticated state to logged out."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock initial authenticated session state
        mock_session_state = MagicMock()
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        mock_session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        
        # Verify user is initially authenticated
        self.assertTrue(auth_manager.is_authenticated())
        self.assertEqual(auth_manager.get_current_user(), 'testuser')
        self.assertEqual(auth_manager.get_current_user_name(), 'Test User')
        
        # Perform logout
        auth_manager.handle_logout()
        
        # Verify logout method was called
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
        
        # Verify session state was cleared
        mock_session_state.__delitem__.assert_any_call('authentication_status')
        mock_session_state.__delitem__.assert_any_call('name')
        mock_session_state.__delitem__.assert_any_call('username')
        
        # Verify success message was displayed
        mock_st.success.assert_called_once_with('You have been logged out successfully')
        
        # Mock post-logout session state (cleared)
        mock_session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Verify user is no longer authenticated
        self.assertFalse(auth_manager.is_authenticated())
        self.assertIsNone(auth_manager.get_current_user())
        self.assertIsNone(auth_manager.get_current_user_name())
    
    @patch('auth.app_wrapper.st')
    def test_app_wrapper_logout_integration(self, mock_st):
        """Test logout integration with AppWrapper."""
        # Create app wrapper
        app_wrapper = AppWrapper(self.config_path)
        
        # Mock authenticated session state
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        mock_st.write = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.button = MagicMock(return_value=True)  # Simulate logout button click
        mock_st.sidebar = MagicMock()
        mock_st.rerun = MagicMock()
        
        # Mock the authenticated app function
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock the authentication manager's logout method
        with patch.object(app_wrapper.auth_manager, 'handle_logout') as mock_logout:
            with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
                with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                    with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                        # Render authenticated app (which should trigger logout when button is clicked)
                        app_wrapper.render_authenticated_app()
                        
                        # Verify logout was called
                        mock_logout.assert_called_once()
                        
                        # Verify rerun was called to refresh the page
                        mock_st.rerun.assert_called()
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_logout_session_cleanup_verification(self, mock_authenticate, mock_st):
        """Test that logout properly cleans up all session variables."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock session state with various authentication-related variables
        mock_session_state = MagicMock()
        session_vars = {
            'authentication_status': True,
            'name': 'Test User',
            'username': 'testuser',
            'other_var': 'should_remain'  # Non-auth variable should remain
        }
        
        mock_session_state.__contains__.side_effect = lambda key: key in session_vars
        mock_session_state.get.side_effect = lambda key: session_vars.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        
        # Perform logout
        auth_manager.handle_logout()
        
        # Verify only authentication-related variables were cleared
        expected_deletions = ['authentication_status', 'name', 'username']
        actual_deletions = [call[0][0] for call in mock_session_state.__delitem__.call_args_list]
        
        for var in expected_deletions:
            self.assertIn(var, actual_deletions)
        
        # Verify non-auth variables were not touched
        self.assertNotIn('other_var', actual_deletions)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_logout_error_recovery(self, mock_authenticate, mock_st):
        """Test logout error recovery and fallback session clearing."""
        # Mock authenticator instance that raises an exception
        mock_auth_instance = MagicMock()
        mock_auth_instance.logout.side_effect = Exception("Logout service unavailable")
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.error = MagicMock()
        
        # Perform logout (should handle exception gracefully)
        auth_manager.handle_logout()
        
        # Verify error was displayed
        mock_st.error.assert_called_once_with('An error occurred during logout: Logout service unavailable')
        
        # Verify fallback session clearing was performed
        mock_session_state.clear.assert_called_once()
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_logout_redirects_to_login_screen(self, mock_authenticate, mock_st):
        """Test that logout properly redirects user to login screen."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_session_state.__contains__.return_value = True
        mock_st.session_state = mock_session_state
        mock_st.success = MagicMock()
        
        # Perform logout
        auth_manager.handle_logout()
        
        # Verify logout was called
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
        
        # Verify success message indicates successful logout
        mock_st.success.assert_called_once_with('You have been logged out successfully')
        
        # Mock post-logout state check
        mock_session_state.get.side_effect = lambda key: None
        
        # Verify user is no longer authenticated (would trigger redirect to login)
        self.assertFalse(auth_manager.is_authenticated())
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_multiple_logout_attempts(self, mock_authenticate, mock_st):
        """Test handling of multiple logout attempts."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state
        mock_st.success = MagicMock()
        
        # First logout attempt
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        auth_manager.handle_logout()
        
        # Verify first logout
        self.assertEqual(mock_auth_instance.logout.call_count, 1)
        self.assertEqual(mock_st.success.call_count, 1)
        
        # Second logout attempt (session already cleared)
        mock_session_state.__contains__.side_effect = lambda key: False
        auth_manager.handle_logout()
        
        # Verify second logout was also handled gracefully
        self.assertEqual(mock_auth_instance.logout.call_count, 2)
        self.assertEqual(mock_st.success.call_count, 2)


if __name__ == '__main__':
    unittest.main()