#!/usr/bin/env python3
"""
Script to help set up authentication using environment variables only.

This script generates environment variable configuration for authentication.
"""
import bcrypt


def hash_password(password: str) -> str:
    """Generate bcrypt hash for a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def setup_authentication():
    """Interactive setup for authentication."""
    print("🔐 Environment Variables Authentication Setup")
    print("=" * 50)
    print("Simple environment variable configuration")
    print()
    
    # Get user input
    username = input("Username: ").strip()
    name = input("Display Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not all([username, name, email, password]):
        print("❌ All fields are required!")
        return
    
    # Hash the password
    print("🔄 Hashing password...")
    hashed_password = hash_password(password)
    
    print("\n" + "=" * 50)
    print("🎉 Configuration Complete!")
    print("=" * 50)
    
    # Show environment variables
    print("\n📋 Environment Variables (.env file):")
    print("-" * 50)
    print(f"AUTH_USERNAME={username}")
    print(f"AUTH_NAME={name}")
    print(f"AUTH_EMAIL={email}")
    print(f"AUTH_PASSWORD={hashed_password}")
    print()
    print("# API configuration")
    print("API_URL=http://localhost:8080")
    print("API_KEY=your_api_key_here")
    print()
    print("# Optional: Cookie configuration (remove for session-only auth)")
    print("# AUTH_COOKIE_NAME=kitchen_intel_auth_cookie")
    print("# AUTH_COOKIE_KEY=your_secret_key_here")
    print("# AUTH_COOKIE_EXPIRY=1")
    print()
    print("# Optional: Suppress warnings")
    print("PYTHONWARNINGS=ignore")
    
    print("\n💡 Next Steps:")
    print("-" * 30)
    print("1. Copy the environment variables above to your .env file")
    print("2. Update API_KEY with your actual API key")
    print("3. Set these variables in your deployment platform (Railway, Render, etc.)")
    print("4. Restart your application")
    
    print("\n🔒 Security Notes:")
    print("-" * 30)
    print("• Never commit .env files to version control")
    print("• Use different credentials for different environments")
    print("• Keep your hashed passwords secure")
    print("• Rotate credentials regularly")


def quick_admin_setup():
    """Quick setup with default admin user."""
    print("🚀 Quick Admin Setup")
    print("=" * 50)
    
    password = input("Enter password for admin user: ").strip()
    if not password:
        print("❌ Password is required!")
        return
    
    # Use default admin values
    username = "admin"
    name = "Administrator"
    email = "admin@example.com"
    hashed_password = hash_password(password)
    
    print(f"\n✅ Admin user configuration generated!")
    print("\n📋 Environment Variables:")
    print("-" * 30)
    print(f"AUTH_USERNAME={username}")
    print(f"AUTH_NAME={name}")
    print(f"AUTH_EMAIL={email}")
    print(f"AUTH_PASSWORD={hashed_password}")
    print("API_URL=http://localhost:8080")
    print("API_KEY=your_api_key_here")
    print("PYTHONWARNINGS=ignore")
    
    print("\n🔑 Login credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    print("\n💡 Copy the environment variables above to your .env file or deployment platform!")


if __name__ == "__main__":
    print("🔐 Authentication Setup (Environment Variables Only)")
    print("=" * 60)
    print("Choose setup option:")
    print("1. Custom user setup")
    print("2. Quick admin setup")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        setup_authentication()
    elif choice == "2":
        quick_admin_setup()
    else:
        print("❌ Invalid choice!")