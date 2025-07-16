"""
End-to-end authentication tests.

These tests verify the complete authentication flow including login, session persistence,
logout, and error handling scenarios across the entire application.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import yaml

from auth.app_wrapper import AppWrapper
from auth.authentication_manager import AuthenticationManager
from auth.config_manager import ConfigurationError, AuthenticationState


class TestAuthenticationE2E(unittest.TestCase):
    """End-to-end tests for authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_credentials.yaml")
        
        # Sample configuration with multiple users for testing
        self.test_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'name': 'Administrator',
                        'email': 'admin@example.com',
                        'password': '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri'  # 'password'
                    },
                    'user1': {
                        'name': 'User One',
                        'email': 'user1@example.com',
                        'password': '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri'  # 'password'
                    },
                    'testuser': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'password': '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri'  # 'password'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'test_signature_key_e2e',
                'name': 'test_auth_cookie_e2e'
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
    
    @patch('auth.app_wrapper.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_complete_authentication_flow(self, mock_authenticate, mock_st):
        """Test complete authentication flow from login to logout."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create app wrapper
        app_wrapper = AppWrapper(self.config_path)
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.rerun = MagicMock()
        
        # Phase 1: Initial unauthenticated state
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: None
        mock_st.session_state = mock_session_state
        
        # Mock login attempt (successful)
        mock_auth_instance.login.return_value = ('Test User', True, 'testuser')
        
        # Simulate login process
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=False):
            app_wrapper.main()
            
            # Verify login screen was displayed
            mock_st.title.assert_called_with("🍜 Kitchen Intel")
            mock_st.subheader.assert_called_with("Please login to access the application")
        
        # Phase 2: Successful authentication
        mock_session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock sidebar for authenticated state
        mock_sidebar = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_st.sidebar.__exit__ = MagicMock(return_value=None)
        mock_sidebar.write = MagicMock()
        mock_sidebar.markdown = MagicMock()
        mock_sidebar.button = MagicMock(return_value=False)  # Logout not clicked yet
        
        # Simulate authenticated state
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
            with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                    app_wrapper.main()
                    
                    # Verify authenticated app was rendered
                    mock_app_func.assert_called()
                    
                    # Verify user info displayed in sidebar
                    mock_sidebar.write.assert_any_call("👤 Logged in as: **Test User**")
                    mock_sidebar.write.assert_any_call("Username: testuser")
        
        # Phase 3: Logout process
        mock_sidebar.button.return_value = True  # Logout button clicked
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        
        with patch.object(app_wrapper.auth_manager, 'handle_logout') as mock_logout:
            with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
                with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                    with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                        app_wrapper.render_authenticated_app()
                        
                        # Verify logout was triggered
                        mock_logout.assert_called_once()
                        mock_st.rerun.assert_called()
        
        # Phase 4: Post-logout state (back to login screen)
        mock_session_state.get.side_effect = lambda key: None
        
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=False):
            app_wrapper.main()
            
            # Verify back to login screen
            self.assertTrue(mock_st.title.called)
            self.assertTrue(mock_st.subheader.called)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_session_persistence_across_page_refreshes(self, mock_authenticate, mock_st):
        """Test that authentication persists across page refreshes."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock persistent session state (simulating page refresh)
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # First check - should be authenticated
        self.assertTrue(auth_manager.is_authenticated())
        self.assertEqual(auth_manager.get_current_user(), 'testuser')
        self.assertEqual(auth_manager.get_current_user_name(), 'Test User')
        
        # Simulate page refresh (create new auth manager instance)
        auth_manager_refresh = AuthenticationManager(self.config_path)
        
        # Session state should persist
        self.assertTrue(auth_manager_refresh.is_authenticated())
        self.assertEqual(auth_manager_refresh.get_current_user(), 'testuser')
        self.assertEqual(auth_manager_refresh.get_current_user_name(), 'Test User')
        
        # Multiple refreshes should maintain authentication
        for i in range(3):
            auth_manager_new = AuthenticationManager(self.config_path)
            self.assertTrue(auth_manager_new.is_authenticated())
            self.assertEqual(auth_manager_new.get_current_user(), 'testuser')
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_authentication_with_multiple_user_accounts(self, mock_authenticate, mock_st):
        """Test authentication with different user accounts."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        mock_st.write = MagicMock()
        mock_st.error = MagicMock()
        mock_st.warning = MagicMock()
        
        # Test authentication with admin user
        mock_auth_instance.login.return_value = ('Administrator', True, 'admin')
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Administrator',
            'authentication_status': True,
            'username': 'admin'
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertTrue(auth_state.is_authenticated)
        self.assertEqual(auth_state.username, 'admin')
        self.assertEqual(auth_state.name, 'Administrator')
        
        # Test authentication with regular user
        mock_auth_instance.login.return_value = ('User One', True, 'user1')
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'User One',
            'authentication_status': True,
            'username': 'user1'
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertTrue(auth_state.is_authenticated)
        self.assertEqual(auth_state.username, 'user1')
        self.assertEqual(auth_state.name, 'User One')
        
        # Test authentication with test user
        mock_auth_instance.login.return_value = ('Test User', True, 'testuser')
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertTrue(auth_state.is_authenticated)
        self.assertEqual(auth_state.username, 'testuser')
        self.assertEqual(auth_state.name, 'Test User')
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_error_handling_scenarios(self, mock_authenticate, mock_st):
        """Test various error handling scenarios."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        mock_st.write = MagicMock()
        mock_st.error = MagicMock()
        mock_st.warning = MagicMock()
        
        # Test Case 1: Invalid credentials
        mock_auth_instance.login.return_value = (None, False, None)
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertFalse(auth_state.is_authenticated)
        mock_st.error.assert_called_with('Username/password is incorrect')
        
        # Test Case 2: Empty credentials
        mock_auth_instance.login.return_value = (None, None, None)
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': None,
            'username': None
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertFalse(auth_state.is_authenticated)
        mock_st.warning.assert_called_with('Please enter your username and password')
        
        # Test Case 3: Authentication service exception
        mock_auth_instance.login.side_effect = Exception("Service unavailable")
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        mock_st.session_state = mock_session_state
        
        auth_state = auth_manager.handle_login()
        self.assertFalse(auth_state.is_authenticated)
        mock_st.error.assert_called_with('An error occurred during login: Service unavailable')
        mock_session_state.__setitem__.assert_called_with('authentication_status', False)
    
    def test_configuration_error_handling(self):
        """Test handling of configuration errors."""
        # Test Case 1: Missing configuration file
        missing_config_path = os.path.join(self.temp_dir, "missing.yaml")
        
        with patch('auth.app_wrapper.st') as mock_st:
            mock_st.set_page_config = MagicMock()
            mock_st.title = MagicMock()
            mock_st.error = MagicMock()
            mock_st.info = MagicMock()
            
            app_wrapper = AppWrapper(missing_config_path)
            
            # Should create default config and proceed
            app_wrapper.main()
            
            # Verify page config was set
            mock_st.set_page_config.assert_called()
        
        # Test Case 2: Invalid YAML format
        invalid_config_path = os.path.join(self.temp_dir, "invalid.yaml")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: format: [")
        
        with patch('auth.app_wrapper.st') as mock_st:
            mock_st.set_page_config = MagicMock()
            mock_st.title = MagicMock()
            mock_st.error = MagicMock()
            mock_st.info = MagicMock()
            mock_st.expander = MagicMock()
            
            app_wrapper = AppWrapper(invalid_config_path)
            app_wrapper.main()
            
            # Verify error handling
            mock_st.error.assert_called()
            mock_st.info.assert_called()
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_cookie_expiration_handling(self, mock_authenticate, mock_st):
        """Test handling of expired authentication cookies."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock expired session state (authentication_status becomes None/False)
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': None,  # Expired/invalid
            'username': None
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Check authentication status - should be False for expired session
        self.assertFalse(auth_manager.is_authenticated())
        self.assertIsNone(auth_manager.get_current_user())
        self.assertIsNone(auth_manager.get_current_user_name())
        
        # User should need to re-authenticate
        auth_state = auth_manager.check_authentication()
        self.assertFalse(auth_state.is_authenticated)
        self.assertIsNone(auth_state.authentication_status)
    
    @patch('auth.app_wrapper.st')
    def test_app_wrapper_error_recovery(self, mock_st):
        """Test app wrapper error recovery mechanisms."""
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        mock_st.error = MagicMock()
        mock_st.info = MagicMock()
        
        # Test Case 1: Configuration error recovery
        invalid_config_path = os.path.join(self.temp_dir, "nonexistent.yaml")
        os.remove(self.config_path)  # Remove valid config
        
        app_wrapper = AppWrapper(invalid_config_path)
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Should handle missing config gracefully
        app_wrapper.main()
        
        # Verify error handling UI was displayed
        mock_st.set_page_config.assert_called()
        
        # Test Case 2: Unexpected exception handling
        with patch.object(app_wrapper.auth_manager, 'load_config', side_effect=Exception("Unexpected error")):
            app_wrapper.main()
            
            # Should handle unexpected errors gracefully
            mock_st.title.assert_called_with("🍜 Kitchen Intel")
            mock_st.error.assert_called()
            mock_st.info.assert_called()
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_concurrent_session_handling(self, mock_authenticate, mock_st):
        """Test handling of concurrent sessions (multiple auth manager instances)."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock shared session state
        shared_session_data = {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }
        
        mock_st.session_state.get.side_effect = lambda key: shared_session_data.get(key)
        
        # Create multiple authentication manager instances
        auth_manager1 = AuthenticationManager(self.config_path)
        auth_manager2 = AuthenticationManager(self.config_path)
        auth_manager3 = AuthenticationManager(self.config_path)
        
        # All should see the same authentication state
        self.assertTrue(auth_manager1.is_authenticated())
        self.assertTrue(auth_manager2.is_authenticated())
        self.assertTrue(auth_manager3.is_authenticated())
        
        self.assertEqual(auth_manager1.get_current_user(), 'testuser')
        self.assertEqual(auth_manager2.get_current_user(), 'testuser')
        self.assertEqual(auth_manager3.get_current_user(), 'testuser')
        
        # Simulate logout from one instance
        mock_session_state = MagicMock()
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        mock_st.session_state = mock_session_state
        mock_st.success = MagicMock()
        
        auth_manager1.handle_logout()
        
        # Verify logout was processed
        mock_auth_instance.logout.assert_called_with('Logout', 'sidebar')
        mock_session_state.__delitem__.assert_any_call('authentication_status')
        mock_session_state.__delitem__.assert_any_call('name')
        mock_session_state.__delitem__.assert_any_call('username')
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_requirements_validation(self, mock_authenticate, mock_st):
        """Test that all requirements are properly validated through E2E flow."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Create authentication manager
        auth_manager = AuthenticationManager(self.config_path)
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        mock_st.write = MagicMock()
        mock_st.error = MagicMock()
        mock_st.warning = MagicMock()
        
        # Requirement 1: Load credentials from YAML with hashed passwords
        config = auth_manager.load_config()
        self.assertIn('credentials', config)
        self.assertIn('usernames', config['credentials'])
        self.assertIn('cookie', config)
        
        # Verify hashed passwords
        for username, user_data in config['credentials']['usernames'].items():
            self.assertTrue(user_data['password'].startswith('$2b$'))  # bcrypt hash
        
        # Requirement 2: Display login form
        mock_auth_instance.login.return_value = (None, None, None)
        mock_st.session_state.get.side_effect = lambda key: None
        
        auth_state = auth_manager.handle_login()
        mock_auth_instance.login.assert_called_with('Login', 'main')
        mock_st.warning.assert_called_with('Please enter your username and password')
        
        # Requirement 3: Successful authentication and welcome message
        mock_auth_instance.login.return_value = ('Test User', True, 'testuser')
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertTrue(auth_state.is_authenticated)
        mock_st.success.assert_called_with('Welcome *Test User*')
        mock_st.write.assert_called_with('You are now logged in as Test User')
        
        # Requirement 4: Error messages for invalid credentials
        mock_auth_instance.login.return_value = (None, False, None)
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        auth_state = auth_manager.handle_login()
        self.assertFalse(auth_state.is_authenticated)
        mock_st.error.assert_called_with('Username/password is incorrect')
        
        # Requirement 5: Logout functionality
        mock_session_state = MagicMock()
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        mock_st.session_state = mock_session_state
        
        auth_manager.handle_logout()
        mock_auth_instance.logout.assert_called_with('Logout', 'sidebar')
        mock_st.success.assert_called_with('You have been logged out successfully')
        
        # Requirement 6: Session persistence
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Multiple checks should maintain authentication
        self.assertTrue(auth_manager.is_authenticated())
        self.assertTrue(auth_manager.is_authenticated())
        self.assertEqual(auth_manager.get_current_user(), 'testuser')


if __name__ == '__main__':
    unittest.main()