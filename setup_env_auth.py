#!/usr/bin/env python3
"""
Script to help set up authentication via environment variables.

This script generates the AUTH_USERS JSON string that can be used
as an environment variable instead of credentials.yaml file.
"""
import json
import bcrypt


def hash_password(password: str) -> str:
    """Generate bcrypt hash for a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_user_config():
    """Interactive script to create user configuration."""
    users = {}
    
    print("🔐 Authentication Environment Variable Setup")
    print("=" * 50)
    
    while True:
        print(f"\nAdding user #{len(users) + 1}")
        username = input("Username: ").strip()
        if not username:
            break
            
        name = input("Display Name: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if not all([username, name, email, password]):
            print("❌ All fields are required!")
            continue
            
        # Hash the password
        hashed_password = hash_password(password)
        
        users[username] = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        
        print(f"✅ Added user: {username}")
        
        another = input("\nAdd another user? (y/N): ").strip().lower()
        if another != 'y':
            break
    
    if not users:
        print("❌ No users created!")
        return
    
    # Generate JSON string
    auth_users_json = json.dumps(users, indent=2)
    
    print("\n" + "=" * 50)
    print("🎉 Configuration Complete!")
    print("=" * 50)
    
    print("\n📋 Add this to your .env file:")
    print("-" * 30)
    print(f'AUTH_USERS=\'{auth_users_json}\'')
    
    print("\n📋 Or export as environment variable:")
    print("-" * 30)
    print(f'export AUTH_USERS=\'{auth_users_json}\'')
    
    print("\n📋 Optional cookie settings (add to .env if needed):")
    print("-" * 30)
    print("AUTH_COOKIE_NAME=kitchen_intel_auth_cookie")
    print("AUTH_COOKIE_KEY=your_secret_key_here")
    print("AUTH_COOKIE_EXPIRY=1")
    
    print("\n💡 Usage:")
    print("-" * 30)
    print("1. Add AUTH_USERS to your .env file")
    print("2. Remove or rename credentials.yaml file")
    print("3. Restart your Streamlit application")
    print("4. Environment variables take precedence over YAML file")


def quick_setup():
    """Quick setup with default admin user."""
    print("🚀 Quick Setup - Creating default admin user")
    print("=" * 50)
    
    password = input("Enter password for admin user: ").strip()
    if not password:
        print("❌ Password is required!")
        return
    
    users = {
        "admin": {
            "name": "Administrator",
            "email": "admin@example.com",
            "password": hash_password(password)
        }
    }
    
    auth_users_json = json.dumps(users)
    
    print(f"\n✅ Quick setup complete!")
    print(f"\n📋 Add to .env file:")
    print(f"AUTH_USERS='{auth_users_json}'")


if __name__ == "__main__":
    print("Choose setup option:")
    print("1. Interactive setup (multiple users)")
    print("2. Quick setup (admin user only)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        create_user_config()
    elif choice == "2":
        quick_setup()
    else:
        print("❌ Invalid choice!")