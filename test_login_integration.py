#!/usr/bin/env python3
"""
Simple integration test to verify login functionality works.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from unittest.mock import patch, MagicMock
from auth.authentication_manager import AuthenticationManager
from auth.config_manager import AuthenticationState

def test_login_integration():
    """Test the complete login flow."""
    print("Testing login integration...")
    
    # Create auth manager with test config
    auth_manager = AuthenticationManager("credentials.yaml")
    
    # Mock streamlit and authenticator
    with patch('auth.authentication_manager.st') as mock_st, \
         patch('auth.authentication_manager.stauth.Authenticate') as mock_authenticate:
        
        # Setup mocks
        mock_auth_instance = MagicMock()
        mock_authenticate.return_value = mock_auth_instance
        
        # Test successful login
        print("1. Testing successful login...")
        mock_auth_instance.login.return_value = ('Test User', True, 'testuser')
        mock_st.session_state.get.side_effect = lambda key: {
            'name': 'Test User',
            'authentication_status': True,
            'username': 'testuser'
        }.get(key)
        mock_st.success = MagicMock()
        mock_st.write = MagicMock()
        
        auth_state = auth_manager.handle_login()
        
        assert auth_state.is_authenticated == True
        assert auth_state.name == 'Test User'
        assert auth_state.username == 'testuser'
        mock_st.success.assert_called_once_with('Welcome *Test User*')
        print("✓ Successful login test passed")
        
        # Test failed login
        print("2. Testing failed login...")
        mock_auth_instance.login.return_value = (None, False, None)
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': False,
            'username': None
        }.get(key)
        mock_st.error = MagicMock()
        
        auth_state = auth_manager.handle_login()
        
        assert auth_state.is_authenticated == False
        assert auth_state.name is None
        assert auth_state.username is None
        mock_st.error.assert_called_with('Username/password is incorrect')
        print("✓ Failed login test passed")
        
        # Test empty credentials
        print("3. Testing empty credentials...")
        mock_auth_instance.login.return_value = (None, None, None)
        mock_st.session_state.get.side_effect = lambda key: {
            'name': None,
            'authentication_status': None,
            'username': None
        }.get(key)
        mock_st.warning = MagicMock()
        
        auth_state = auth_manager.handle_login()
        
        assert auth_state.is_authenticated == False
        mock_st.warning.assert_called_with('Please enter your username and password')
        print("✓ Empty credentials test passed")
        
    print("All login integration tests passed! ✓")

if __name__ == "__main__":
    test_login_integration()