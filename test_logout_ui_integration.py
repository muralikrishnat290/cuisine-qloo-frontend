"""
UI Integration tests for logout functionality.

These tests verify the logout button behavior and UI flow.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
import yaml

from auth.app_wrapper import AppWrapper


class TestLogoutUIIntegration(unittest.TestCase):
    """UI integration tests for logout functionality."""
    
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
    
    @patch('auth.app_wrapper.st')
    def test_logout_button_display_for_authenticated_user(self, mock_st):
        """Test that logout button is displayed for authenticated users."""
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
        
        # Mock sidebar context manager
        mock_sidebar_context = MagicMock()
        mock_st.sidebar = mock_sidebar_context
        mock_sidebar_context.__enter__ = MagicMock(return_value=mock_sidebar_context)
        mock_sidebar_context.__exit__ = MagicMock(return_value=None)
        mock_sidebar_context.write = MagicMock()
        mock_sidebar_context.markdown = MagicMock()
        mock_sidebar_context.button = MagicMock(return_value=False)  # Button not clicked
        
        # Mock the authenticated app function
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock authentication manager methods
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
            with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                    # Render authenticated app
                    app_wrapper.render_authenticated_app()
                    
                    # Verify user info is displayed in sidebar
                    mock_sidebar_context.write.assert_any_call("👤 Logged in as: **Test User**")
                    mock_sidebar_context.write.assert_any_call("Username: testuser")
                    
                    # Verify logout button is displayed
                    mock_sidebar_context.button.assert_called_with(
                        "🚪 Logout", 
                        type="secondary", 
                        use_container_width=True
                    )
                    
                    # Verify main app function was called
                    mock_app_func.assert_called_once()
    
    @patch('auth.app_wrapper.st')
    def test_logout_button_click_triggers_logout(self, mock_st):
        """Test that clicking logout button triggers logout process."""
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
        mock_st.button = MagicMock(return_value=True)  # Button clicked
        mock_st.rerun = MagicMock()
        
        # Mock sidebar context manager
        mock_sidebar = MagicMock()
        mock_st.sidebar = mock_sidebar
        mock_sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_sidebar.__exit__ = MagicMock(return_value=None)
        mock_sidebar.write = MagicMock()
        mock_sidebar.markdown = MagicMock()
        mock_sidebar.button = MagicMock(return_value=True)  # Logout button clicked
        
        # Mock the authenticated app function
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock authentication manager methods
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
            with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                    with patch.object(app_wrapper.auth_manager, 'handle_logout') as mock_logout:
                        # Render authenticated app
                        app_wrapper.render_authenticated_app()
                        
                        # Verify logout was called
                        mock_logout.assert_called_once()
                        
                        # Verify page rerun was triggered
                        mock_st.rerun.assert_called_once()
    
    @patch('auth.app_wrapper.st')
    def test_logout_button_not_displayed_for_unauthenticated_user(self, mock_st):
        """Test that logout button is not displayed for unauthenticated users."""
        # Create app wrapper
        app_wrapper = AppWrapper(self.config_path)
        
        # Mock unauthenticated session state
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        mock_st.subheader = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.rerun = MagicMock()
        
        # Mock authentication manager methods
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=False):
            with patch.object(app_wrapper.auth_manager, 'handle_login') as mock_login:
                # Mock login returns unauthenticated state
                from auth.config_manager import AuthenticationState
                mock_login.return_value = AuthenticationState(
                    name=None, 
                    authentication_status=False, 
                    username=None
                )
                
                # Render login screen
                app_wrapper.render_login_screen()
                
                # Verify login screen elements are displayed
                mock_st.title.assert_called_with("🍜 Kitchen Intel")
                mock_st.subheader.assert_called_with("Please login to access the application")
                
                # Verify login handler was called
                mock_login.assert_called_once()
                
                # Verify no logout button was displayed (sidebar not used)
                mock_st.sidebar.assert_not_called() if hasattr(mock_st, 'sidebar') else None
    
    @patch('auth.app_wrapper.st')
    def test_user_info_display_in_sidebar(self, mock_st):
        """Test that user information is properly displayed in sidebar."""
        # Create app wrapper
        app_wrapper = AppWrapper(self.config_path)
        
        # Mock authenticated session state
        mock_session_state = MagicMock()
        mock_session_state.get.side_effect = lambda key: {
            'name': 'John Doe',
            'authentication_status': True,
            'username': 'johndoe'
        }.get(key)
        mock_st.session_state = mock_session_state
        
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        
        # Mock sidebar context manager
        mock_sidebar_context = MagicMock()
        mock_st.sidebar = mock_sidebar_context
        mock_sidebar_context.__enter__ = MagicMock(return_value=mock_sidebar_context)
        mock_sidebar_context.__exit__ = MagicMock(return_value=None)
        mock_sidebar_context.write = MagicMock()
        mock_sidebar_context.markdown = MagicMock()
        mock_sidebar_context.button = MagicMock(return_value=False)
        
        # Mock the authenticated app function
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock authentication manager methods
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
            with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='John Doe'):
                with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='johndoe'):
                    # Render authenticated app
                    app_wrapper.render_authenticated_app()
                    
                    # Verify user information is displayed correctly
                    expected_calls = [
                        call("👤 Logged in as: **John Doe**"),
                        call("Username: johndoe")
                    ]
                    mock_sidebar_context.write.assert_has_calls(expected_calls, any_order=False)
                    
                    # Verify separator is displayed
                    mock_sidebar_context.markdown.assert_called_with("---")
    
    @patch('auth.app_wrapper.st')
    def test_logout_flow_with_page_refresh(self, mock_st):
        """Test complete logout flow including page refresh behavior."""
        # Create app wrapper
        app_wrapper = AppWrapper(self.config_path)
        
        # Mock the authenticated app function
        mock_app_func = MagicMock()
        app_wrapper.set_authenticated_app(mock_app_func)
        
        # Mock streamlit UI methods
        mock_st.set_page_config = MagicMock()
        mock_st.rerun = MagicMock()
        
        # Mock sidebar with logout button clicked
        mock_sidebar = MagicMock()
        mock_st.sidebar = mock_sidebar
        mock_sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_sidebar.__exit__ = MagicMock(return_value=None)
        mock_sidebar.write = MagicMock()
        mock_sidebar.markdown = MagicMock()
        mock_sidebar.button = MagicMock(return_value=True)  # Logout button clicked
        
        # Mock authentication manager methods
        with patch.object(app_wrapper.auth_manager, 'is_authenticated', return_value=True):
            with patch.object(app_wrapper.auth_manager, 'get_current_user_name', return_value='Test User'):
                with patch.object(app_wrapper.auth_manager, 'get_current_user', return_value='testuser'):
                    with patch.object(app_wrapper.auth_manager, 'handle_logout') as mock_logout:
                        # Render authenticated app (logout button clicked)
                        app_wrapper.render_authenticated_app()
                        
                        # Verify logout process
                        mock_logout.assert_called_once()
                        
                        # Verify page refresh is triggered
                        mock_st.rerun.assert_called_once()
                        
                        # After logout, user should be redirected to login screen
                        # This would be handled by the main() method checking authentication status


if __name__ == '__main__':
    unittest.main()