"""
Simple map rendering utilities for Kitchen Intel application.

This module provides lightweight map rendering functionality that won't cause
page reruns and handles fallback scenarios gracefully.
"""
import json
import streamlit as st
from typing import List, Dict, Any
import pandas as pd

from .map_data_converter import convert_api_response_to_location_data
from .map_error_handler import handle_json_parse_error, show_map_fallback_options
from styles.map.map_styles import reduce_map_spacing


def render_simple_map(map_details: str) -> None:
    """
    Render a simple, lightweight map that won't cause page reruns.
    
    Args:
        map_details: JSON string containing API response with location data
    """
    try:
        # Parse and convert location data
        location_data, conversion_errors = convert_api_response_to_location_data(map_details)
        
        if not location_data:
            st.warning("⚠️ No valid location data found in the API response.")
            try:
                map_object = json.loads(map_details)
                with st.expander("🔍 View Raw API Response"):
                    st.json(map_object)
            except json.JSONDecodeError:
                pass
            return
        
        # Display map with traditional location markers
        st.subheader("📍 Location Analysis Map")
        
        # Apply CSS to reduce spacing around map components
        reduce_map_spacing()
        
        # Try to render with Folium first, fallback to st.map
        if _render_folium_map(location_data):
            return
        else:
            _render_streamlit_map(location_data)
        
    except json.JSONDecodeError as e:
        handle_json_parse_error(e, map_details)
    except Exception as e:
        st.error(f"❌ Error rendering simple map: {str(e)}")
        st.info("**Troubleshooting:**")
        st.write("• The location data might be in an unexpected format")
        st.write("• Some coordinates might be invalid")
        
        with st.expander("🔍 Debug Information"):
            st.text(f"Error: {str(e)}")
            st.text("Raw map_details:")
            st.text(map_details[:500] + "..." if len(map_details) > 500 else map_details)


def _render_folium_map(location_data: List[Dict[str, Any]]) -> bool:
    """
    Render map using Folium with enhanced markers.
    
    Args:
        location_data: List of location data dictionaries
        
    Returns:
        True if successful, False if Folium is not available
    """
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
        
        # Add enhanced markers for each location
        for item in location_data:
            _add_folium_marker(m, item, folium)
        
        # Display the map with maximum width
        st_folium(m, width=None, height=500)
        return True
        
    except ImportError:
        st.warning("⚠️ Folium not available. Using fallback map with dot markers.")
        return False


def _add_folium_marker(map_obj: Any, item: Dict[str, Any], folium_module: Any) -> None:
    """Add a styled marker to the Folium map."""
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
    folium_module.Marker(
        location=[item['latitude'], item['longitude']],
        popup=folium_module.Popup(popup_text, max_width=250),
        tooltip=folium_module.Tooltip(tooltip_text, sticky=True),
        icon=folium_module.Icon(
            color=color,
            icon='map-marker',
            prefix='fa'
        )
    ).add_to(map_obj)


def _render_streamlit_map(location_data: List[Dict[str, Any]]) -> None:
    """
    Render map using Streamlit's built-in map with dot markers.
    
    Args:
        location_data: List of location data dictionaries
    """
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
    st.map(map_df, size='size', color='color', height=400)