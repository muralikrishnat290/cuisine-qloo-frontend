"""
Data processing utilities for the demography map display feature.
"""

from typing import List, Dict, Any, Tuple
import math


def calculate_map_bounds(data: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
    """
    Calculate optimal map bounds to show all data points.
    
    Args:
        data: List of location data dictionaries with latitude and longitude
        
    Returns:
        Tuple of (min_lat, min_lon, max_lat, max_lon)
        
    Raises:
        ValueError: If data is empty or contains invalid coordinates
    """
    if not data:
        raise ValueError("Data list cannot be empty")
    
    valid_coords = []
    
    for item in data:
        try:
            lat = float(item.get('latitude', 0))
            lon = float(item.get('longitude', 0))
            
            # Validate coordinate ranges
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                valid_coords.append((lat, lon))
        except (TypeError, ValueError):
            continue  # Skip invalid coordinates
    
    if not valid_coords:
        raise ValueError("No valid coordinates found in data")
    
    latitudes = [coord[0] for coord in valid_coords]
    longitudes = [coord[1] for coord in valid_coords]
    
    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)
    
    # Add padding to bounds (5% of the range or minimum 0.01 degrees)
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon
    
    lat_padding = max(lat_range * 0.05, 0.01)
    lon_padding = max(lon_range * 0.05, 0.01)
    
    # Ensure bounds don't exceed valid coordinate ranges
    min_lat = max(min_lat - lat_padding, -90)
    max_lat = min(max_lat + lat_padding, 90)
    min_lon = max(min_lon - lon_padding, -180)
    max_lon = min(max_lon + lon_padding, 180)
    
    return min_lat, min_lon, max_lat, max_lon


