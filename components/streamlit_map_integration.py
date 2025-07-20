"""
Streamlit integration component for the demography map display feature.
This module handles Streamlit-specific rendering and state management for interactive maps.
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from typing import List, Dict, Any, Optional, Tuple
import logging

from .map_renderer import MapRenderer
from .data_models import validate_location_data


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_map_component(
    data: List[Dict[str, Any]], 
    container: Optional[st.container] = None,
    key: Optional[str] = None,
    height: int = 600,
    width: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main Streamlit integration function for displaying interactive maps.
    
    This function handles Streamlit container management and component lifecycle
    for rendering demographic maps with location data.
    
    Args:
        data: List of location data dictionaries containing coordinates and metrics
        container: Optional Streamlit container to render the map in
        key: Optional unique key for the Streamlit component
        height: Map height in pixels (default: 600)
        width: Optional map width in pixels (auto-sized if None)
        
    Returns:
        Dictionary containing map interaction data and component state
        
    Raises:
        ValueError: If data validation fails
        RuntimeError: If map rendering fails
    """
    # Use provided container or create a new one
    if container is None:
        container = st.container()
    
    # Generate unique key if not provided
    if key is None:
        key = f"demographic_map_{hash(str(data))}"
    
    with container:
        try:
            # Validate input data
            is_valid, errors = validate_location_data(data)
            if not is_valid:
                st.error("Invalid location data provided:")
                for error in errors[:5]:  # Show first 5 errors
                    st.error(f"• {error}")
                if len(errors) > 5:
                    st.error(f"... and {len(errors) - 5} more errors")
                return {"error": "Data validation failed", "errors": errors}
            
            # Show data summary
            st.info(f"Displaying {len(data)} location(s) on the map")
            
            # Create map renderer with Streamlit-optimized configuration
            map_config = {
                'width': f'{width}px' if width else '100%',
                'height': f'{height}px',
                'tile_layer': 'OpenStreetMap'
            }
            
            renderer = MapRenderer(config=map_config)
            
            # Render the map
            with st.spinner("Rendering map..."):
                folium_map = renderer.render_demographic_map(data)
            
            # Display the map using streamlit-folium
            map_data = st_folium(
                folium_map,
                key=key,
                width=width,
                height=height,
                returned_objects=["last_object_clicked", "last_clicked", "bounds"]
            )
            
            # Handle map interactions
            interaction_data = _handle_map_interactions(map_data, data)
            
            # Display interaction feedback
            if interaction_data.get("clicked_location"):
                _display_location_details(interaction_data["clicked_location"])
            
            return {
                "map_data": map_data,
                "interaction_data": interaction_data,
                "status": "success",
                "data_count": len(data)
            }
            
        except ValueError as e:
            error_msg = f"Data validation error: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            return {"error": error_msg, "status": "validation_failed"}
            
        except RuntimeError as e:
            error_msg = f"Map rendering failed: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
            st.info("Please check your data format and try again.")
            return {"error": error_msg, "status": "render_failed"}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            st.error("An unexpected error occurred while rendering the map.")
            st.error(error_msg)
            return {"error": error_msg, "status": "unexpected_error"}


