"""
Application wrapper with authentication gate for Streamlit application.

This module provides the main application wrapper that handles authentication
and renders either the login screen or the authenticated application.
"""
import streamlit as st
from typing import Callable, Optional
from .authentication_manager import AuthenticationManager, ConfigurationError


class AppWrapper:
    """Application wrapper that provides authentication gate functionality."""
    
    def __init__(self, config_path: str = "credentials.yaml"):
        """Initialize the application wrapper.
        
        Args:
            config_path: Path to the authentication configuration file.
        """
        self.auth_manager = AuthenticationManager(config_path)
        self._authenticated_app_func: Optional[Callable] = None
    
    def set_authenticated_app(self, app_func: Callable) -> None:
        """Set the function that renders the authenticated application.
        
        Args:
            app_func: Function that renders the main application content.
        """
        self._authenticated_app_func = app_func
    
    def render_login_screen(self) -> None:
        """Render the authentication interface (login screen)."""
        # Login screen header
        st.title("🍜 Kitchen Intel")
        st.subheader("Please login to access the application")
        
        # Add some spacing and styling
        st.markdown("---")
        
        try:
            # Handle the login process
            auth_state = self.auth_manager.handle_login()
            
            # If authentication is successful, rerun to show the main app
            if auth_state.is_authenticated:
                st.rerun()
                
        except ConfigurationError as e:
            st.error(f"Configuration Error: {str(e)}")
            st.info("Please contact your administrator to resolve this issue.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.info("Please try refreshing the page or contact support.")
    
    def render_authenticated_app(self) -> None:
        """Render the main application for authenticated users."""
        if self._authenticated_app_func is None:
            st.error("No authenticated application function has been set.")
            return
        
        try:
            # Check authentication status
            if not self.auth_manager.is_authenticated():
                # If not authenticated, redirect to login
                st.rerun()
                return
            
            # Get current user info
            user_name = self.auth_manager.get_current_user_name()
            username = self.auth_manager.get_current_user()
            
            # Add logout functionality in sidebar
            with st.sidebar:
                st.write(f"👤 Logged in as: **{user_name}**")
                st.write(f"Username: {username}")
                st.markdown("---")
                
                if st.button("🚪 Logout", type="secondary", use_container_width=True):
                    self.auth_manager.handle_logout()
                    # Force clear session state to ensure logout
                    st.session_state.clear()
                    st.rerun()
            
            # Render the main authenticated application
            self._authenticated_app_func()
            
        except ConfigurationError as e:
            st.error(f"Configuration Error: {str(e)}")
            st.info("Please contact your administrator to resolve this issue.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.info("Please try refreshing the page or contact support.")
    
    def main(self) -> None:
        """Main application entry point with authentication check logic."""
        # Set page configuration once at the start
        st.set_page_config(
            page_title="KitchenIntel", 
            page_icon="🍜",
            layout="wide"
        )
        
        try:
            # Initialize authentication manager
            self.auth_manager.load_config()
            
            # Check if user is authenticated
            if self.auth_manager.is_authenticated():
                # User is authenticated, show the main app
                self.render_authenticated_app()
            else:
                # User is not authenticated, show login screen
                self.render_login_screen()
                
        except ConfigurationError as e:
            # Handle configuration errors gracefully
            st.title("🍜 Kitchen Intel")
            st.error(f"Configuration Error: {str(e)}")
            st.info("Please contact your administrator to resolve this issue.")
            
            # Show some helpful information for administrators
            with st.expander("Administrator Information"):
                st.markdown("""
                **Common configuration issues:**
                - Missing `credentials.yaml` file
                - Invalid YAML format in configuration file
                - Missing required configuration fields
                - Incorrect file permissions
                
                **To resolve:**
                1. Ensure `credentials.yaml` exists in the application root
                2. Verify the YAML format is correct
                3. Check that all required fields are present
                4. Ensure the application has read access to the file
                """)
        
        except Exception as e:
            # Handle unexpected errors
            st.title("🍜 Kitchen Intel")
            st.error(f"An unexpected error occurred: {str(e)}")
            st.info("Please try refreshing the page or contact support.")


def create_app_wrapper(config_path: str = "credentials.yaml") -> AppWrapper:
    """Create and return an AppWrapper instance.
    
    Args:
        config_path: Path to the authentication configuration file.
        
    Returns:
        Configured AppWrapper instance.
    """
    return AppWrapper(config_path)