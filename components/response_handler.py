"""
Response handling utilities for Kitchen Intel application.

This module provides utilities for processing and displaying API responses
in various formats with proper error handling.
"""
import json
import streamlit as st
from typing import Any, Dict, Optional


def extract_text_from_response(result: Any) -> str:
    """
    Extract text content from various response formats.
    
    Args:
        result: API response in various formats (dict, string, etc.)
        
    Returns:
        String representation of the response content
    """
    if isinstance(result, dict):
        # Try common response field names
        for field in ['text', 'content', 'response', 'message', 'data', 'output']:
            if field in result:
                print(f"Extracting from field: {result}")
                return str(result[field])
        # If no common field found, return formatted JSON
        return json.dumps(result, indent=2)
    else:
        return str(result)


def display_response(placeholder: st.container, content: str, display_format: str, 
                    title: str, preserve_formatting: bool) -> None:
    """
    Display response content with proper formatting.
    
    Args:
        placeholder: Streamlit container to display content in
        content: Response content to display
        display_format: Format type for display (Auto-detect, Markdown, Code, JSON, Plain Text)
        title: Title for the response section
        preserve_formatting: Whether to preserve original formatting
    """
    if display_format == "Auto-detect":
        _auto_detect_and_display(placeholder, content, title, preserve_formatting)
    elif display_format == "Markdown":
        placeholder.markdown(f"**📥 {title}:**\n\n{content}")
    elif display_format == "Code":
        placeholder.code(content, language="text")
    elif display_format == "JSON":
        _display_as_json(placeholder, content)
    else:  # Plain Text
        placeholder.text_area(f"📥 {title}:", value=content, height=300, disabled=True)


def _auto_detect_and_display(placeholder: st.container, content: str, title: str, 
                           preserve_formatting: bool) -> None:
    """Auto-detect content type and display appropriately."""
    content_stripped = content.strip()
    
    if content_stripped.startswith('{') or content_stripped.startswith('['):
        # Looks like JSON
        try:
            parsed = json.loads(content)
            placeholder.json(parsed)
        except json.JSONDecodeError:
            placeholder.markdown(f"**📥 {title}:**\n\n{content}")
    elif any(marker in content for marker in ['**', '#', '*', '<']):
        # Looks like markdown
        placeholder.markdown(f"**📥 {title}:**\n\n{content}", unsafe_allow_html=True)
    else:
        # Plain text with preserved formatting
        if preserve_formatting:
            placeholder.text(content)
        else:
            placeholder.write(content)


def _display_as_json(placeholder: st.container, content: str) -> None:
    """Display content as JSON with error handling."""
    try:
        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content
        placeholder.json(parsed)
    except json.JSONDecodeError:
        placeholder.code(content, language="json")


def show_fallback_response_info(raw_data: str) -> None:
    """Show fallback information when response parsing fails."""
    st.info("**Troubleshooting steps:**")
    st.write("1. Check if the API is returning valid JSON")
    st.write("2. Verify the API endpoint configuration")
    st.write("3. Try the request again")
    
    with st.expander("🔍 View Raw Response"):
        st.text(raw_data[:1000] + "..." if len(raw_data) > 1000 else raw_data)