"""
Authentication manager for Streamlit application.

This module provides the core authentication functionality using streamlit-authenticator.
"""
from typing import Optional, Dict, Any
import streamlit as st
import streamlit_authenticator as stauth

from .config_manager import ConfigManager, AuthenticationState, ConfigurationError


class AuthenticationManager:
    """Core authentication manager for the Streamlit application."""
    
    def __init__(self, config_path: str = "credentials.yaml"):
        """Initialize the authentication manager.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self.config_manager = ConfigManager(config_path)
        self.authenticator = None
        self._config_loaded = False
    
    def load_config(self) -> Dict[str, Any]:
        """Load and initialize configuration.
        
        Returns:
            Dict containing the loaded configuration.
            
        Raises:
            ConfigurationError: If configuration loading fails.
        """
        try:
            config = self.config_manager.load_config()
            self._config_loaded = True
            return config
        except ConfigurationError as e:
            # Try to create default config if file doesn't exist
            if "not found" in str(e):
                self.config_manager.create_default_config()
                config = self.config_manager.load_config()
                self._config_loaded = True
                return config
            raise
    
    def initialize_authenticator(self) -> stauth.Authenticate:
        """Initialize the streamlit-authenticator instance.
        
        Returns:
            Configured Authenticate instance.
            
        Raises:
            ConfigurationError: If configuration is not loaded or invalid.
        """
        if not self._config_loaded:
            self.load_config()
        
        try:
            # Get user credentials and cookie config
            user_credentials = self.config_manager.get_user_credentials()
            cookie_config = self.config_manager.get_cookie_config()
            
            # Convert user credentials to the format expected by streamlit-authenticator
            credentials = {
                'usernames': {}
            }
            
            for username, user_cred in user_credentials.items():
                credentials['usernames'][username] = {
                    'name': user_cred.name,
                    'email': user_cred.email,
                    'password': user_cred.hashed_password
                }
            
            # Initialize the authenticator
            self.authenticator = stauth.Authenticate(
                credentials,
                cookie_config.name,
                cookie_config.key,
                cookie_config.expiry_days
            )
            
            return self.authenticator
            
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize authenticator: {str(e)}")
    
    def check_authentication(self) -> AuthenticationState:
        """Check the current authentication status.
        
        Returns:
            AuthenticationState object with current authentication information.
            
        Raises:
            ConfigurationError: If authenticator is not initialized.
        """
        if self.authenticator is None:
            self.initialize_authenticator()
        
        # Get authentication status from session state
        # streamlit-authenticator stores authentication info in session state
        name = st.session_state.get('name')
        authentication_status = st.session_state.get('authentication_status')
        username = st.session_state.get('username')
        
        return AuthenticationState(
            name=name,
            authentication_status=authentication_status,
            username=username
        )
    
    def is_authenticated(self) -> bool:
        """Check if the current user is authenticated.
        
        Returns:
            True if user is authenticated, False otherwise.
        """
        auth_state = self.check_authentication()
        return auth_state.is_authenticated
    
    def get_current_user(self) -> Optional[str]:
        """Get the current authenticated username.
        
        Returns:
            Username if authenticated, None otherwise.
        """
        auth_state = self.check_authentication()
        return auth_state.username if auth_state.is_authenticated else None
    
    def get_current_user_name(self) -> Optional[str]:
        """Get the current authenticated user's display name.
        
        Returns:
            User's display name if authenticated, None otherwise.
        """
        auth_state = self.check_authentication()
        return auth_state.name if auth_state.is_authenticated else None
    
    def handle_login(self) -> AuthenticationState:
        """Handle the login process with form rendering and authentication.
        
        This method renders the login form and processes authentication attempts.
        It handles both the UI rendering and the authentication logic.
        
        Returns:
            AuthenticationState object with current authentication information.
            
        Raises:
            ConfigurationError: If authenticator is not initialized.
        """
        if self.authenticator is None:
            self.initialize_authenticator()
        
        # Render the login form and handle authentication
        try:
            # In newer versions of streamlit-authenticator, login() doesn't return values
            # Instead, it directly updates the session state
            self.authenticator.login(location='main')
            
            # Get authentication status from session state after login attempt
            name = st.session_state.get('name')
            authentication_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            
            # Handle authentication results
            if authentication_status is False:
                st.error('Username/password is incorrect')
            elif authentication_status is None:
                st.warning('Please enter your username and password')
            elif authentication_status:
                # Successful authentication - display welcome message
                st.success(f'Welcome *{name}*')
                st.write(f'You are now logged in as {name}')
        
        except Exception as e:
            st.error(f'An error occurred during login: {str(e)}')
            # Set authentication status to failed
            st.session_state['authentication_status'] = False
        
        # Return current authentication state
        return self.check_authentication()
    
    def handle_logout(self) -> None:
        """Handle the logout process with session cleanup.
        
        This method clears the user's session and authentication state,
        effectively logging them out and requiring re-authentication.
        
        Raises:
            ConfigurationError: If authenticator is not initialized.
        """
        if self.authenticator is None:
            self.initialize_authenticator()
        
        try:
            # Use streamlit-authenticator's logout method
            self.authenticator.logout(location='sidebar')
            
            # Clear session state variables to ensure complete logout
            if 'authentication_status' in st.session_state:
                del st.session_state['authentication_status']
            if 'name' in st.session_state:
                del st.session_state['name']
            if 'username' in st.session_state:
                del st.session_state['username']
                
            # Don't display success message to avoid interfering with redirect
            
        except Exception as e:
            # Force clear session state even if logout method fails
            st.session_state.clear()