def _handle_map_interactions(map_data: Dict[str, Any], original_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process user interactions with the map component.
    
    Args:
        map_data: Data returned from st_folium component
        original_data: Original location data for reference
        
    Returns:
        Dictionary containing processed interaction data
    """
    interaction_data = {
        "clicked_location": None,
        "map_bounds": None,
        "last_interaction": None
    }
    
    try:
        # Handle marker clicks
        if map_data.get("last_object_clicked"):
            clicked_data = map_data["last_object_clicked"]
            
            # Find the corresponding location data
            if "lat" in clicked_data and "lng" in clicked_data:
                clicked_lat = clicked_data["lat"]
                clicked_lng = clicked_data["lng"]
                
                # Find matching location in original data (with tolerance for floating point comparison)
                for location in original_data:
                    try:
                        loc_lat = float(location.get("latitude", 0))
                        loc_lng = float(location.get("longitude", 0))
                        
                        # Use small tolerance for coordinate matching
                        if (abs(loc_lat - clicked_lat) < 0.0001 and 
                            abs(loc_lng - clicked_lng) < 0.0001):
                            interaction_data["clicked_location"] = location
                            interaction_data["last_interaction"] = "marker_click"
                            break
                    except (TypeError, ValueError):
                        continue
        
        # Handle map bounds changes
        if map_data.get("bounds"):
            interaction_data["map_bounds"] = map_data["bounds"]
            if not interaction_data["last_interaction"]:
                interaction_data["last_interaction"] = "bounds_change"
        
        # Handle general map clicks
        if map_data.get("last_clicked") and not interaction_data["clicked_location"]:
            interaction_data["last_interaction"] = "map_click"
            
    except Exception as e:
        logger.warning(f"Error processing map interactions: {str(e)}")
    
    return interaction_data


def _display_location_details(location: Dict[str, Any]) -> None:
    """
    Display detailed information about a clicked location.
    
    Args:
        location: Location data dictionary
    """
    try:
        st.subheader("📍 Location Details")
        
        # Create columns for organized display
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Location:** {location.get('location', 'Unknown')}")
            st.write(f"**Coordinates:** {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
        
        with col2:
            affinity = location.get('affinity', 0)
            affinity_rank = location.get('affinity_rank', 0)
            popularity = location.get('popularity', 0)
            
            st.write(f"**Affinity Score:** {affinity:.1%}")
            st.write(f"**Affinity Rank:** {affinity_rank:.1%}")
            st.write(f"**Popularity:** {popularity:.1%}")
        
        # Add visual indicators
        st.progress(affinity, text=f"Affinity: {affinity:.1%}")
        
    except Exception as e:
        logger.warning(f"Error displaying location details: {str(e)}")
        st.warning("Could not display location details")


def handle_map_errors(error_type: str, error_message: str, data: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Handle and display map-related errors in a user-friendly way.
    
    Args:
        error_type: Type of error (validation, rendering, etc.)
        error_message: Detailed error message
        data: Optional data that caused the error for debugging
    """
    st.error(f"Map Error ({error_type})")
    
    if error_type == "validation":
        st.error("The provided data does not meet the required format:")
        st.code(error_message)
        
        if data:
            with st.expander("View problematic data"):
                st.json(data[:3] if len(data) > 3 else data)  # Show first 3 items
                
        st.info("Required data format:")
        st.code("""
[
    {
        "location": "Location Name",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "affinity": 0.85,
        "affinity_rank": 0.92,
        "popularity": 0.78
    }
]
        """)
        
    elif error_type == "rendering":
        st.error("Failed to render the map:")
        st.code(error_message)
        st.info("This might be due to invalid coordinates or missing dependencies.")
        
    else:
        st.error("An unexpected error occurred:")
        st.code(error_message)
        st.info("Please try refreshing the page or contact support if the issue persists.")


def create_map_loading_state() -> None:
    """
    Display a loading state for map rendering.
    """
    with st.container():
        st.info("🗺️ Preparing map visualization...")
        
        # Create placeholder for map
        placeholder = st.empty()
        
        with placeholder.container():
            # Show loading animation
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            import time
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 30:
                    status_text.text("Loading map tiles...")
                elif i < 60:
                    status_text.text("Processing location data...")
                elif i < 90:
                    status_text.text("Rendering markers...")
                else:
                    status_text.text("Finalizing map...")
                time.sleep(0.01)
        
        placeholder.empty()


def get_map_component_state(key: str) -> Dict[str, Any]:
    """
    Get the current state of a map component.
    
    Args:
        key: Unique key for the map component
        
    Returns:
        Dictionary containing component state
    """
    if key not in st.session_state:
        st.session_state[key] = {
            "initialized": False,
            "last_data": None,
            "interaction_history": [],
            "error_count": 0
        }
    
    return st.session_state[key]


def update_map_component_state(key: str, **kwargs) -> None:
    """
    Update the state of a map component.
    
    Args:
        key: Unique key for the map component
        **kwargs: State updates to apply
    """
    state = get_map_component_state(key)
    state.update(kwargs)
    st.session_state[key] = state


def display_map_controls(
    data: List[Dict[str, Any]], 
    key: str = "map_controls"
) -> Dict[str, Any]:
    """
    Display user interface controls for map display options and filtering.
    
    This function creates interactive widgets that allow users to:
    - Filter data by affinity score ranges
    - Toggle different marker styles
    - Control map display options
    - Export or share map data
    
    Args:
        data: List of location data dictionaries
        key: Unique key for the control widgets
        
    Returns:
        Dictionary containing current control settings and filtered data
    """
    st.subheader("🎛️ Map Controls")
    
    # Create columns for organized control layout
    col1, col2, col3 = st.columns(3)
    
    # Initialize control state
    control_state = get_map_component_state(f"{key}_state")
    
    with col1:
        st.write("**Filtering Options**")
        
        # Affinity score filter
        if data:
            min_affinity = min(item.get('affinity', 0) for item in data)
            max_affinity = max(item.get('affinity', 0) for item in data)
            
            affinity_range = st.slider(
                "Affinity Score Range",
                min_value=float(min_affinity),
                max_value=float(max_affinity),
                value=(float(min_affinity), float(max_affinity)),
                step=0.01,
                key=f"{key}_affinity_range",
                help="Filter locations by affinity score range"
            )
        else:
            affinity_range = (0.0, 1.0)
        
        # Popularity filter
        if data:
            min_popularity = min(item.get('popularity', 0) for item in data)
            max_popularity = max(item.get('popularity', 0) for item in data)
            
            popularity_range = st.slider(
                "Popularity Range",
                min_value=float(min_popularity),
                max_value=float(max_popularity),
                value=(float(min_popularity), float(max_popularity)),
                step=0.01,
                key=f"{key}_popularity_range",
                help="Filter locations by popularity range"
            )
        else:
            popularity_range = (0.0, 1.0)
        
        # Location name filter
        location_filter = st.text_input(
            "Location Name Filter",
            value="",
            key=f"{key}_location_filter",
            help="Filter locations by name (case-insensitive partial match)"
        )
    
    with col2:
        st.write("**Display Options**")
        
        # Marker style options
        marker_style = st.selectbox(
            "Marker Style",
            options=["Circles", "Pins", "Custom Icons"],
            index=0,
            key=f"{key}_marker_style",
            help="Choose how markers are displayed on the map"
        )
        
        # Color scheme
        color_scheme = st.selectbox(
            "Color Scheme",
            options=["Default", "Heat Map", "High Contrast", "Monochrome"],
            index=0,
            key=f"{key}_color_scheme",
            help="Choose color scheme for markers"
        )
        
        # Show/hide options
        show_labels = st.checkbox(
            "Show Location Labels",
            value=False,
            key=f"{key}_show_labels",
            help="Display location names on markers"
        )
        
        show_metrics = st.checkbox(
            "Show Metrics in Popups",
            value=True,
            key=f"{key}_show_metrics",
            help="Include affinity and popularity metrics in marker popups"
        )
        
        # Clustering option
        enable_clustering = st.checkbox(
            "Enable Marker Clustering",
            value=len(data) > 20 if data else False,
            key=f"{key}_clustering",
            help="Group nearby markers together for better performance"
        )
    
    with col3:
        st.write("**Map Options**")
        
        # Map tile layer
        tile_layer = st.selectbox(
            "Map Style",
            options=["OpenStreetMap", "Satellite", "Terrain", "Dark Mode"],
            index=0,
            key=f"{key}_tile_layer",
            help="Choose the base map style"
        )
        
        # Map size
        map_height = st.slider(
            "Map Height (px)",
            min_value=400,
            max_value=1000,
            value=600,
            step=50,
            key=f"{key}_map_height",
            help="Adjust the height of the map display"
        )
        
        # Auto-fit bounds
        auto_fit = st.checkbox(
            "Auto-fit Map Bounds",
            value=True,
            key=f"{key}_auto_fit",
            help="Automatically adjust map zoom to show all markers"
        )
        
        # Export options
        st.write("**Export Options**")
        
        if st.button("📊 Export Data", key=f"{key}_export_data"):
            _handle_data_export(data, affinity_range, popularity_range, location_filter)
        
        if st.button("🔗 Share Map", key=f"{key}_share_map"):
            _handle_map_sharing(data, {
                'affinity_range': affinity_range,
                'popularity_range': popularity_range,
                'location_filter': location_filter,
                'marker_style': marker_style,
                'color_scheme': color_scheme
            })
    
    # Apply filters to data
    filtered_data = _apply_data_filters(
        data, 
        affinity_range, 
        popularity_range, 
        location_filter
    )
    
    # Display filter results
    if filtered_data != data:
        st.info(f"Showing {len(filtered_data)} of {len(data)} locations after filtering")
    
    # Prepare control settings
    control_settings = {
        'affinity_range': affinity_range,
        'popularity_range': popularity_range,
        'location_filter': location_filter,
        'marker_style': marker_style,
        'color_scheme': color_scheme,
        'show_labels': show_labels,
        'show_metrics': show_metrics,
        'enable_clustering': enable_clustering,
        'tile_layer': tile_layer,
        'map_height': map_height,
        'auto_fit': auto_fit,
        'filtered_data': filtered_data,
        'original_data_count': len(data),
        'filtered_data_count': len(filtered_data)
    }
    
    # Update component state
    update_map_component_state(f"{key}_state", **control_settings)
    
    return control_settings


def _apply_data_filters(
    data: List[Dict[str, Any]], 
    affinity_range: Tuple[float, float],
    popularity_range: Tuple[float, float],
    location_filter: str
) -> List[Dict[str, Any]]:
    """
    Apply filtering criteria to location data.
    
    Args:
        data: Original location data
        affinity_range: Min and max affinity scores to include
        popularity_range: Min and max popularity scores to include
        location_filter: Text filter for location names
        
    Returns:
        Filtered list of location data
    """
    if not data:
        return []
    
    filtered_data = []
    location_filter_lower = location_filter.lower().strip()
    
    for item in data:
        try:
            # Check affinity range
            affinity = float(item.get('affinity', 0))
            if not (affinity_range[0] <= affinity <= affinity_range[1]):
                continue
            
            # Check popularity range
            popularity = float(item.get('popularity', 0))
            if not (popularity_range[0] <= popularity <= popularity_range[1]):
                continue
            
            # Check location name filter
            if location_filter_lower:
                location_name = str(item.get('location', '')).lower()
                if location_filter_lower not in location_name:
                    continue
            
            filtered_data.append(item)
            
        except (TypeError, ValueError):
            # Skip items with invalid data
            continue
    
    return filtered_data


def _handle_data_export(
    data: List[Dict[str, Any]], 
    affinity_range: Tuple[float, float],
    popularity_range: Tuple[float, float],
    location_filter: str
) -> None:
    """
    Handle data export functionality.
    
    Args:
        data: Location data to export
        affinity_range: Current affinity filter range
        popularity_range: Current popularity filter range
        location_filter: Current location name filter
    """
    try:
        # Apply current filters
        filtered_data = _apply_data_filters(data, affinity_range, popularity_range, location_filter)
        
        if not filtered_data:
            st.warning("No data to export with current filters")
            return
        
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['location', 'latitude', 'longitude', 'affinity', 'affinity_rank', 'popularity'])
        writer.writeheader()
        writer.writerows(filtered_data)
        
        csv_data = output.getvalue()
        
        # Provide download button
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"map_data_{len(filtered_data)}_locations.csv",
            mime="text/csv",
            help="Download filtered location data as CSV file"
        )
        
        st.success(f"Prepared {len(filtered_data)} locations for download")
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        st.error("Failed to export data. Please try again.")


