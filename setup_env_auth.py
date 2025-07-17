#!/usr/bin/env python3
"""
Script to help set up authentication via Streamlit secrets or environment variables.

This script follows the Streamlit secrets management standard and generates
configuration for both .streamlit/secrets.toml and .env files.
"""
import os
import bcrypt


def hash_password(password: str) -> str:
    """Generate bcrypt hash for a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_streamlit_secrets():
    """Create Streamlit secrets configuration."""
    print("🔐 Streamlit Secrets Setup")
    print("=" * 50)
    
    username = input("Username: ").strip()
    name = input("Display Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not all([username, name, email, password]):
        print("❌ All fields are required!")
        return
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Ask about cookie configuration
    use_cookies = input("\nEnable cookie-based sessions? (y/N): ").strip().lower() == 'y'
    
    # Generate secrets.toml content
    secrets_content = f"""[auth]
username = "{username}"
name = "{name}"
email = "{email}"
password = "{hashed_password}"
"""
    
    if use_cookies:
        cookie_key = input("Cookie secret key (or press Enter for auto-generated): ").strip()
        if not cookie_key:
            import secrets
            cookie_key = secrets.token_urlsafe(32)
        
        cookie_expiry = input("Cookie expiry days (default: 1): ").strip() or "1"
        
        secrets_content += f"""
# Cookie configuration
cookie_name = "kitchen_intel_auth_cookie"
cookie_key = "{cookie_key}"
cookie_expiry = {cookie_expiry}
"""
    
    print("\n" + "=" * 50)
    print("🎉 Streamlit Secrets Configuration Complete!")
    print("=" * 50)
    
    print("\n📋 Create .streamlit/secrets.toml with this content:")
    print("-" * 50)
    print(secrets_content)
    
    # Offer to create the file automatically
    create_file = input("\nCreate .streamlit/secrets.toml file automatically? (Y/n): ").strip().lower()
    if create_file != 'n':
        try:
            os.makedirs('.streamlit', exist_ok=True)
            with open('.streamlit/secrets.toml', 'w') as f:
                f.write(secrets_content)
            print("✅ Created .streamlit/secrets.toml")
            
            # Add to .gitignore
            gitignore_content = "\n# Streamlit secrets\n.streamlit/secrets.toml\n"
            try:
                with open('.gitignore', 'r') as f:
                    existing = f.read()
                if 'secrets.toml' not in existing:
                    with open('.gitignore', 'a') as f:
                        f.write(gitignore_content)
                    print("✅ Added secrets.toml to .gitignore")
            except FileNotFoundError:
                with open('.gitignore', 'w') as f:
                    f.write(gitignore_content)
                print("✅ Created .gitignore with secrets.toml")
                
        except Exception as e:
            print(f"❌ Error creating file: {e}")
    
    print("\n💡 Usage:")
    print("-" * 30)
    print("1. Secrets file created (or copy content above)")
    print("2. Remove or rename credentials.yaml file")
    print("3. Restart your Streamlit application")
    print("4. Secrets take precedence over other config methods")


def create_env_variables():
    """Create environment variables configuration."""
    print("🔐 Environment Variables Setup")
    print("=" * 50)
    
    username = input("Username: ").strip()
    name = input("Display Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not all([username, name, email, password]):
        print("❌ All fields are required!")
        return
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Ask about cookie configuration
    use_cookies = input("\nEnable cookie-based sessions? (y/N): ").strip().lower() == 'y'
    
    print("\n" + "=" * 50)
    print("🎉 Environment Variables Configuration Complete!")
    print("=" * 50)
    
    print("\n📋 Add these to your .env file:")
    print("-" * 30)
    print(f"AUTH_USERNAME={username}")
    print(f"AUTH_NAME={name}")
    print(f"AUTH_EMAIL={email}")
    print(f"AUTH_PASSWORD={hashed_password}")
    
    if use_cookies:
        cookie_key = input("\nCookie secret key (or press Enter for auto-generated): ").strip()
        if not cookie_key:
            import secrets
            cookie_key = secrets.token_urlsafe(32)
        
        cookie_expiry = input("Cookie expiry days (default: 1): ").strip() or "1"
        
        print(f"\nAUTH_COOKIE_NAME=kitchen_intel_auth_cookie")
        print(f"AUTH_COOKIE_KEY={cookie_key}")
        print(f"AUTH_COOKIE_EXPIRY={cookie_expiry}")
    
    print("\n💡 Usage:")
    print("-" * 30)
    print("1. Add variables above to your .env file")
    print("2. Remove or rename credentials.yaml file")
    print("3. Restart your Streamlit application")
    print("4. Environment variables are fallback to Streamlit secrets")


def quick_setup():
    """Quick setup with default admin user using Streamlit secrets."""
    print("🚀 Quick Setup - Creating default admin user")
    print("=" * 50)
    
    password = input("Enter password for admin user: ").strip()
    if not password:
        print("❌ Password is required!")
        return
    
    hashed_password = hash_password(password)
    
    secrets_content = f"""[auth]
username = "admin"
name = "Administrator"
email = "admin@example.com"
password = "{hashed_password}"
"""
    
    print(f"\n✅ Quick setup complete!")
    print(f"\n📋 Create .streamlit/secrets.toml with this content:")
    print("-" * 50)
    print(secrets_content)
    
    # Offer to create the file automatically
    create_file = input("\nCreate .streamlit/secrets.toml file automatically? (Y/n): ").strip().lower()
    if create_file != 'n':
        try:
            os.makedirs('.streamlit', exist_ok=True)
            with open('.streamlit/secrets.toml', 'w') as f:
                f.write(secrets_content)
            print("✅ Created .streamlit/secrets.toml")
        except Exception as e:
            print(f"❌ Error creating file: {e}")


if __name__ == "__main__":
    print("🔐 Authentication Setup")
    print("=" * 50)
    print("Choose configuration method:")
    print("1. Streamlit Secrets (recommended)")
    print("2. Environment Variables")
    print("3. Quick setup (admin user with Streamlit secrets)")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        create_streamlit_secrets()
    elif choice == "2":
        create_env_variables()
    elif choice == "3":
        quick_setup()
    else:
        print("❌ Invalid choice!")