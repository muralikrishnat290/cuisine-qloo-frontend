"""
Tests for the config_manager module.
"""
import os
import tempfile
import unittest
import yaml

from auth.config_manager import (
    ConfigManager, 
    ConfigurationError,
    UserCredential,
    AuthenticationState,
    CookieConfig
)


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_credentials.yaml")
        
        # Create a valid test configuration
        self.valid_config = {
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
                'key': 'test_key',
                'name': 'test_cookie'
            }
        }
        
        # Write the valid configuration to the temporary file
        with open(self.config_path, 'w') as file:
            yaml.dump(self.valid_config, file)
        
        # Create a config manager instance
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_valid_config(self):
        """Test loading a valid configuration."""
        config = self.config_manager.load_config()
        self.assertEqual(config['credentials']['usernames']['testuser']['name'], 'Test User')
        self.assertEqual(config['cookie']['expiry_days'], 30)
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        # Create a config manager with a non-existent file
        config_manager = ConfigManager("nonexistent.yaml")
        with self.assertRaises(ConfigurationError) as context:
            config_manager.load_config()
        self.assertIn("Configuration file not found", str(context.exception))
    
    def test_invalid_yaml_format(self):
        """Test handling of invalid YAML format."""
        # Write invalid YAML to the temporary file
        with open(self.config_path, 'w') as file:
            file.write("invalid: yaml: format:")
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Invalid YAML format", str(context.exception))
    
    def test_missing_credentials_section(self):
        """Test validation of missing credentials section."""
        # Create a config with missing credentials section
        invalid_config = {
            'cookie': {
                'expiry_days': 30,
                'key': 'test_key',
                'name': 'test_cookie'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(invalid_config, file)
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Missing 'credentials' section", str(context.exception))
    
    def test_missing_usernames_section(self):
        """Test validation of missing usernames section."""
        # Create a config with missing usernames section
        invalid_config = {
            'credentials': {},
            'cookie': {
                'expiry_days': 30,
                'key': 'test_key',
                'name': 'test_cookie'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(invalid_config, file)
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Missing 'usernames' section", str(context.exception))
    
    def test_missing_cookie_section(self):
        """Test validation of missing cookie section."""
        # Create a config with missing cookie section
        invalid_config = {
            'credentials': {
                'usernames': {
                    'testuser': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'password': 'hashed_password'
                    }
                }
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(invalid_config, file)
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Missing 'cookie' section", str(context.exception))
    
    def test_missing_cookie_fields(self):
        """Test validation of missing cookie fields."""
        # Create a config with missing cookie fields
        invalid_config = {
            'credentials': {
                'usernames': {
                    'testuser': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'password': 'hashed_password'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                # Missing 'key' and 'name'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(invalid_config, file)
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Missing required field", str(context.exception))
    
    def test_missing_user_fields(self):
        """Test validation of missing user fields."""
        # Create a config with missing user fields
        invalid_config = {
            'credentials': {
                'usernames': {
                    'testuser': {
                        'name': 'Test User',
                        # Missing 'email' and 'password'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'test_key',
                'name': 'test_cookie'
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(invalid_config, file)
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load_config()
        self.assertIn("Missing required field", str(context.exception))
    
    def test_get_user_credentials(self):
        """Test getting user credentials."""
        self.config_manager.load_config()
        credentials = self.config_manager.get_user_credentials()
        
        self.assertIn('testuser', credentials)
        user = credentials['testuser']
        self.assertIsInstance(user, UserCredential)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.hashed_password, '$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri')
    
    def test_get_cookie_config(self):
        """Test getting cookie configuration."""
        self.config_manager.load_config()
        cookie_config = self.config_manager.get_cookie_config()
        
        self.assertIsInstance(cookie_config, CookieConfig)
        self.assertEqual(cookie_config.expiry_days, 30)
        self.assertEqual(cookie_config.key, 'test_key')
        self.assertEqual(cookie_config.name, 'test_cookie')
    
    def test_get_config_before_loading(self):
        """Test getting configuration before loading."""
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.get_user_credentials()
        self.assertIn("Configuration not loaded", str(context.exception))
        
        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.get_cookie_config()
        self.assertIn("Configuration not loaded", str(context.exception))
    
    def test_create_default_config(self):
        """Test creating a default configuration."""
        # Remove the existing config file
        os.remove(self.config_path)
        
        # Create a default configuration
        self.config_manager.create_default_config()
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.config_path))
        
        # Load the configuration and check its structure
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.assertIn('credentials', config)
        self.assertIn('usernames', config['credentials'])
        self.assertIn('admin', config['credentials']['usernames'])
        self.assertIn('cookie', config)
        self.assertIn('expiry_days', config['cookie'])
        self.assertIn('key', config['cookie'])
        self.assertIn('name', config['cookie'])
    
    def test_authentication_state(self):
        """Test AuthenticationState class."""
        # Test default state (not authenticated)
        state = AuthenticationState()
        self.assertFalse(state.is_authenticated)
        
        # Test authenticated state
        state = AuthenticationState(name="Test User", authentication_status=True, username="testuser")
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.name, "Test User")
        self.assertEqual(state.username, "testuser")
        
        # Test failed authentication
        state = AuthenticationState(authentication_status=False)
        self.assertFalse(state.is_authenticated)


if __name__ == '__main__':
    unittest.main()