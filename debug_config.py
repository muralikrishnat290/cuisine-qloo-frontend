#!/usr/bin/env python3
"""
Debug script to check environment variable configuration.
"""
import os

def check_environment_variables():
    """Check if all required environment variables are set."""
    print("🔍 Checking Environment Variables")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'AUTH_USERNAME': 'Username for login',
        'AUTH_NAME': 'Display name',
        'AUTH_EMAIL': 'User email',
        'AUTH_PASSWORD': 'Bcrypt hashed password'
    }
    
    # Optional environment variables
    optional_vars = {
        'AUTH_COOKIE_NAME': 'Cookie name',
        'AUTH_COOKIE_KEY': 'Cookie key',
        'AUTH_COOKIE_EXPIRY': 'Cookie expiry days',
        'API_URL': 'API URL',
        'API_KEY': 'API key'
    }
    
    print("\n📋 Required Variables:")
    print("-" * 30)
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description}")
            if var == 'AUTH_PASSWORD':
                print(f"   Value: {value[:20]}... (truncated)")
            else:
                print(f"   Value: {value}")
        else:
            print(f"❌ {var}: {description} - NOT SET")
            missing_required.append(var)
    
    print("\n📋 Optional Variables:")
    print("-" * 30)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description}")
            if var == 'API_KEY':
                print(f"   Value: {value[:10]}... (truncated)")
            else:
                print(f"   Value: {value}")
        else:
            print(f"⚠️  {var}: {description} - NOT SET")
    
    print("\n" + "=" * 50)
    
    if missing_required:
        print("❌ CONFIGURATION ERROR:")
        print(f"Missing required variables: {', '.join(missing_required)}")
        print("\n💡 To fix this:")
        print("1. Set the missing environment variables")
        print("2. Or run: python3 setup_env_auth.py")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def test_config_loading():
    """Test loading configuration with current environment variables."""
    print("\n🧪 Testing Configuration Loading")
    print("=" * 50)
    
    try:
        from auth.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        print("✅ Configuration loaded successfully")
        
        # Check user credentials
        user_creds = config_manager.get_user_credentials()
        print(f"✅ Found {len(user_creds)} user(s):")
        
        for username, cred in user_creds.items():
            print(f"   - {username}: {cred.name} ({cred.email})")
            
            # Validate password hash
            if cred.hashed_password and cred.hashed_password.startswith('$2b$'):
                print(f"     Password hash: ✅ Valid bcrypt format")
            else:
                print(f"     Password hash: ❌ Invalid format")
        
        # Check cookie config
        try:
            cookie_config = config_manager.get_cookie_config()
            print(f"✅ Cookie config: {cookie_config.name} (expires: {cookie_config.expiry_days} days)")
        except:
            print("ℹ️  No cookie configuration (session-only mode)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {str(e)}")
        return False

def test_authenticator_initialization():
    """Test authenticator initialization."""
    print("\n🔐 Testing Authenticator Initialization")
    print("=" * 50)
    
    try:
        from auth.authentication_manager import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        authenticator = auth_manager.initialize_authenticator()
        
        print("✅ Authenticator initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Authenticator initialization failed: {str(e)}")
        print("\n🔍 Possible causes:")
        print("- One of the environment variables is None or empty")
        print("- Password hash is not in valid bcrypt format")
        print("- streamlit-authenticator version compatibility issue")
        return False

if __name__ == "__main__":
    print("🔧 Kitchen Intel Configuration Debug")
    print("=" * 60)
    
    # Step 1: Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ Fix environment variables first before proceeding.")
        exit(1)
    
    # Step 2: Test configuration loading
    config_ok = test_config_loading()
    
    if not config_ok:
        print("\n❌ Fix configuration issues before proceeding.")
        exit(1)
    
    # Step 3: Test authenticator initialization
    auth_ok = test_authenticator_initialization()
    
    if auth_ok:
        print("\n🎉 All tests passed! Configuration is working correctly.")
    else:
        print("\n❌ Authenticator initialization failed. Check the error above.")
        exit(1)