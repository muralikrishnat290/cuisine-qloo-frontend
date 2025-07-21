"""
Map error handling utilities for Kitchen Intel application.

This module provides comprehensive error handling and user feedback
for map rendering operations.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def handle_json_parse_error(error: Exception, raw_data: str) -> None:
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


def handle_no_location_data_error(map_object: Dict[str, Any], raw_data_found: bool, 
                                conversion_errors: List[str], extraction_strategies: List[tuple]) -> None:
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


def handle_general_map_error(error: Exception, map_details: str, 
                           conversion_errors: List[str], validation_errors: List[str]) -> None:
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


def show_map_fallback_options(location_data: List[Dict[str, Any]]) -> None:
    """Show fallback options when map rendering fails."""
    st.info("**Alternative ways to view your location data:**")
    
    # Show data table
    with st.expander("📊 View Location Data Table"):
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


def show_validation_warnings(validation_errors: List[str]) -> None:
    """Show validation warnings for location data."""
    if validation_errors:
        st.warning("⚠️ Some location data failed validation but will attempt to render valid entries")
        with st.expander("🔍 Validation Issues"):
            for error in validation_errors[:10]:  # Show first 10 errors
                st.text(f"• {error}")
            if len(validation_errors) > 10:
                st.text(f"... and {len(validation_errors) - 10} more validation errors")