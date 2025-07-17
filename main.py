"""
Kitchen Intel Streamlit Application with Authentication

Main entry point for the Kitchen Intel application with authentication gate.
"""
from auth.app_wrapper import create_app_wrapper
from kitchen_intel_app import render_authenticated_app
from dotenv import load_dotenv

load_dotenv('.env')


def main():
    """Main application entry point."""
    # Create the application wrapper with authentication
    app_wrapper = create_app_wrapper()
    
    # Set the authenticated application function
    app_wrapper.set_authenticated_app(render_authenticated_app)
    
    # Run the application with authentication gate
    app_wrapper.main()


if __name__ == "__main__":
    main()