def _handle_map_sharing(data: List[Dict[str, Any]], settings: Dict[str, Any]) -> None:
    """
    Handle map sharing functionality.
    
    Args:
        data: Location data being shared
        settings: Current map display settings
    """
    try:
        # Create shareable configuration
        share_config = {
            'data_count': len(data),
            'filters': {
                'affinity_range': settings['affinity_range'],
                'popularity_range': settings['popularity_range'],
                'location_filter': settings['location_filter']
            },
            'display': {
                'marker_style': settings['marker_style'],
                'color_scheme': settings['color_scheme']
            }
        }
        
        # Generate shareable URL or configuration
        import json
        import base64
        
        config_json = json.dumps(share_config)
        config_encoded = base64.b64encode(config_json.encode()).decode()
        
        # Display sharing options
        st.info("Map sharing options:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_area(
                "Share Configuration",
                value=config_encoded,
                height=100,
                help="Copy this configuration to share your map settings"
            )
        
        with col2:
            st.code(f"""
# To recreate this map view:
# 1. Use {len(data)} location data points
# 2. Apply affinity filter: {settings['affinity_range']}
# 3. Apply popularity filter: {settings['popularity_range']}
# 4. Use marker style: {settings['marker_style']}
# 5. Use color scheme: {settings['color_scheme']}
            """)
        
        st.success("Map configuration ready for sharing!")
        
    except Exception as e:
        logger.error(f"Error sharing map: {str(e)}")
        st.error("Failed to generate sharing configuration. Please try again.")


