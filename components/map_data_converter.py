"""
Map data conversion utilities for Kitchen Intel application.

This module handles conversion of API response data to map-compatible formats
with comprehensive error handling and validation.
"""
import json
from typing import Dict, List, Any, Optional, Tuple


def convert_api_response_to_location_data(api_response: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Convert API response to location data format.
    
    Args:
        api_response: JSON string containing API response
        
    Returns:
        Tuple of (location_data_list, conversion_errors)
        
    Raises:
        json.JSONDecodeError: If response is not valid JSON
        ValueError: If response structure is invalid
    """
    # Parse JSON response
    try:
        map_object = json.loads(api_response)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to parse API response as JSON: {str(e)}", api_response, 0)
    
    # Validate response structure
    if not isinstance(map_object, dict):
        raise ValueError("Invalid API response format: Expected JSON object")
    
    # Extract location data with comprehensive error handling
    location_data = []
    conversion_errors = []
    
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
            raw_locations = map_object[field_name]
            
            # Handle different data structures
            if isinstance(raw_locations, list):
                for i, item in enumerate(raw_locations):
                    converted_item = convert_api_item_to_location_data(item)
                    if converted_item:
                        location_data.append(converted_item)
                    else:
                        conversion_errors.append(f"Item {i} in '{field_name}': Could not convert to location data")
                        
            elif isinstance(raw_locations, dict):
                # Single location object
                converted_item = convert_api_item_to_location_data(raw_locations)
                if converted_item:
                    location_data.append(converted_item)
                else:
                    conversion_errors.append(f"Single item in '{field_name}': Could not convert to location data")
            
            # If we found data in this field, stop looking
            if location_data:
                break
    
    return location_data, conversion_errors


def convert_api_item_to_location_data(api_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
        location_name = _extract_location_name(api_item)
        if not location_name:
            return None
        
        # Extract coordinates - try various field names
        latitude, longitude = _extract_coordinates(api_item)
        if latitude is None or longitude is None:
            return None
        
        # Validate coordinates
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


def _extract_location_name(api_item: Dict[str, Any]) -> Optional[str]:
    """Extract location name from API item."""
    for name_field in ["location", "name", "place", "address", "city", "title"]:
        if name_field in api_item and api_item[name_field]:
            return str(api_item[name_field]).strip()
    return None


def _extract_coordinates(api_item: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """Extract latitude and longitude from API item."""
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
    
    return latitude, longitude


def _extract_numeric_field(data_dict: Dict[str, Any], field_names: List[str], 
                          default_value: float) -> float:
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