"""
Configuration manager for authentication.

This module handles loading and validating YAML configuration for authentication.
"""
import os
from dataclasses import dataclass
from typing import Dict, Optional, Any
import yaml


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
    
    def __init__(self, config_path: str = "credentials.yaml"):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self.config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables or YAML file.
        
        Environment variables take precedence over YAML file.
        Expected env vars for single user:
        - AUTH_USERNAME: Username for login
        - AUTH_NAME: Display name
        - AUTH_EMAIL: User email
        - AUTH_PASSWORD: Bcrypt hashed password
        - AUTH_COOKIE_NAME: Cookie name (optional)
        - AUTH_COOKIE_KEY: Cookie key (optional)  
        - AUTH_COOKIE_EXPIRY: Cookie expiry days (optional)
        
        Returns:
            Dict containing the configuration.
            
        Raises:
            ConfigurationError: If the configuration is missing or invalid.
        """
        # Try to load from environment variables first
        config = self._load_from_env()
        if config:
            self._validate_config(config)
            self.config = config
            return config
        
        # Fall back to YAML file
        try:
            if not os.path.exists(self.config_path):
                raise ConfigurationError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            self._validate_config(config)
            self.config = config
            return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML format in {self.config_path}: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {str(e)}")
    
    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load configuration from Streamlit secrets or environment variables.
        
        Follows Streamlit secrets management standard:
        https://docs.streamlit.io/develop/concepts/connections/secrets-management
        
        Priority order:
        1. Streamlit secrets (.streamlit/secrets.toml)
        2. Environment variables
        
        Expected secrets format in .streamlit/secrets.toml:
        [auth]
        username = "admin"
        name = "Administrator"
        email = "admin@example.com"
        password = "$2b$12$hashed_password"
        
        # Optional cookie settings
        cookie_name = "app_auth_cookie"
        cookie_key = "secret_key"
        cookie_expiry = 1
        
        Fallback environment variables:
        - AUTH_USERNAME, AUTH_NAME, AUTH_EMAIL, AUTH_PASSWORD
        
        Returns:
            Dict containing the configuration or None if not available.
        """
        import streamlit as st
        
        # Try Streamlit secrets first (recommended approach)
        try:
            # Check if auth section exists in secrets
            if "auth" in st.secrets:
                auth_secrets = st.secrets["auth"]
                
                # Get required auth fields
                auth_username = auth_secrets.get("username")
                auth_name = auth_secrets.get("name")
                auth_email = auth_secrets.get("email")
                auth_password = auth_secrets.get("password")
                
                # All required secrets must be present
                if not all([auth_username, auth_name, auth_email, auth_password]):
                    # Some required secrets missing, fall back to env vars
                    pass
                else:
                    # All required secrets are available
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
                    
                    # Add optional cookie configuration from secrets
                    cookie_name = auth_secrets.get("cookie_name")
                    cookie_key = auth_secrets.get("cookie_key")
                    cookie_expiry = auth_secrets.get("cookie_expiry")
                    
                    if cookie_name and cookie_key and cookie_expiry:
                        try:
                            config['cookie'] = {
                                'name': cookie_name,
                                'key': cookie_key,
                                'expiry_days': int(cookie_expiry)
                            }
                        except ValueError:
                            # Invalid cookie_expiry, skip cookie config
                            pass
                    
                    return config
            
        except Exception:
            # Error accessing secrets, fall back to environment variables
            pass
        
        # Fallback to environment variables
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
    
    def create_default_config(self) -> None:
        """Create a default configuration file if it doesn't exist.
        
        This creates a template configuration file with instructions.
        """
        if os.path.exists(self.config_path):
            return
        
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'name': 'Administrator',
                        'email': 'admin@example.com',
                        'password': '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri'  # 'password'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'some_random_signature_key',
                'name': 'kitchen_intel_auth_cookie'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)