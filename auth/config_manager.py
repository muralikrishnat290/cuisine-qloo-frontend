"""
Configuration manager for authentication.

This module handles loading and validating environment variable configuration for authentication.
"""
import os
from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class UserCredential:
    """User credential data model."""
    username: str
    name: str
    email: str
    hashed_password: str


@dataclass
class AuthenticationState:
    """Authentication state data model."""
    name: Optional[str] = None
    authentication_status: Optional[bool] = None
    username: Optional[str] = None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the user is authenticated."""
        return self.authentication_status is True


@dataclass
class CookieConfig:
    """Cookie configuration data model."""
    expiry_days: int
    key: str
    name: str


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class ConfigManager:
    """Manager for authentication configuration."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables only.
        
        Required environment variables:
        - AUTH_USERNAME: Username for login
        - AUTH_NAME: Display name
        - AUTH_EMAIL: User email
        - AUTH_PASSWORD: Bcrypt hashed password
        
        Optional environment variables:
        - AUTH_COOKIE_NAME: Cookie name
        - AUTH_COOKIE_KEY: Cookie key  
        - AUTH_COOKIE_EXPIRY: Cookie expiry days
        
        Returns:
            Dict containing the configuration.
            
        Raises:
            ConfigurationError: If required environment variables are missing.
        """
        config = self._load_from_env()
        if not config:
            raise ConfigurationError(
                "Required environment variables not found. Please set: "
                "AUTH_USERNAME, AUTH_NAME, AUTH_EMAIL, AUTH_PASSWORD"
            )
        
        self._validate_config(config)
        self.config = config
        return config
    
    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load configuration from environment variables only.
        
        Required environment variables:
        - AUTH_USERNAME: Username for login
        - AUTH_NAME: Display name
        - AUTH_EMAIL: User email
        - AUTH_PASSWORD: Bcrypt hashed password
        
        Optional environment variables:
        - AUTH_COOKIE_NAME: Cookie name
        - AUTH_COOKIE_KEY: Cookie key
        - AUTH_COOKIE_EXPIRY: Cookie expiry days
        
        Returns:
            Dict containing the configuration or None if not available.
        """
        # Get required environment variables
        auth_username = os.getenv('AUTH_USERNAME')
        auth_name = os.getenv('AUTH_NAME')
        auth_email = os.getenv('AUTH_EMAIL')
        auth_password = os.getenv('AUTH_PASSWORD')
        
        # If any required variable is missing, return None
        if not all([auth_username, auth_name, auth_email, auth_password]):
            return None
        
        try:
            # Create single user configuration from env vars
            config = {
                'credentials': {
                    'usernames': {
                        auth_username: {
                            'name': auth_name,
                            'email': auth_email,
                            'password': auth_password
                        }
                    }
                }
            }
            
            # Add optional cookie configuration from env vars
            cookie_name = os.getenv('AUTH_COOKIE_NAME')
            cookie_key = os.getenv('AUTH_COOKIE_KEY')
            cookie_expiry = os.getenv('AUTH_COOKIE_EXPIRY')
            
            if cookie_name and cookie_key and cookie_expiry:
                config['cookie'] = {
                    'name': cookie_name,
                    'key': cookie_key,
                    'expiry_days': int(cookie_expiry)
                }
            
            return config
            
        except ValueError as e:
            raise ConfigurationError(f"Invalid AUTH_COOKIE_EXPIRY value: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration from environment: {str(e)}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration structure.
        
        Args:
            config: Configuration dictionary to validate.
            
        Raises:
            ConfigurationError: If the configuration is invalid.
        """
        # Check if credentials section exists
        if 'credentials' not in config:
            raise ConfigurationError("Missing 'credentials' section in configuration")
        
        # Check if usernames section exists
        if 'usernames' not in config['credentials']:
            raise ConfigurationError("Missing 'usernames' section in credentials configuration")
        
        # Check if cookie section exists (optional)
        if 'cookie' in config:
            # Validate cookie configuration if present
            cookie_config = config['cookie']
            required_cookie_fields = ['expiry_days', 'key', 'name']
            for field in required_cookie_fields:
                if field not in cookie_config:
                    raise ConfigurationError(f"Missing required field '{field}' in cookie configuration")
        
        # Validate user credentials
        usernames = config['credentials']['usernames']
        if not usernames:
            raise ConfigurationError("No users defined in configuration")
        
        for username, user_data in usernames.items():
            required_user_fields = ['name', 'email', 'password']
            for field in required_user_fields:
                if field not in user_data:
                    raise ConfigurationError(f"Missing required field '{field}' for user '{username}'")
    
    def get_user_credentials(self) -> Dict[str, UserCredential]:
        """Get user credentials from the configuration.
        
        Returns:
            Dict mapping usernames to UserCredential objects.
            
        Raises:
            ConfigurationError: If the configuration is not loaded.
        """
        if self.config is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        credentials = {}
        usernames = self.config['credentials']['usernames']
        
        for username, user_data in usernames.items():
            credentials[username] = UserCredential(
                username=username,
                name=user_data['name'],
                email=user_data['email'],
                hashed_password=user_data['password']
            )
        
        return credentials
    
    def get_cookie_config(self) -> CookieConfig:
        """Get cookie configuration.
        
        Returns:
            CookieConfig object.
            
        Raises:
            ConfigurationError: If the configuration is not loaded or no cookie config exists.
        """
        if self.config is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        if 'cookie' not in self.config:
            raise ConfigurationError("No cookie configuration found.")
        
        cookie_data = self.config['cookie']
        return CookieConfig(
            expiry_days=cookie_data['expiry_days'],
            key=cookie_data['key'],
            name=cookie_data['name']
        )
    
