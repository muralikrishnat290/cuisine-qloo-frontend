"""
Data models and type definitions for the demography map display feature.
"""

from typing import TypedDict, List, Dict, Any, Tuple, Optional


class LocationData(TypedDict):
    """Type definition for location data structure."""
    location: str           # Full location description
    latitude: float         # Geographic latitude (-90 to 90)
    longitude: float        # Geographic longitude (-180 to 180)
    affinity: float         # Affinity score (0.0 to 1.0)
    affinity_rank: float    # Affinity ranking (0.0 to 1.0)
    popularity: float       # Popularity metric (0.0 to 1.0)


class MarkerStyle(TypedDict):
    """Type definition for marker style configuration."""
    color: str              # Marker color based on affinity
    size: int               # Marker size based on popularity
    icon: str               # Icon type (circle, star, etc.)
    opacity: float          # Marker opacity


class MapConfig(TypedDict):
    """Type definition for map configuration."""
    center_lat: float       # Map center latitude
    center_lon: float       # Map center longitude
    zoom_level: int         # Initial zoom level (1-18)
    tile_layer: str         # Map tile provider
    width: str              # Map width (CSS format)
    height: str             # Map height (CSS format)


def validate_location_data(data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate location data for required fields and value ranges.
    
    Args:
        data: List of location data dictionaries
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not isinstance(data, list):
        return False, ["Data must be a list"]
    
    if not data:
        return False, ["Data list cannot be empty"]
    
    errors = []
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {i}: Must be a dictionary")
            continue
            
        # Check required fields
        required_fields = ['location', 'latitude', 'longitude', 'affinity', 'affinity_rank', 'popularity']
        for field in required_fields:
            if field not in item:
                errors.append(f"Item {i}: Missing required field '{field}'")
                continue
                
        # Validate location string
        if not isinstance(item.get('location'), str) or not item.get('location').strip():
            errors.append(f"Item {i}: 'location' must be a non-empty string")
            
        # Validate latitude
        try:
            lat = float(item.get('latitude', 0))
            if not -90 <= lat <= 90:
                errors.append(f"Item {i}: 'latitude' must be between -90 and 90, got {lat}")
        except (TypeError, ValueError):
            errors.append(f"Item {i}: 'latitude' must be a valid number")
            
        # Validate longitude
        try:
            lon = float(item.get('longitude', 0))
            if not -180 <= lon <= 180:
                errors.append(f"Item {i}: 'longitude' must be between -180 and 180, got {lon}")
        except (TypeError, ValueError):
            errors.append(f"Item {i}: 'longitude' must be a valid number")
            
        # Validate affinity score
        try:
            affinity = float(item.get('affinity', 0))
            if not 0.0 <= affinity <= 1.0:
                errors.append(f"Item {i}: 'affinity' must be between 0.0 and 1.0, got {affinity}")
        except (TypeError, ValueError):
            errors.append(f"Item {i}: 'affinity' must be a valid number")
            
        # Validate affinity rank
        try:
            affinity_rank = float(item.get('affinity_rank', 0))
            if not 0.0 <= affinity_rank <= 1.0:
                errors.append(f"Item {i}: 'affinity_rank' must be between 0.0 and 1.0, got {affinity_rank}")
        except (TypeError, ValueError):
            errors.append(f"Item {i}: 'affinity_rank' must be a valid number")
            
        # Validate popularity
        try:
            popularity = float(item.get('popularity', 0))
            if not 0.0 <= popularity <= 1.0:
                errors.append(f"Item {i}: 'popularity' must be between 0.0 and 1.0, got {popularity}")
        except (TypeError, ValueError):
            errors.append(f"Item {i}: 'popularity' must be a valid number")
    
    return len(errors) == 0, errors


def validate_marker_style(style: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate marker style configuration.
    
    Args:
        style: Marker style dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not isinstance(style, dict):
        return False, ["Style must be a dictionary"]
    
    errors = []
    required_fields = ['color', 'size', 'icon', 'opacity']
    
    for field in required_fields:
        if field not in style:
            errors.append(f"Missing required field '{field}'")
    
    # Validate color (basic string check)
    if 'color' in style and not isinstance(style['color'], str):
        errors.append("'color' must be a string")
        
    # Validate size
    if 'size' in style:
        try:
            size = int(style['size'])
            if size <= 0:
                errors.append("'size' must be a positive integer")
        except (TypeError, ValueError):
            errors.append("'size' must be a valid integer")
            
    # Validate icon
    if 'icon' in style and not isinstance(style['icon'], str):
        errors.append("'icon' must be a string")
        
    # Validate opacity
    if 'opacity' in style:
        try:
            opacity = float(style['opacity'])
            if not 0.0 <= opacity <= 1.0:
                errors.append("'opacity' must be between 0.0 and 1.0")
        except (TypeError, ValueError):
            errors.append("'opacity' must be a valid number")
    
    return len(errors) == 0, errors


def validate_map_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate map configuration.
    
    Args:
        config: Map configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not isinstance(config, dict):
        return False, ["Config must be a dictionary"]
    
    errors = []
    required_fields = ['center_lat', 'center_lon', 'zoom_level', 'tile_layer', 'width', 'height']
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field '{field}'")
    
    # Validate center_lat
    if 'center_lat' in config:
        try:
            lat = float(config['center_lat'])
            if not -90 <= lat <= 90:
                errors.append("'center_lat' must be between -90 and 90")
        except (TypeError, ValueError):
            errors.append("'center_lat' must be a valid number")
            
    # Validate center_lon
    if 'center_lon' in config:
        try:
            lon = float(config['center_lon'])
            if not -180 <= lon <= 180:
                errors.append("'center_lon' must be between -180 and 180")
        except (TypeError, ValueError):
            errors.append("'center_lon' must be a valid number")
            
    # Validate zoom_level
    if 'zoom_level' in config:
        try:
            zoom = int(config['zoom_level'])
            if not 1 <= zoom <= 18:
                errors.append("'zoom_level' must be between 1 and 18")
        except (TypeError, ValueError):
            errors.append("'zoom_level' must be a valid integer")
            
    # Validate tile_layer
    if 'tile_layer' in config and not isinstance(config['tile_layer'], str):
        errors.append("'tile_layer' must be a string")
        
    # Validate width and height (basic string check for CSS format)
    for dimension in ['width', 'height']:
        if dimension in config and not isinstance(config[dimension], str):
            errors.append(f"'{dimension}' must be a string (CSS format)")
    
    return len(errors) == 0, errors