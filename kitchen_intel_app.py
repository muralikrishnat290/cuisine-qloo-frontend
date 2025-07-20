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
import streamlit.components.v1 as components

load_dotenv()
# Configuration
api_url = os.getenv("API_URL", "http://localhost:8080")
api_key = os.getenv("API_KEY", "sample-key")


def auto_scroll_to_bottom():
    """Inject JavaScript to auto-scroll to the bottom of the page"""
    scroll_script = """
    <script>
        function scrollToBottom() {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }
        
        // Scroll immediately
        scrollToBottom();
        
        // Also scroll after a short delay to catch any dynamic content
        setTimeout(scrollToBottom, 100);
        setTimeout(scrollToBottom, 300);
    </script>
    """
    components.html(scroll_script, height=0, width=0)


def auto_scroll_to_element(element_id):
    """Inject JavaScript to auto-scroll to a specific element"""
    scroll_script = f"""
    <script>
        function scrollToElement() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center'
                }});
            }} else {{
                window.scrollTo({{
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                }});
            }}
        }}
        
        // Scroll immediately
        scrollToElement();
        
        // Also scroll after a short delay to catch any dynamic content
        setTimeout(scrollToElement, 100);
        setTimeout(scrollToElement, 300);
    </script>
    """
    components.html(scroll_script, height=0, width=0)


def reduce_map_spacing():
    """Inject CSS to reduce spacing around map components"""
    css_script = """
    <style>
        /* Reduce spacing around Streamlit map components */
        .stMap > div {
            margin-bottom: 0.5rem !important;
        }
        
        /* Reduce spacing around folium maps */
        iframe[title*="map"] {
            margin-bottom: 0.5rem !important;
        }
        
        /* Reduce spacing around buttons after maps */
        .stButton > button {
            margin-top: 0.5rem !important;
        }
        
        /* Reduce overall container spacing */
        .stContainer > div {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }
    </style>
    """
    components.html(css_script, height=0, width=0)


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
        elif '**' in content or '#' in content or '*' in content or '<' in content:
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

def render_map(map_details):
    """
    Render interactive map with location data from API response.
    
    Args:
        map_details: JSON string containing API response with location data
    """
    # Initialize error tracking
    conversion_errors = []
    validation_errors = []
    
    try:
        # Parse JSON response with detailed error handling
        try:
            map_object = json.loads(map_details)
        except json.JSONDecodeError as e:
            _handle_json_parse_error(e, map_details)
            return
        
        # Validate response structure
        if not isinstance(map_object, dict):
            st.error("❌ Invalid API response format: Expected JSON object")
            _show_fallback_response_info(map_details)
            return
        
        # Extract location data from the response with comprehensive error handling
        location_data = []
        raw_data_found = False
        
        # Try multiple extraction strategies
        extraction_strategies = [
            ("location", "Direct location field"),
            ("locations", "Locations array"),
            ("results", "Results array"),
            ("data", "Data array"),
            ("items", "Items array")
        ]
        
        for field_name, description in extraction_strategies:
            if field_name in map_object:
                raw_data_found = True
                raw_locations = map_object[field_name]
                
                # Handle different data structures
                if isinstance(raw_locations, list):
                    for i, item in enumerate(raw_locations):
                        converted_item = _convert_api_data_to_location_data(item)
                        if converted_item:
                            location_data.append(converted_item)
                        else:
                            conversion_errors.append(f"Item {i} in '{field_name}': Could not convert to location data")
                            
                elif isinstance(raw_locations, dict):
                    # Single location object
                    converted_item = _convert_api_data_to_location_data(raw_locations)
                    if converted_item:
                        location_data.append(converted_item)
                    else:
                        conversion_errors.append(f"Single item in '{field_name}': Could not convert to location data")
                
                # If we found data in this field, stop looking
                if location_data:
                    break
        
        # Validate extracted location data
        if location_data:
            from components.data_models import validate_location_data
            is_valid, validation_errors = validate_location_data(location_data)
            
            if not is_valid:
                st.warning("⚠️ Some location data failed validation but will attempt to render valid entries")
                with st.expander("🔍 Validation Issues"):
                    for error in validation_errors[:10]:  # Show first 10 errors
                        st.text(f"• {error}")
                    if len(validation_errors) > 10:
                        st.text(f"... and {len(validation_errors) - 10} more validation errors")
        
        # Display the map if we have valid location data
        if location_data:
            _render_map_with_data(location_data, conversion_errors)
            
        else:
            # No valid location data found - provide comprehensive feedback
            _handle_no_location_data_error(map_object, raw_data_found, conversion_errors, extraction_strategies)
                
    except ImportError as e:
        _handle_import_error(e)
        
    except Exception as e:
        _handle_general_map_error(e, map_details, conversion_errors, validation_errors)


