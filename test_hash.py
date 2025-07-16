#!/usr/bin/env python3
"""
Test script to generate bcrypt hashes and test authentication.
"""
import bcrypt
import streamlit_authenticator as stauth

def generate_hash(password: str) -> str:
    """Generate bcrypt hash for a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def test_hash(password: str, hash_str: str) -> bool:
    """Test if password matches hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hash_str.encode('utf-8'))

if __name__ == "__main__":
    # Generate new hash for 'password'
    new_hash = generate_hash('password')
    print(f"New hash for 'password': {new_hash}")
    
    # Test the existing hash
    existing_hash = "$2b$12$rAp7.pP33jWnWEJVhXuvY.jqvCHnDgX1KFrOHMQQ.xIm4cEMjEiri"
    print(f"Testing existing hash: {test_hash('password', existing_hash)}")
    
    # Test new hash
    print(f"Testing new hash: {test_hash('password', new_hash)}")
    
    # Try using streamlit-authenticator's hashing
    try:
        hashed_passwords = stauth.Hasher(['password']).generate()
        print(f"Streamlit-authenticator hash: {hashed_passwords[0]}")
    except Exception as e:
        print(f"Error with streamlit-authenticator hasher: {e}")