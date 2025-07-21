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

# Import modular components
from components.ui_components import (
    render_app_header, render_mvp_notice, render_disclaimer,
    render_sidebar_settings, render_input_section, render_action_buttons,
    validate_inputs, show_error_message, create_containers, render_divider,
    clear_session_keys, check_existing_results, prepare_analysis_payload,
    update_session_state
)
from components.response_handler import display_response, extract_text_from_response
from components.comprehensive_map_renderer import render_map, render_lightweight_map
from styles.scroll.autoscroll import auto_scroll_to_bottom, auto_scroll_to_element

load_dotenv()

# Configuration
api_url = os.getenv("API_URL", "http://localhost:8080")
api_key = os.getenv("API_KEY", "sample-key")


# These functions are now imported from components.response_handler

# render_map function is now imported from components.comprehensive_map_renderer


# These functions are now handled by the modular components:
# - Error handling functions moved to components.map_error_handler
# - Map rendering functions moved to components.comprehensive_map_renderer
# - Data conversion functions moved to components.map_data_converter

def render_authenticated_app():
    """Render the main Kitchen Intel application for authenticated users."""
    # Render UI components using modular approach
    render_app_header()
    render_mvp_notice()
    
    # Render sidebar settings
    settings = render_sidebar_settings()
    auto_scroll = settings['auto_scroll']
    preserve_formatting = settings['preserve_formatting']
    
    # Render input section
    inputs = render_input_section()
    cuisine_input = inputs['cuisine']
    city_input = inputs['city']
    
    # Render disclaimer
    render_disclaimer()
    
    # Check for existing results and render action buttons
    has_existing_results = check_existing_results()
    buttons = render_action_buttons(has_existing_results)
    start_analysis_clicked = buttons['start_analysis']
    start_new_clicked = buttons['start_new']
    
    # Render divider
    render_divider()
    
    # Create containers for organized layout
    containers = create_containers()
    streaming_container = containers['streaming']
    map_container = containers['map']

    # Handle button clicks
    if start_analysis_clicked or start_new_clicked:
        # Handle new analysis request
        if start_new_clicked:
            keys_to_clear = [
                'pending_map_task_id', 'show_map_button', 'map_data', 'show_map', 
                'current_query', 'analysis_complete', 'analysis_in_progress',
                'final_response', 'response_format', 'preserve_formatting'
            ]
            clear_session_keys(keys_to_clear)
            st.rerun()
        
        # Validate inputs using modular validation
        error_message = validate_inputs(cuisine_input, city_input)
        if error_message:
            with streaming_container:
                show_error_message(error_message)
            st.stop()
            
        # Clear previous analysis data
        keys_to_clear = [
            'pending_map_task_id', 'show_map_button', 'map_data', 'show_map', 
            'current_query', 'analysis_complete', 'analysis_in_progress',
            'final_response', 'response_format', 'preserve_formatting'
        ]
        clear_session_keys(keys_to_clear)
        
        # Prepare analysis payload using modular function
        start_payload = prepare_analysis_payload(cuisine_input, city_input)
        combined_query = start_payload["query"]
        
        # Update session state using modular function
        update_session_state({
            'current_query': combined_query,
            'analysis_in_progress': True
        })
        
        try:
            start_response = requests.post(
                f"{api_url}/start",
                json=start_payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                }
            )
            
            with streaming_container:
                # Initialize streaming content area
                display_format = "Auto-detect"
                
                # Create status area and response area in proper order
                status_info = st.info("🔄 Sending request...")
                response_placeholder = st.empty()

                try:
                    # Make POST request to /stream endpoint
                    response = requests.post(
                        f"{api_url}/stream",
                        json=json.loads(start_response.content.decode('utf-8')),
                        headers={
                            "Content-Type": "application/json",
                            "x-api-key": api_key
                        },
                        stream=True,
                        timeout=240
                    )
         
                    if response.status_code == 200:
                        # Update status without clearing previous content
                        status_info.success("✅ Connected! Receiving response...")
                        
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
                                        time.sleep(0.05)  # Small delay for visual effect
                                        auto_scroll_to_bottom()  # Auto-scroll to latest content
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
                            
                            if auto_scroll:
                                auto_scroll_to_bottom()  # Auto-scroll to show response

                        # Store the final response and add completion status
                        st.session_state['final_response'] = full_response
                        st.session_state['response_format'] = display_format
                        st.session_state['preserve_formatting'] = preserve_formatting
                        
                        # Analysis completed - update status
                        status_info.success("✅ Analysis completed!")
                        
                        task_id = json.loads(start_response.content.decode("utf-8"))["task_id"]
                        
                        # Auto-generate map in separate container
                        with map_container:
                            st.divider()
                            map_status = st.info("🗺️ Generating location map...")
                        
                            try:
                                # Get the task results immediately
                                end_response = requests.get(
                                    f"{api_url}/tasks/{task_id}",
                                    headers={
                                        "Content-Type": "application/json",
                                        "x-api-key": api_key
                                    }
                                )
                                
                                if end_response.status_code == 200:
                                    # Store map data and render immediately
                                    map_data = end_response.content.decode('utf-8')
                                    st.session_state['map_data'] = map_data
                                    st.session_state['show_map'] = True
                                    st.session_state['analysis_in_progress'] = False
                                    st.session_state['analysis_complete'] = True
                                    
                                    map_status.success("✅ Map generated successfully!")
                                    render_lightweight_map(map_data)
                                    
                                    # Auto-scroll to show the map
                                    if auto_scroll:
                                        auto_scroll_to_bottom()
                                    
                                    # Option to hide the map - minimal spacing
                                    col1, col2, col3 = st.columns([2, 1, 2])
                                    with col2:
                                        if st.button("🗺️ Hide Map", use_container_width=True, key="hide_map_btn"):
                                            st.session_state['show_map'] = False
                                            st.rerun()
                                    
                                else:
                                    map_status.error(f"❌ Failed to fetch map data: {end_response.status_code}")
                                    
                            except Exception as map_error:
                                map_status.error(f"❌ Failed to generate map: {str(map_error)}")

                    else:
                        st.error(f"❌ Error {response.status_code}: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to API. Check if server is running.")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
        except Exception as outer_error:
            with streaming_container:
                st.error(f"❌ Failed to start analysis: {str(outer_error)}")
    
    # Display any existing streaming content from previous analysis
    elif (st.session_state.get('final_response') and 
          st.session_state.get('response_format') and 
          not st.session_state.get('analysis_in_progress', False) and
          not start_analysis_clicked and not start_new_clicked):
        
        with streaming_container:
            # Display the stored response
            response_placeholder = st.empty()
            display_response(response_placeholder, st.session_state['final_response'],
                           st.session_state['response_format'], "Analysis Results",
                           st.session_state.get('preserve_formatting', True))
            
            # Auto-scroll to show existing results when page loads
            if auto_scroll:
                auto_scroll_to_bottom()
        
        # Display map only if it's been generated and is set to show
        if (st.session_state.get('show_map', False) and 
            st.session_state.get('map_data') and 
            st.session_state.get('analysis_complete', False)):
            
            with map_container:
                st.divider()
                render_lightweight_map(st.session_state['map_data'])
                
                # Auto-scroll to show the map for existing results
                if auto_scroll:
                    auto_scroll_to_bottom()
                
                # Option to hide the map - minimal spacing
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("🗺️ Hide Map", use_container_width=True, key="hide_map_existing_btn"):
                        st.session_state['show_map'] = False
                        st.rerun()
    
    # Show map rendering button if there's a pending task (only when not running new analysis)
    if (st.session_state.get('show_map_button', False) and 
        st.session_state.get('pending_map_task_id') and
        not start_analysis_clicked and not start_new_clicked):
        
        with map_container:
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🗺️ Generate Location Map", type="secondary", use_container_width=True):
                    try:
                        # Get the task results
                        task_id = st.session_state['pending_map_task_id']
                        end_response = requests.get(
                            f"{api_url}/tasks/{task_id}",
                            headers={
                                "Content-Type": "application/json",
                                "x-api-key": api_key
                            }
                        )
                        
                        if end_response.status_code == 200:
                            # Store map data in session state and render map immediately
                            st.session_state['map_data'] = end_response.content.decode('utf-8')
                            st.session_state['show_map'] = True
                            st.session_state['show_map_button'] = False
                            st.session_state['pending_map_task_id'] = None
                            
                            # Render map immediately without page refresh
                            st.divider()
                            render_lightweight_map(st.session_state['map_data'])
                            
                            # Auto-scroll to show the manually generated map
                            if auto_scroll:
                                auto_scroll_to_bottom()
                            
                            # Add hide map button for manually generated map - minimal spacing
                            hide_col1, hide_col2, hide_col3 = st.columns([2, 1, 2])
                            with hide_col2:
                                if st.button("🗺️ Hide Map", use_container_width=True, key="hide_manual_map_btn"):
                                    st.session_state['show_map'] = False
                                    st.rerun()
                            
                        else:
                            st.error(f"❌ Failed to fetch task results: {end_response.status_code}")
                            
                    except Exception as map_error:
                        st.error(f"❌ Failed to render map: {str(map_error)}")
            
            # Option to dismiss the map button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("❌ Skip Map Generation", use_container_width=True):
                    st.session_state['show_map_button'] = False
                    st.session_state['pending_map_task_id'] = None
                    st.info("Map generation skipped. You can run a new analysis to get another opportunity to generate a map.")