def _handle_json_parse_error(error, raw_data):
    """Handle JSON parsing errors with user-friendly feedback."""
    st.error("❌ Failed to parse API response as JSON")
    st.error(f"JSON Error: {str(error)}")
    
    # Provide helpful suggestions
    st.info("**Possible solutions:**")
    st.write("• Check if the API is returning valid JSON")
    st.write("• Verify the API endpoint is working correctly")
    st.write("• Try the request again in a few moments")
    
    with st.expander("🔍 View Raw Response"):
        st.text(raw_data[:1000] + "..." if len(raw_data) > 1000 else raw_data)


def _handle_import_error(error):
    """Handle missing dependency errors."""
    st.error("❌ Missing required dependencies for map rendering")
    st.error(f"Import Error: {str(error)}")
    
    st.info("**Required dependencies:**")
    st.code("""
pip install streamlit-folium folium
    """)
    
    st.write("Please install the required packages and restart the application.")


def _handle_no_location_data_error(map_object, raw_data_found, conversion_errors, extraction_strategies):
    """Handle cases where no valid location data is found."""
    if not raw_data_found:
        st.warning("⚠️ No location data found in the API response.")
        st.info("The API response doesn't contain location information in expected fields.")
        
        # Show what fields were searched
        searched_fields = [strategy[0] for strategy in extraction_strategies]
        st.write(f"**Searched fields:** {', '.join(searched_fields)}")
        
        # Show available fields in response
        if isinstance(map_object, dict):
            available_fields = list(map_object.keys())
            st.write(f"**Available fields:** {', '.join(available_fields)}")
    else:
        st.error("❌ Found location data but failed to convert to valid format")
        
        if conversion_errors:
            with st.expander("🔍 Conversion Errors"):
                for error in conversion_errors[:10]:
                    st.text(f"• {error}")
                if len(conversion_errors) > 10:
                    st.text(f"... and {len(conversion_errors) - 10} more errors")
    
    # Always show raw response for debugging
    with st.expander("🔍 View Raw API Response"):
        st.json(map_object)
    
    # Provide guidance
    st.info("**Expected location data format:**")
    st.code("""
{
  "location": [
    {
      "location": "Place Name",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "affinity": 0.85,
      "affinity_rank": 0.92,
      "popularity": 0.78
    }
  ]
}
    """)


def _handle_general_map_error(error, map_details, conversion_errors, validation_errors):
    """Handle general map rendering errors."""
    st.error("❌ Error rendering map")
    st.error(f"Error: {str(error)}")
    
    # Show error context
    error_context = {
        "Error Type": type(error).__name__,
        "Error Message": str(error),
        "Conversion Errors": len(conversion_errors),
        "Validation Errors": len(validation_errors)
    }
    
    with st.expander("🔍 Error Details"):
        for key, value in error_context.items():
            st.write(f"**{key}:** {value}")
        
        if conversion_errors:
            st.write("**Conversion Issues:**")
            for error in conversion_errors[:5]:
                st.text(f"• {error}")
        
        if validation_errors:
            st.write("**Validation Issues:**")
            for error in validation_errors[:5]:
                st.text(f"• {error}")
    
    # Show debug information
    with st.expander("🔍 Debug Information"):
        st.text("Raw map_details:")
        st.text(map_details[:500] + "..." if len(map_details) > 500 else map_details)


def _render_map_with_data(location_data, conversion_errors):
    """Render the map with valid location data."""
    try:
        st.subheader("📍 Location Analysis Map")
        
        # Show data quality summary
        if conversion_errors:
            st.info(f"ℹ️ Successfully processed {len(location_data)} locations ({len(conversion_errors)} items skipped due to data issues)")
        else:
            st.success(f"✅ Successfully processed {len(location_data)} locations")
        
        # Import map components with error handling
        try:
            from components.streamlit_map_integration import display_map_component, display_map_controls
        except ImportError as e:
            st.error("❌ Failed to import map components")
            st.error(f"Import Error: {str(e)}")
            st.info("Please ensure all map dependencies are installed correctly.")
            return
        
        # Display map controls for user interaction
        try:
            control_settings = display_map_controls(location_data, key="main_map_controls")
        except Exception as e:
            st.warning("⚠️ Map controls failed to load, using default settings")
            control_settings = {'filtered_data': location_data, 'map_height': 600}
        
        # Use filtered data from controls
        filtered_data = control_settings.get('filtered_data', location_data)
        
        # Display the map component with comprehensive error handling
        try:
            map_result = display_map_component(
                filtered_data,
                key="main_demographic_map",
                height=control_settings.get('map_height', 600)
            )
            
            # Display summary information
            if map_result.get("status") == "success":
                print("Successfully rendered map")
            elif map_result.get("error"):
                st.error(f"Map component error: {map_result['error']}")
                _show_map_fallback_options(location_data)
                
        except Exception as map_error:
            st.error(f"❌ Map rendering failed: {str(map_error)}")
            _show_map_fallback_options(location_data)
            
    except Exception as e:
        st.error(f"❌ Unexpected error in map rendering: {str(e)}")
        _show_map_fallback_options(location_data)




