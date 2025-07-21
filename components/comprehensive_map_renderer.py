"""
Comprehensive map rendering module for Kitchen Intel application.

This module consolidates all map rendering functionality into a clean,
easy-to-use interface following the established patterns.
"""
import json
import streamlit as st
from typing import List, Dict, Any, Optional

from .map_data_converter import convert_api_response_to_location_data
from .map_error_handler import (
    handle_json_parse_error, 
    handle_no_location_data_error, 
    handle_general_map_error,
    show_map_fallback_options,
    show_validation_warnings
)
from .data_models import validate_location_data
from .streamlit_map_integration import display_map_component, display_map_controls
from .simple_map_renderer import render_simple_map


def render_map(map_details: str) -> None:
    """
    Main entry point for rendering interactive maps with location data.
    
    This function handles the complete map rendering workflow:
    1. Parse and validate API response
    2. Convert data to map format
    3. Render interactive map with controls
    4. Handle errors gracefully
    
    Args:
        map_details: JSON string containing API response with location data
    """
    # Initialize error tracking
    conversion_errors = []
    validation_errors = []
    
    try:
        # Parse and convert API response to location data
        location_data, conversion_errors = convert_api_response_to_location_data(map_details)
        
        if not location_data:
            # Handle case where no location data was found
            try:
                map_object = json.loads(map_details)
                extraction_strategies = [
                    ("location", "Direct location field"),
                    ("locations", "Locations array"),
                    ("results", "Results array"),
                    ("data", "Data array"),
                    ("items", "Items array")
                ]
                handle_no_location_data_error(map_object, False, conversion_errors, extraction_strategies)
            except json.JSONDecodeError as e:
                handle_json_parse_error(e, map_details)
            return
        
        # Validate extracted location data
        is_valid, validation_errors = validate_location_data(location_data)
        
        if not is_valid:
            show_validation_warnings(validation_errors)
        
        # Render the map with data
        _render_map_with_data(location_data, conversion_errors)
        
    except json.JSONDecodeError as e:
        handle_json_parse_error(e, map_details)
    except Exception as e:
        handle_general_map_error(e, map_details, conversion_errors, validation_errors)


def _render_map_with_data(location_data: List[Dict[str, Any]], conversion_errors: List[str]) -> None:
    """
    Render the map with valid location data.
    
    Args:
        location_data: List of validated location data dictionaries
        conversion_errors: List of conversion errors encountered
    """
    try:
        st.subheader("📍 Location Analysis Map")
        
        # Show data quality summary
        if conversion_errors:
            st.info(f"ℹ️ Successfully processed {len(location_data)} locations "
                   f"({len(conversion_errors)} items skipped due to data issues)")
        else:
            st.success(f"✅ Successfully processed {len(location_data)} locations")
        
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
                show_map_fallback_options(location_data)
                
        except Exception as map_error:
            st.error(f"❌ Map rendering failed: {str(map_error)}")
            show_map_fallback_options(location_data)
            
    except Exception as e:
        st.error(f"❌ Unexpected error in map rendering: {str(e)}")
        show_map_fallback_options(location_data)


def render_lightweight_map(map_details: str) -> None:
    """
    Render a lightweight map for better performance.
    
    This is a simplified version that uses the simple map renderer
    for cases where full interactivity is not needed.
    
    Args:
        map_details: JSON string containing API response with location data
    """
    render_simple_map(map_details)


def get_map_data_summary(map_details: str) -> Optional[Dict[str, Any]]:
    """
    Get a summary of map data without rendering.
    
    Args:
        map_details: JSON string containing API response with location data
        
    Returns:
        Dictionary containing data summary or None if parsing fails
    """
    try:
        location_data, conversion_errors = convert_api_response_to_location_data(map_details)
        
        if not location_data:
            return None
        
        # Calculate summary statistics
        affinities = [item.get('affinity', 0) for item in location_data]
        popularities = [item.get('popularity', 0) for item in location_data]
        
        return {
            'total_locations': len(location_data),
            'conversion_errors': len(conversion_errors),
            'avg_affinity': sum(affinities) / len(affinities) if affinities else 0,
            'max_affinity': max(affinities) if affinities else 0,
            'avg_popularity': sum(popularities) / len(popularities) if popularities else 0,
            'coordinate_bounds': _calculate_bounds(location_data)
        }
        
    except Exception:
        return None


def _calculate_bounds(location_data: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """Calculate geographic bounds of location data."""
    try:
        lats = [item['latitude'] for item in location_data if 'latitude' in item]
        lons = [item['longitude'] for item in location_data if 'longitude' in item]
        
        if not lats or not lons:
            return None
        
        return {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lon': min(lons),
            'max_lon': max(lons)
        }
    except Exception:
        return None