def handle_user_interactions(
    map_data: Dict[str, Any], 
    original_data: List[Dict[str, Any]],
    control_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enhanced user interaction handling with control integration.
    
    Args:
        map_data: Data returned from st_folium component
        original_data: Original location data for reference
        control_settings: Current control settings from display_map_controls
        
    Returns:
        Dictionary containing processed interaction data with control context
    """
    # Get base interaction data
    interaction_data = _handle_map_interactions(map_data, original_data)
    
    # Add control context
    interaction_data.update({
        'control_settings': control_settings,
        'filtered_data_count': control_settings.get('filtered_data_count', len(original_data)),
        'active_filters': {
            'affinity': control_settings.get('affinity_range'),
            'popularity': control_settings.get('popularity_range'),
            'location': control_settings.get('location_filter', '')
        }
    })
    
    # Enhanced interaction feedback
    if interaction_data.get("clicked_location"):
        clicked_location = interaction_data["clicked_location"]
        
        # Check if clicked location passes current filters
        filtered_data = control_settings.get('filtered_data', original_data)
        is_visible = any(
            loc.get('location') == clicked_location.get('location') 
            for loc in filtered_data
        )
        
        interaction_data['location_visible_in_filter'] = is_visible
        
        if not is_visible:
            st.warning("⚠️ The clicked location is currently filtered out by your display settings.")
    
    return interaction_data


def create_advanced_map_controls(
    data: List[Dict[str, Any]], 
    key: str = "advanced_controls"
) -> Dict[str, Any]:
    """
    Create advanced control panel with additional features.
    
    Args:
        data: List of location data dictionaries
        key: Unique key for the control widgets
        
    Returns:
        Dictionary containing advanced control settings
    """
    with st.expander("🔧 Advanced Controls", expanded=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Analysis**")
            
            # Statistical summary
            if st.button("📈 Show Statistics", key=f"{key}_stats"):
                _display_data_statistics(data)
            
            # Correlation analysis
            if st.button("🔗 Analyze Correlations", key=f"{key}_correlations"):
                _display_correlation_analysis(data)
            
            # Outlier detection
            outlier_threshold = st.slider(
                "Outlier Detection Sensitivity",
                min_value=1.0,
                max_value=3.0,
                value=2.0,
                step=0.1,
                key=f"{key}_outlier_threshold",
                help="Standard deviations from mean to consider as outliers"
            )
            
        with col2:
            st.write("**Performance Options**")
            
            # Rendering optimization
            max_markers = st.number_input(
                "Max Markers to Display",
                min_value=10,
                max_value=1000,
                value=min(100, len(data)) if data else 100,
                step=10,
                key=f"{key}_max_markers",
                help="Limit number of markers for better performance"
            )
            
            # Update frequency
            update_mode = st.selectbox(
                "Map Update Mode",
                options=["Real-time", "On Apply", "Manual"],
                index=0,
                key=f"{key}_update_mode",
                help="How frequently the map updates with filter changes"
            )
            
            # Debug mode
            debug_mode = st.checkbox(
                "Debug Mode",
                value=False,
                key=f"{key}_debug_mode",
                help="Show additional debugging information"
            )
    
    return {
        'outlier_threshold': outlier_threshold,
        'max_markers': max_markers,
        'update_mode': update_mode,
        'debug_mode': debug_mode
    }


def _display_data_statistics(data: List[Dict[str, Any]]) -> None:
    """Display statistical summary of the location data."""
    if not data:
        st.warning("No data available for statistics")
        return
    
    try:
        # Calculate statistics
        affinities = [float(item.get('affinity', 0)) for item in data]
        popularities = [float(item.get('popularity', 0)) for item in data]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Locations", len(data))
            st.metric("Avg Affinity", f"{sum(affinities)/len(affinities):.2%}")
        
        with col2:
            st.metric("Max Affinity", f"{max(affinities):.2%}")
            st.metric("Min Affinity", f"{min(affinities):.2%}")
        
        with col3:
            st.metric("Avg Popularity", f"{sum(popularities)/len(popularities):.2%}")
            high_affinity_count = sum(1 for a in affinities if a >= 0.8)
            st.metric("High Affinity (≥80%)", high_affinity_count)
        
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")


def _display_correlation_analysis(data: List[Dict[str, Any]]) -> None:
    """Display correlation analysis between metrics."""
    if not data or len(data) < 2:
        st.warning("Need at least 2 data points for correlation analysis")
        return
    
    try:
        # Calculate correlation between affinity and popularity
        affinities = [float(item.get('affinity', 0)) for item in data]
        popularities = [float(item.get('popularity', 0)) for item in data]
        
        # Simple correlation coefficient calculation
        n = len(affinities)
        sum_a = sum(affinities)
        sum_p = sum(popularities)
        sum_ap = sum(a * p for a, p in zip(affinities, popularities))
        sum_a2 = sum(a * a for a in affinities)
        sum_p2 = sum(p * p for p in popularities)
        
        correlation = (n * sum_ap - sum_a * sum_p) / (
            ((n * sum_a2 - sum_a * sum_a) * (n * sum_p2 - sum_p * sum_p)) ** 0.5
        )
        
        st.info(f"Correlation between Affinity and Popularity: {correlation:.3f}")
        
        if abs(correlation) > 0.7:
            st.success("Strong correlation detected!")
        elif abs(correlation) > 0.3:
            st.warning("Moderate correlation detected")
        else:
            st.info("Weak correlation")
            
    except Exception as e:
        st.error(f"Error calculating correlation: {str(e)}")