def _show_map_fallback_options(location_data):
    """Show fallback options when map rendering fails."""
    st.info("**Alternative ways to view your location data:**")
    
    # Show data table
    with st.expander("📊 View Location Data Table"):
        import pandas as pd
        try:
            df = pd.DataFrame(location_data)
            st.dataframe(df)
        except Exception:
            st.json(location_data)
    
    # Show coordinates list
    with st.expander("📍 View Coordinates List"):
        for i, item in enumerate(location_data):
            st.write(f"{i+1}. **{item.get('location', 'Unknown')}**")
            st.write(f"   Coordinates: {item.get('latitude', 'N/A')}, {item.get('longitude', 'N/A')}")
            st.write(f"   Affinity: {item.get('affinity', 0):.1%}")


def _show_fallback_response_info(raw_data):
    """Show fallback information when response parsing fails."""
    st.info("**Troubleshooting steps:**")
    st.write("1. Check if the API is returning valid JSON")
    st.write("2. Verify the API endpoint configuration")
    st.write("3. Try the request again")
    
    with st.expander("🔍 View Raw Response"):
        st.text(raw_data[:1000] + "..." if len(raw_data) > 1000 else raw_data)


def _convert_api_data_to_location_data(api_item):
    """
    Convert API response item to LocationData format.
    
    Args:
        api_item: Dictionary from API response
        
    Returns:
        Dictionary in LocationData format or None if conversion fails
    """
    if not isinstance(api_item, dict):
        return None
    
    try:
        # Extract location name - try various field names
        location_name = None
        for name_field in ["location", "name", "place", "address", "city", "title"]:
            if name_field in api_item and api_item[name_field]:
                location_name = str(api_item[name_field]).strip()
                break
        
        if not location_name:
            return None
        
        # Extract coordinates - try various field names
        latitude = None
        longitude = None
        
        # Try direct lat/lon fields
        for lat_field in ["latitude", "lat", "y"]:
            if lat_field in api_item:
                try:
                    latitude = float(api_item[lat_field])
                    break
                except (TypeError, ValueError):
                    continue
        
        for lon_field in ["longitude", "lon", "lng", "x"]:
            if lon_field in api_item:
                try:
                    longitude = float(api_item[lon_field])
                    break
                except (TypeError, ValueError):
                    continue
        
        # Try coordinates array format
        if latitude is None or longitude is None:
            if "coordinates" in api_item and isinstance(api_item["coordinates"], list):
                coords = api_item["coordinates"]
                if len(coords) >= 2:
                    try:
                        # GeoJSON format is [longitude, latitude]
                        longitude = float(coords[0])
                        latitude = float(coords[1])
                    except (TypeError, ValueError, IndexError):
                        pass
        
        # Validate coordinates
        if latitude is None or longitude is None:
            return None
            
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return None
        
        # Extract metrics - try various field names with defaults
        affinity = _extract_numeric_field(api_item, ["affinity", "score", "rating", "relevance"], 0.5)
        affinity_rank = _extract_numeric_field(api_item, ["affinity_rank", "rank", "ranking", "position"], 0.5)
        popularity = _extract_numeric_field(api_item, ["popularity", "popular", "frequency", "count", "weight"], 0.5)
        
        # Normalize metrics to 0-1 range
        affinity = max(0.0, min(1.0, affinity))
        affinity_rank = max(0.0, min(1.0, affinity_rank))
        popularity = max(0.0, min(1.0, popularity))
        
        return {
            'location': location_name,
            'latitude': latitude,
            'longitude': longitude,
            'affinity': affinity,
            'affinity_rank': affinity_rank,
            'popularity': popularity
        }
        
    except Exception as e:
        # Log the error but don't fail the entire process
        print(f"Warning: Failed to convert API item to LocationData: {e}")
        return None