def normalize_affinity_scores(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize affinity scores for consistent marker styling.
    
    Args:
        data: List of location data dictionaries
        
    Returns:
        List of dictionaries with normalized affinity scores
    """
    if not data:
        return []
    
    # Create a copy of the data to avoid modifying the original
    normalized_data = []
    
    # Extract valid affinity scores
    valid_affinities = []
    for item in data:
        try:
            affinity = float(item.get('affinity', 0))
            if 0.0 <= affinity <= 1.0:
                valid_affinities.append(affinity)
        except (TypeError, ValueError):
            continue
    
    if not valid_affinities:
        # If no valid affinities, return data with default normalized values
        for item in data:
            normalized_item = item.copy()
            normalized_item['normalized_affinity'] = 0.5  # Default middle value
            normalized_data.append(normalized_item)
        return normalized_data
    
    # Calculate statistics for normalization
    min_affinity = min(valid_affinities)
    max_affinity = max(valid_affinities)
    affinity_range = max_affinity - min_affinity
    
    # Process each item
    for item in data:
        normalized_item = item.copy()
        
        try:
            affinity = float(item.get('affinity', 0))
            
            if affinity_range == 0:
                # All affinities are the same
                normalized_item['normalized_affinity'] = 0.5
            else:
                # Normalize to 0-1 range based on min/max in dataset
                normalized_affinity = (affinity - min_affinity) / affinity_range
                normalized_item['normalized_affinity'] = max(0.0, min(1.0, normalized_affinity))
                
        except (TypeError, ValueError):
            # Invalid affinity value, use default
            normalized_item['normalized_affinity'] = 0.5
            
        normalized_data.append(normalized_item)
    
    return normalized_data


def calculate_center_point(data: List[Dict[str, Any]]) -> Tuple[float, float]:
    """
    Calculate the center point for map display based on data points.
    
    Args:
        data: List of location data dictionaries
        
    Returns:
        Tuple of (center_lat, center_lon)
        
    Raises:
        ValueError: If data is empty or contains no valid coordinates
    """
    if not data:
        raise ValueError("Data list cannot be empty")
    
    valid_coords = []
    
    for item in data:
        try:
            lat = float(item.get('latitude', 0))
            lon = float(item.get('longitude', 0))
            
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                valid_coords.append((lat, lon))
        except (TypeError, ValueError):
            continue
    
    if not valid_coords:
        raise ValueError("No valid coordinates found in data")
    
    # Calculate centroid
    total_lat = sum(coord[0] for coord in valid_coords)
    total_lon = sum(coord[1] for coord in valid_coords)
    
    center_lat = total_lat / len(valid_coords)
    center_lon = total_lon / len(valid_coords)
    
    return center_lat, center_lon


def calculate_optimal_zoom_level(bounds: Tuple[float, float, float, float], 
                                map_width: int = 800, 
                                map_height: int = 600) -> int:
    """
    Calculate optimal zoom level based on map bounds and display size.
    
    Args:
        bounds: Tuple of (min_lat, min_lon, max_lat, max_lon)
        map_width: Map width in pixels (default: 800)
        map_height: Map height in pixels (default: 600)
        
    Returns:
        Optimal zoom level (1-18)
    """
    min_lat, min_lon, max_lat, max_lon = bounds
    
    # Calculate the span of coordinates
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon
    
    # Calculate zoom level based on coordinate span
    # This is a simplified calculation - real implementations might be more complex
    
    # For latitude: each zoom level roughly doubles the resolution
    lat_zoom = 1
    if lat_span > 0:
        lat_zoom = max(1, min(18, int(math.log2(180 / lat_span))))
    
    # For longitude: similar calculation
    lon_zoom = 1
    if lon_span > 0:
        lon_zoom = max(1, min(18, int(math.log2(360 / lon_span))))
    
    # Use the more restrictive (lower) zoom level to ensure all points are visible
    optimal_zoom = min(lat_zoom, lon_zoom)
    
    # Adjust based on map size (larger maps can handle higher zoom levels)
    size_factor = min(map_width, map_height) / 600  # 600px as baseline
    if size_factor > 1:
        optimal_zoom = min(18, optimal_zoom + int(math.log2(size_factor)))
    elif size_factor < 1:
        optimal_zoom = max(1, optimal_zoom - 1)
    
    return max(1, min(18, optimal_zoom))


def filter_data_by_bounds(data: List[Dict[str, Any]], 
                         bounds: Tuple[float, float, float, float]) -> List[Dict[str, Any]]:
    """
    Filter data points to only include those within specified bounds.
    
    Args:
        data: List of location data dictionaries
        bounds: Tuple of (min_lat, min_lon, max_lat, max_lon)
        
    Returns:
        Filtered list of data points within bounds
    """
    if not data:
        return []
    
    min_lat, min_lon, max_lat, max_lon = bounds
    filtered_data = []
    
    for item in data:
        try:
            lat = float(item.get('latitude', 0))
            lon = float(item.get('longitude', 0))
            
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                filtered_data.append(item)
                
        except (TypeError, ValueError):
            continue  # Skip items with invalid coordinates
    
    return filtered_data


def group_nearby_points(data: List[Dict[str, Any]], 
                       distance_threshold: float = 0.01) -> List[List[Dict[str, Any]]]:
    """
    Group nearby data points for clustering purposes.
    
    Args:
        data: List of location data dictionaries
        distance_threshold: Maximum distance (in degrees) to consider points as nearby
        
    Returns:
        List of groups, where each group is a list of nearby points
    """
    if not data:
        return []
    
    # Simple clustering based on coordinate distance
    groups = []
    ungrouped_points = data.copy()
    
    while ungrouped_points:
        # Start a new group with the first ungrouped point
        current_point = ungrouped_points.pop(0)
        current_group = [current_point]
        
        try:
            current_lat = float(current_point.get('latitude', 0))
            current_lon = float(current_point.get('longitude', 0))
            
            # Find nearby points
            i = 0
            while i < len(ungrouped_points):
                try:
                    other_point = ungrouped_points[i]
                    other_lat = float(other_point.get('latitude', 0))
                    other_lon = float(other_point.get('longitude', 0))
                    
                    # Calculate simple Euclidean distance
                    distance = math.sqrt((current_lat - other_lat)**2 + (current_lon - other_lon)**2)
                    
                    if distance <= distance_threshold:
                        current_group.append(ungrouped_points.pop(i))
                    else:
                        i += 1
                        
                except (TypeError, ValueError):
                    i += 1  # Skip invalid coordinates
                    
        except (TypeError, ValueError):
            pass  # Skip if current point has invalid coordinates
        
        groups.append(current_group)
    
    return groups