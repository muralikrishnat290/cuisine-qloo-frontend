"""
Unit tests for authentication manager.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import yaml

from auth.authentication_manager import AuthenticationManager
from auth.config_manager import ConfigurationError, AuthenticationState


class TestAuthenticationManager(unittest.TestCase):
    """Test cases for AuthenticationManager class."""
    
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
                    },
                    'admin': {
                        'name': 'Administrator',
                        'email': 'admin@example.com',
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
        
        self.auth_manager = AuthenticationManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test AuthenticationManager initialization."""
        self.assertEqual(self.auth_manager.config_path, self.config_path)
        self.assertIsNotNone(self.auth_manager.config_manager)
        self.assertIsNone(self.auth_manager.authenticator)
        self.assertFalse(self.auth_manager._config_loaded)
    
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config = self.auth_manager.load_config()
        
        self.assertEqual(config, self.test_config)
        self.assertTrue(self.auth_manager._config_loaded)
    
    def test_load_config_missing_file(self):
        """Test configuration loading with missing file."""
        # Create auth manager with non-existent file
        missing_path = os.path.join(self.temp_dir, "missing.yaml")
        auth_manager = AuthenticationManager(missing_path)
        
        # Should create default config and load it
        config = auth_manager.load_config()
        
        self.assertIsNotNone(config)
        self.assertTrue(auth_manager._config_loaded)
        self.assertTrue(os.path.exists(missing_path))
    
    def test_load_config_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        # Write invalid YAML to file
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with self.assertRaises(ConfigurationError):
            self.auth_manager.load_config()
    
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_initialize_authenticator_success(self, mock_authenticate):
        """Test successful authenticator initialization."""
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Load config first
        self.auth_manager.load_config()
        
        # Initialize authenticator
        authenticator = self.auth_manager.initialize_authenticator()
        
        self.assertEqual(authenticator, mock_auth_instance)
        self.assertEqual(self.auth_manager.authenticator, mock_auth_instance)
        
        # Verify authenticate was called with correct parameters
        mock_authenticate.assert_called_once()
        call_args = mock_authenticate.call_args[0]
        
        # Check credentials structure
        credentials = call_args[0]
        self.assertIn('usernames', credentials)
        self.assertIn('testuser', credentials['usernames'])
        self.assertIn('admin', credentials['usernames'])
        
        # Check cookie parameters
        self.assertEqual(call_args[1], 'test_auth_cookie')  # cookie name
        self.assertEqual(call_args[2], 'test_signature_key')  # cookie key
        self.assertEqual(call_args[3], 30)  # expiry days
    
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_initialize_authenticator_without_config(self, mock_authenticate):
        """Test authenticator initialization without loading config first."""
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Initialize authenticator without loading config first
        authenticator = self.auth_manager.initialize_authenticator()
        
        self.assertEqual(authenticator, mock_auth_instance)
        self.assertTrue(self.auth_manager._config_loaded)
    
    @patch('auth.authentication_manager.st')
    def test_check_authentication_authenticated(self, mock_st):
        """Test check_authentication with authenticated user."""
        # Mock session state with authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        auth_state = self.auth_manager.check_authentication()
        
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertEqual(auth_state.name, 'Test User')
        self.assertTrue(auth_state.authentication_status)
        self.assertEqual(auth_state.username, 'testuser')
        self.assertTrue(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    def test_check_authentication_not_authenticated(self, mock_st):
        """Test check_authentication with non-authenticated user."""
        # Mock session state with non-authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        auth_state = self.auth_manager.check_authentication()
        
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertIsNone(auth_state.name)
        self.assertFalse(auth_state.authentication_status)
        self.assertIsNone(auth_state.username)
        self.assertFalse(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_check_authentication_initializes_authenticator(self, mock_authenticate, mock_st):
        """Test that check_authentication initializes authenticator if needed."""
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock session state
        mock_st.session_state.get.return_value = None
        
        # Ensure authenticator is None
        self.auth_manager.authenticator = None
        
        auth_state = self.auth_manager.check_authentication()
        
        # Should have initialized authenticator
        self.assertEqual(self.auth_manager.authenticator, mock_auth_instance)
        self.assertIsInstance(auth_state, AuthenticationState)
    
    @patch('auth.authentication_manager.st')
    def test_is_authenticated_true(self, mock_st):
        """Test is_authenticated returns True for authenticated user."""
        # Mock session state with authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertTrue(self.auth_manager.is_authenticated())
    
    @patch('auth.authentication_manager.st')
    def test_is_authenticated_false(self, mock_st):
        """Test is_authenticated returns False for non-authenticated user."""
        # Mock session state with non-authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertFalse(self.auth_manager.is_authenticated())
    
    @patch('auth.authentication_manager.st')
    def test_get_current_user_authenticated(self, mock_st):
        """Test get_current_user returns username for authenticated user."""
        # Mock session state with authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertEqual(self.auth_manager.get_current_user(), 'testuser')
    
    @patch('auth.authentication_manager.st')
    def test_get_current_user_not_authenticated(self, mock_st):
        """Test get_current_user returns None for non-authenticated user."""
        # Mock session state with non-authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertIsNone(self.auth_manager.get_current_user())
    
    @patch('auth.authentication_manager.st')
    def test_get_current_user_name_authenticated(self, mock_st):
        """Test get_current_user_name returns display name for authenticated user."""
        # Mock session state with authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertEqual(self.auth_manager.get_current_user_name(), 'Test User')
    
    @patch('auth.authentication_manager.st')
    def test_get_current_user_name_not_authenticated(self, mock_st):
        """Test get_current_user_name returns None for non-authenticated user."""
        # Mock session state with non-authenticated user
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Mock authenticator
        self.auth_manager.authenticator = MagicMock()
        
        self.assertIsNone(self.auth_manager.get_current_user_name())
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_login_successful_authentication(self, mock_authenticate, mock_st):
        """Test handle_login with successful authentication."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock successful login response
        mock_auth_instance.login.return_value = ('Test User', True, 'testuser')
        
        # Mock session state for check_authentication
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        mock_st.write = MagicMock()
        
        # Execute handle_login
        auth_state = self.auth_manager.handle_login()
        
        # Verify authenticator.login was called
        mock_auth_instance.login.assert_called_once_with('Login', 'main')
        
        # Verify success messages were displayed
        mock_st.success.assert_called_once_with('Welcome *Test User*')
        mock_st.write.assert_called_once_with('You are now logged in as Test User')
        
        # Verify authentication state
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertEqual(auth_state.name, 'Test User')
        self.assertTrue(auth_state.authentication_status)
        self.assertEqual(auth_state.username, 'testuser')
        self.assertTrue(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_login_invalid_credentials(self, mock_authenticate, mock_st):
        """Test handle_login with invalid credentials."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock failed login response (invalid credentials)
        mock_auth_instance.login.return_value = (None, False, None)
        
        # Mock session state for check_authentication
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        
        # Mock streamlit UI methods
        mock_st.error = MagicMock()
        
        # Execute handle_login
        auth_state = self.auth_manager.handle_login()
        
        # Verify authenticator.login was called
        mock_auth_instance.login.assert_called_once_with('Login', 'main')
        
        # Verify error message was displayed
        mock_st.error.assert_called_once_with('Username/password is incorrect')
        
        # Verify authentication state
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertIsNone(auth_state.name)
        self.assertFalse(auth_state.authentication_status)
        self.assertIsNone(auth_state.username)
        self.assertFalse(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_login_empty_credentials(self, mock_authenticate, mock_st):
        """Test handle_login with empty credentials."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock empty credentials response
        mock_auth_instance.login.return_value = (None, None, None)
        
        # Mock session state for check_authentication
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': None,
            'username': None
        }.get(key)
        
        # Mock streamlit UI methods
        mock_st.warning = MagicMock()
        
        # Execute handle_login
        auth_state = self.auth_manager.handle_login()
        
        # Verify authenticator.login was called
        mock_auth_instance.login.assert_called_once_with('Login', 'main')
        
        # Verify warning message was displayed
        mock_st.warning.assert_called_once_with('Please enter your username and password')
        
        # Verify authentication state
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertIsNone(auth_state.name)
        self.assertIsNone(auth_state.authentication_status)
        self.assertIsNone(auth_state.username)
        self.assertFalse(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_login_exception_handling(self, mock_authenticate, mock_st):
        """Test handle_login with exception during authentication."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock exception during login
        mock_auth_instance.login.side_effect = Exception("Authentication service error")
        
        # Mock session state for check_authentication
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.error = MagicMock()
        
        # Execute handle_login
        auth_state = self.auth_manager.handle_login()
        
        # Verify authenticator.login was called
        mock_auth_instance.login.assert_called_once_with('Login', 'main')
        
        # Verify error message was displayed
        mock_st.error.assert_called_once_with('An error occurred during login: Authentication service error')
        
        # Verify authentication status was set to False in session state
        mock_session_state.__setitem__.assert_called_with('authentication_status', False)
        
        # Verify authentication state
        self.assertIsInstance(auth_state, AuthenticationState)
        self.assertFalse(auth_state.is_authenticated)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_login_initializes_authenticator(self, mock_authenticate, mock_st):
        """Test that handle_login initializes authenticator if needed."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock login response
        mock_auth_instance.login.return_value = (None, None, None)
        
        # Mock session state
        mock_st.session_state.get.return_value = None
        mock_st.warning = MagicMock()
        
        # Ensure authenticator is None
        self.auth_manager.authenticator = None
        
        # Execute handle_login
        auth_state = self.auth_manager.handle_login()
        
        # Should have initialized authenticator
        self.assertEqual(self.auth_manager.authenticator, mock_auth_instance)
        
        # Should have called login
        mock_auth_instance.login.assert_called_once_with('Login', 'main')
        
        # Verify authentication state is returned
        self.assertIsInstance(auth_state, AuthenticationState)
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_logout_successful(self, mock_authenticate, mock_st):
        """Test handle_logout with successful logout."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock session state with authenticated user
        mock_session_state = MagicMock()
        mock_session_state.__contains__.side_effect = lambda key: key in [
            'authentication_status', 'name', 'username'
        ]
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        
        # Set up authenticator
        self.auth_manager.authenticator = mock_auth_instance
        
        # Execute handle_logout
        self.auth_manager.handle_logout()
        
        # Verify authenticator.logout was called
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
        
        # Verify session state variables were cleared
        mock_session_state.__delitem__.assert_any_call('authentication_status')
        mock_session_state.__delitem__.assert_any_call('name')
        mock_session_state.__delitem__.assert_any_call('username')
        
        # Verify success message was displayed
        mock_st.success.assert_called_once_with('You have been logged out successfully')
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_logout_initializes_authenticator(self, mock_authenticate, mock_st):
        """Test that handle_logout initializes authenticator if needed."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_session_state.__contains__.return_value = False
        mock_st.session_state = mock_session_state
        mock_st.success = MagicMock()
        
        # Ensure authenticator is None
        self.auth_manager.authenticator = None
        
        # Execute handle_logout
        self.auth_manager.handle_logout()
        
        # Should have initialized authenticator
        self.assertEqual(self.auth_manager.authenticator, mock_auth_instance)
        
        # Should have called logout
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
    
    @patch('auth.authentication_manager.st')
    @patch('auth.authentication_manager.stauth.Authenticate')
    def test_handle_logout_exception_handling(self, mock_authenticate, mock_st):
        """Test handle_logout with exception during logout."""
        # Mock authenticator instance
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Mock exception during logout
        mock_auth_instance.logout.side_effect = Exception("Logout service error")
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.error = MagicMock()
        
        # Set up authenticator
        self.auth_manager.authenticator = mock_auth_instance
        
        # Execute handle_logout
        self.auth_manager.handle_logout()
        
        # Verify authenticator.logout was called
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
        
        # Verify error message was displayed
        mock_st.error.assert_called_once_with('An error occurred during logout: Logout service error')
        
        # Verify session state was cleared as fallback
        mock_session_state.clear.assert_called_once()
    
    @patch('auth.authentication_manager.st')
    def test_handle_logout_partial_session_state(self, mock_st):
        """Test handle_logout with partial session state variables."""
        # Mock authenticator
        mock_auth_instance = MagicMock()
        self.auth_manager.authenticator = mock_auth_instance
        
        # Mock session state with only some variables present
        mock_session_state = MagicMock()
        mock_session_state.__contains__.side_effect = lambda key: key in ['name', 'username']
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.success = MagicMock()
        
        # Execute handle_logout
        self.auth_manager.handle_logout()
        
        # Verify authenticator.logout was called
        mock_auth_instance.logout.assert_called_once_with('Logout', 'sidebar')
        
        # Verify only existing session state variables were cleared
        mock_session_state.__delitem__.assert_any_call('name')
        mock_session_state.__delitem__.assert_any_call('username')
        
        # authentication_status should not be deleted since it's not present
        calls = [call[0][0] for call in mock_session_state.__delitem__.call_args_list]
        self.assertNotIn('authentication_status', calls)
        
        # Verify success message was displayed
        mock_st.success.assert_called_once_with('You have been logged out successfully')


if __name__ == '__main__':
    unittest.main()