def _extract_numeric_field(data_dict, field_names, default_value):
    """
    Extract numeric value from dictionary trying multiple field names.
    
    Args:
        data_dict: Dictionary to search
        field_names: List of field names to try
        default_value: Default value if no valid field found
        
    Returns:
        Numeric value or default_value
    """
    for field_name in field_names:
        if field_name in data_dict:
            try:
                value = float(data_dict[field_name])
                return value
            except (TypeError, ValueError):
                continue
    
    return default_value


def render_simple_map(map_details):
    """
    Render a simple, lightweight map that won't cause page reruns.
    
    Args:
        map_details: JSON string containing API response with location data
    """
    try:
        # Parse JSON response
        try:
            map_object = json.loads(map_details)
        except json.JSONDecodeError as e:
            st.error("❌ Failed to parse API response as JSON")
            st.error(f"JSON Error: {str(e)}")
            return
        
        # Extract location data using the same logic as the complex map
        location_data = []
        extraction_strategies = [
            ("location", "Direct location field"),
            ("locations", "Locations array"),
            ("results", "Results array"),
            ("data", "Data array"),
            ("items", "Items array")
        ]
        
        for field_name, description in extraction_strategies:
            if field_name in map_object:
                raw_locations = map_object[field_name]
                
                if isinstance(raw_locations, list):
                    for item in raw_locations:
                        converted_item = _convert_api_data_to_location_data(item)
                        if converted_item:
                            location_data.append(converted_item)
                elif isinstance(raw_locations, dict):
                    converted_item = _convert_api_data_to_location_data(raw_locations)
                    if converted_item:
                        location_data.append(converted_item)
                
                if location_data:
                    break
        
        if not location_data:
            st.warning("⚠️ No valid location data found in the API response.")
            with st.expander("🔍 View Raw API Response"):
                st.json(map_object)
            return
        
        # Display map with traditional location markers using Folium
        st.subheader("📍 Location Analysis Map")
        
        # Apply CSS to reduce spacing around map components
        reduce_map_spacing()
        
        try:
            import folium
            from streamlit_folium import st_folium
            
            # Calculate center point for the map
            center_lat = sum(item['latitude'] for item in location_data) / len(location_data)
            center_lon = sum(item['longitude'] for item in location_data) / len(location_data)
            
            # Create Folium map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # Add traditional markers for each location
            for item in location_data:
                # Color based on popularity
                popularity = item['popularity']
                if popularity >= 0.7:
                    color = 'green'  # High popularity
                elif popularity >= 0.5:
                    color = 'orange'  # Medium popularity  
                elif popularity >= 0.3:
                    color = 'red'  # Low-medium popularity
                else:
                    color = 'darkred'  # Low popularity
                
                # Icon size based on affinity
                if item['affinity'] >= 0.7:
                    icon_size = 'large'
                elif item['affinity'] >= 0.4:
                    icon_size = 'medium'
                else:
                    icon_size = 'small'
                
                # Create detailed popup with all metrics
                popup_text = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">{item['location']}</h4>
                    <hr style="margin: 5px 0;">
                    <p style="margin: 3px 0;"><b>📊 Affinity:</b> {item['affinity']:.1%}</p>
                    <p style="margin: 3px 0;"><b>🏆 Affinity Rank:</b> {item['affinity_rank']:.1%}</p>
                    <p style="margin: 3px 0;"><b>⭐ Popularity:</b> {item['popularity']:.1%}</p>
                    <hr style="margin: 5px 0;">
                    <p style="margin: 3px 0; font-size: 12px; color: #666;">
                        📍 {item['latitude']:.4f}, {item['longitude']:.4f}
                    </p>
                </div>
                """
                
                # Create enhanced tooltip for hover
                tooltip_text = f"""
                <div style="font-family: Arial, sans-serif;">
                    <b>{item['location']}</b><br>
                    Affinity: {item['affinity']:.1%} | Rank: {item['affinity_rank']:.1%} | Popularity: {item['popularity']:.1%}
                </div>
                """
                
                # Add traditional location marker with enhanced hover details
                folium.Marker(
                    location=[item['latitude'], item['longitude']],
                    popup=folium.Popup(popup_text, max_width=250),
                    tooltip=folium.Tooltip(tooltip_text, sticky=True),
                    icon=folium.Icon(
                        color=color,
                        icon='map-marker',
                        prefix='fa'
                    )
                ).add_to(m)
            
            # Display the map with maximum width
            st_folium(m, width=None, height=500)  # Reduced height from 600 to 500
            
        except ImportError:
            st.warning("⚠️ Folium not available. Using fallback map with dot markers.")
            # Fallback to st.map if Folium is not available
            import pandas as pd
            
            map_data = []
            for item in location_data:
                size = int(15 + (item['affinity'] * 25))  # 15-40 pixel range
                
                popularity = item['popularity']
                if popularity >= 0.7:
                    color = '#00FF00'  # Green for high popularity
                elif popularity >= 0.5:
                    color = '#FFFF00'  # Yellow for medium popularity  
                elif popularity >= 0.3:
                    color = '#FFA500'  # Orange for low-medium popularity
                else:
                    color = '#FF0000'  # Red for low popularity
                
                map_data.append({
                    'lat': item['latitude'],
                    'lon': item['longitude'],
                    'size': size,
                    'color': color
                })
            
            map_df = pd.DataFrame(map_data)
            st.map(map_df, size='size', color='color', height=400)  # Set specific height for fallback map
        
    except Exception as e:
        st.error(f"❌ Error rendering simple map: {str(e)}")
        st.info("**Troubleshooting:**")
        st.write("• The location data might be in an unexpected format")
        st.write("• Some coordinates might be invalid")
        
        with st.expander("🔍 Debug Information"):
            st.text(f"Error: {str(e)}")
            st.text("Raw map_details:")
            st.text(map_details[:500] + "..." if len(map_details) > 500 else map_details)

def render_authenticated_app():
    """Render the main Kitchen Intel application for authenticated users."""
    # Page config is handled by the app wrapper, so we don't set it here
    
    # Title
    st.title("🍜 Kitchen Intel")
    
    # App description
    st.markdown("""
    **Analyze food & cuisine business performance with AI-powered insights**
    
    Get comprehensive analysis of restaurant and food business performance, market trends, and location-based insights for any cuisine type in any city. This tool leverages advanced language models to provide sales analysis, demographic insights, and interactive location mapping for food businesses.
    """)

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

    # Separate inputs for cuisine and city
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            cuisine_input = st.text_input("🍽️ Cuisine Type", placeholder="e.g., chinese, italian...", help="Enter the type of cuisine you want to analyze")
        with col2:
            city_input = st.text_input("🏙️ City", placeholder="e.g., Stuttgart, Delhi, New York...", help="Enter the city for the analysis")

    # Disclaimer
    st.markdown("""
    ⚠️ **Disclaimer:** This tool uses Large Language Models (LLMs) which may occasionally produce inaccurate information. Please verify and double-check all results before making business decisions.
    """)

    # Button area - positioned immediately after inputs and before any output
    button_col1, button_col2 = st.columns(2)
    
    # Check if we have existing results to show both buttons
    has_existing_results = (st.session_state.get('final_response') and 
                           st.session_state.get('response_format') and 
                           not st.session_state.get('analysis_in_progress', False))
    
    with button_col1:
        start_analysis_clicked = st.button("Start Analysis Workflow", type="primary", key="start_analysis_btn", use_container_width=True)
    
    with button_col2:
        if has_existing_results:
            start_new_clicked = st.button("🔄 Start New Analysis", type="secondary", key="start_new_analysis_btn", use_container_width=True)
        else:
            start_new_clicked = False

    # Create containers for organized layout - MUST be created before button logic
    streaming_container = st.container()
    map_container = st.container()

    # Handle button clicks
    if start_analysis_clicked or start_new_clicked:
        # If it's a new analysis request, clear all data first
        if start_new_clicked:
            keys_to_clear = [
                'pending_map_task_id', 'show_map_button', 'map_data', 'show_map', 
                'current_query', 'analysis_complete', 'analysis_in_progress',
                'final_response', 'response_format', 'preserve_formatting'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # Validate inputs for new analysis
        if not cuisine_input.strip():
            with streaming_container:
                st.error("🍽️ Please enter a cuisine type")
            st.stop()
        if not city_input.strip():
            with streaming_container:
                st.error("🏙️ Please enter a city name")
            st.stop()
            
        # Clear ALL previous analysis data
        keys_to_clear = [
            'pending_map_task_id', 'show_map_button', 'map_data', 'show_map', 
            'current_query', 'analysis_complete', 'analysis_in_progress',
            'final_response', 'response_format', 'preserve_formatting'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Combine inputs into query format
        combined_query = f"how {cuisine_input.strip()} performs in {city_input.strip()}"
        
        # Store current query to track state
        st.session_state['current_query'] = combined_query
        st.session_state['analysis_in_progress'] = True
        
        # Prepare payload
        start_payload = {"query": combined_query}
        
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
                                    render_simple_map(map_data)
                                    
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
    if (st.session_state.get('final_response') and 
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
                render_simple_map(st.session_state['map_data'])
                
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
                            render_simple_map(st.session_state['map_data'])
                            
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