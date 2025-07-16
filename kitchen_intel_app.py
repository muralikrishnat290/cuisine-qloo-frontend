"""
Kitchen Intel application - main application logic.

This module contains the core Kitchen Intel application functionality
that will be rendered for authenticated users.
"""
import streamlit as st
from dotenv import load_dotenv
import requests
import os
import time
import json

load_dotenv()


def extract_text_from_response(result):
    """Extract text content from various response formats"""
    if isinstance(result, dict):
        # Try common response field names
        for field in ['text', 'content', 'response', 'message', 'data',
                      'output']:
            if field in result:
                print(f"Extracting from field: {result}")
                return str(result[field])
        # If no common field found, return formatted JSON
        return json.dumps(result, indent=2)
    else:
        return str(result)


def display_response(placeholder, content, display_format, title,
                     preserve_formatting):
    """Display response content with proper formatting"""
    if display_format == "Auto-detect":
        # Auto-detect content type
        if content.strip().startswith('{') or content.strip().startswith('['):
            # Looks like JSON
            try:
                parsed = json.loads(content)
                placeholder.json(parsed)
            except:
                placeholder.markdown(f"**📥 {title}:**\n\n{content}")
        elif '**' in content or '#' in content or '*' in content or '<':
            # Looks like markdown
            placeholder.markdown(f"**📥 {title}:**\n\n{content}", unsafe_allow_html=True)
        else:
            # Plain text with preserved formatting
            if preserve_formatting:
                placeholder.text(content)
            else:
                placeholder.write(content)

    elif display_format == "Markdown":
        placeholder.markdown(f"**📥 {title}:**\n\n{content}")

    elif display_format == "Code":
        placeholder.code(content, language="text")

    elif display_format == "JSON":
        try:
            if isinstance(content, str):
                parsed = json.loads(content)
            else:
                parsed = content
            placeholder.json(parsed)
        except:
            placeholder.code(content, language="json")

    else:  # Plain Text
        placeholder.text_area(f"📥 {title}:", value=content, height=300,
                              disabled=True)


def render_authenticated_app():
    """Render the main Kitchen Intel application for authenticated users."""
    # Page config is handled by the app wrapper, so we don't set it here
    
    # Title
    st.title("🍜 Kitchen Intel")

    # App description and display options
    col1, col2 = st.columns([4, 1])
    with col1:
        # App description popup
        with st.popover("ℹ️ About this app"):
            st.markdown("""
            **Food & Cuisine Business Analysis Tool**
            
            Get insights into food and cuisine business performance, sales analysis, and market trends for restaurants and food businesses in specific geographic areas.
            As this is a MVP (Minimum Viable Product), it does not have memory and is not designated to single user.
            So your queries and responses are not saved or personalized but for your current session only and for single query.
            """)
    with col2:
        # Settings in popup
        with st.popover("⚙️ Settings"):
            auto_scroll = st.checkbox("Auto-scroll", value=True)
            preserve_formatting = st.checkbox("Preserve formatting", value=True)

    # Configuration
    api_url = os.getenv("API_URL", "http://localhost:8080")
    api_key = os.getenv("API_KEY", "sample-key")

    # Text input with larger font size
    with st.container():
        st.markdown("""
        <div style="background-color: #f0f0f0; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #333;">To start analysis, type "how pizza 🍕 performs in Stuttgart":</h4>
        </div>
        """, unsafe_allow_html=True)
    user_text = st.text_area("Query input", height=150, placeholder="Type your message here...", label_visibility="hidden")

    # Disclaimer
    st.markdown("""
    ⚠️ **Disclaimer:** This tool uses Large Language Models (LLMs) which may occasionally produce inaccurate information. Please verify and double-check all results before making business decisions.
    """)

    # Submit button
    if st.button("Start Analysis Workflow", type="primary"):
        if user_text:
            # Prepare payload
            payload = {"query": user_text}

            # Create placeholder for streaming text
            response_placeholder = st.empty()
            status_placeholder = st.empty()

            try:
                status_placeholder.info("🔄 Sending request...")

                # Make POST request to /stream endpoint
                response = requests.post(
                    f"{api_url}/stream",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key
                    },
                    stream=True,
                    timeout=240
                )

                if response.status_code == 200:
                    status_placeholder.success(
                        "✅ Connected! Receiving response...")

                    # Display format options
                    format_col1, format_col2, format_col3 = st.columns(3)
                    with format_col1:
                        display_format = st.selectbox("Display as:",
                                                      ["Auto-detect", "Markdown",
                                                       "Plain Text", "Code",
                                                       "JSON"], index=0)

                    # Handle streaming response
                    full_response = ""

                    # Check if response is streaming (chunked)
                    if response.headers.get('transfer-encoding') == 'chunked':
                        for chunk in response.iter_content(chunk_size=1024,
                                                           decode_unicode=True):
                            if chunk:
                                full_response += chunk
                                display_response(response_placeholder,
                                                 full_response, display_format,
                                                 "Streaming Response",
                                                 preserve_formatting)
                                if auto_scroll:
                                    time.sleep(
                                        0.05)  # Small delay for visual effect
                    else:
                        # Handle regular response
                        try:
                            # Try to parse as JSON first
                            result = response.json()
                            full_response = extract_text_from_response(result)
                        except:
                            # If not JSON, treat as plain text
                            full_response = response.text

                        display_response(response_placeholder, full_response,
                                         display_format, "Response",
                                         preserve_formatting)

                    status_placeholder.success("✅ Complete!")

                else:
                    status_placeholder.error(
                        f"❌ Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                status_placeholder.error(
                    "❌ Could not connect to API. Check if server is running.")
            except requests.exceptions.Timeout:
                status_placeholder.error("❌ Request timed out.")
            except Exception as e:
                status_placeholder.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter some text first.")