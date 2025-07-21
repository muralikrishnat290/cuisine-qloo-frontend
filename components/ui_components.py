"""
UI components for Kitchen Intel application.

This module provides reusable UI components and layout utilities
for consistent application styling and user experience.
"""
import streamlit as st
from typing import Optional, Dict, Any


def render_app_header() -> None:
    """Render the main application header with title and description."""
    st.title("🍜 Kitchen Intel")
    
    # Comprehensive app description with attractive formatting
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.8); padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
        <h3 style="color: #2c3e50; margin-top: 0; margin-bottom: 0.8rem; font-family: 'Poppins', sans-serif;">🚀 AI-Powered Food & Cuisine Business Intelligence</h3>
        <p style="font-size: 1.1rem; color: #34495e; margin-bottom: 1rem; line-height: 1.6; font-family: 'Inter', sans-serif;">
            Transform your restaurant and food business strategy with comprehensive AI-driven analysis. Get deep insights into market performance, demographic trends, and location-based opportunities for any cuisine type in any city worldwide.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_mvp_notice() -> None:
    """Render the MVP notice banner."""
    st.markdown("""
    <div style="background: linear-gradient(45deg, #FFF3E0, #FFECB3); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 10px; padding: 0rem; margin: 0rem 0;">
        <p style="margin: 0; color: #E65100; font-size: 0.9rem;">
            <strong>💡 MVP Notice:</strong> This is a Minimum Viable Product designed for single-session use. Your queries and responses are not saved between sessions, ensuring privacy while providing powerful business insights for immediate decision-making.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer() -> None:
    """Render the application disclaimer."""
    st.markdown("""
    ⚠️ **Disclaimer:** This tool uses Large Language Models (LLMs) which may occasionally produce inaccurate information. Please verify and double-check all results before making business decisions.
    """)


def render_sidebar_settings() -> Dict[str, Any]:
    """
    Render sidebar settings and return configuration.
    
    Returns:
        Dictionary containing user settings
    """
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        auto_scroll = st.checkbox("Auto-scroll", value=True)
        preserve_formatting = st.checkbox("Preserve formatting", value=True)
        
        return {
            'auto_scroll': auto_scroll,
            'preserve_formatting': preserve_formatting
        }


def render_input_section() -> Dict[str, str]:
    """
    Render the input section for cuisine and city.
    
    Returns:
        Dictionary containing user inputs
    """
    st.markdown("### 🍽️ Start Your Analysis")
    
    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        cuisine_input = st.text_input(
            "🍽️ Cuisine Type", 
            placeholder="e.g., chinese, italian...", 
            help="Enter the type of cuisine you want to analyze"
        )
    with col2:
        city_input = st.text_input(
            "🏙️ City", 
            placeholder="e.g., Stuttgart, Delhi, New York...", 
            help="Enter the city for the analysis"
        )
    
    return {
        'cuisine': cuisine_input,
        'city': city_input
    }


def render_action_buttons(has_existing_results: bool = False) -> Dict[str, bool]:
    """
    Render action buttons for starting analysis.
    
    Args:
        has_existing_results: Whether there are existing results to show
        
    Returns:
        Dictionary containing button states
    """
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        start_analysis_clicked = st.button(
            "Start Analysis Workflow", 
            type="primary", 
            key="start_analysis_btn", 
            use_container_width=True
        )
    
    with button_col2:
        if has_existing_results:
            start_new_clicked = st.button(
                "🔄 Start New Analysis", 
                type="secondary", 
                key="start_new_analysis_btn", 
                use_container_width=True
            )
        else:
            start_new_clicked = False
    
    return {
        'start_analysis': start_analysis_clicked,
        'start_new': start_new_clicked
    }


def validate_inputs(cuisine: str, city: str) -> Optional[str]:
    """
    Validate user inputs and return error message if invalid.
    
    Args:
        cuisine: Cuisine type input
        city: City input
        
    Returns:
        Error message string or None if valid
    """
    if not cuisine.strip():
        return "🍽️ Please enter a cuisine type"
    if not city.strip():
        return "🏙️ Please enter a city name"
    return None


def show_error_message(message: str) -> None:
    """Show error message in a consistent format."""
    st.error(message)


def show_success_message(message: str) -> None:
    """Show success message in a consistent format."""
    st.success(message)


def show_info_message(message: str) -> None:
    """Show info message in a consistent format."""
    st.info(message)


def show_warning_message(message: str) -> None:
    """Show warning message in a consistent format."""
    st.warning(message)


def create_containers() -> Dict[str, st.container]:
    """
    Create and return organized containers for the application layout.
    
    Returns:
        Dictionary containing named containers
    """
    return {
        'streaming': st.container(),
        'map': st.container(),
        'results': st.container()
    }


def render_loading_state(message: str = "Processing...") -> None:
    """
    Render a loading state with spinner.
    
    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        st.empty()


def render_divider() -> None:
    """Render a visual divider."""
    st.divider()


def clear_session_keys(keys_to_clear: list) -> None:
    """
    Clear specified keys from session state.
    
    Args:
        keys_to_clear: List of session state keys to clear
    """
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def check_existing_results() -> bool:
    """
    Check if there are existing results in session state.
    
    Returns:
        True if existing results are found
    """
    return (st.session_state.get('final_response') and 
            st.session_state.get('response_format') and 
            not st.session_state.get('analysis_in_progress', False))


def prepare_analysis_payload(cuisine: str, city: str) -> Dict[str, str]:
    """
    Prepare payload for analysis request.
    
    Args:
        cuisine: Cuisine type
        city: City name
        
    Returns:
        Dictionary containing the analysis payload
    """
    combined_query = f"how {cuisine.strip()} performs in {city.strip()}"
    return {"query": combined_query}


def update_session_state(updates: Dict[str, Any]) -> None:
    """
    Update multiple session state values.
    
    Args:
        updates: Dictionary of key-value pairs to update in session state
    """
    for key, value in updates.items():
        st.session_state[key] = value