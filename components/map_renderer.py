"""
Map rendering component for demographic data visualization.
This module contains the MapRenderer class for creating interactive maps with Folium.
"""

from typing import List, Dict, Any, Optional, Tuple
from .data_models import LocationData, MapConfig
from .data_processor import calculate_center_point, calculate_map_bounds, calculate_optimal_zoom_level

# Conditional import for optional dependency
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


class MapRenderer:
    """
    Core class responsible for creating and styling interactive maps using Folium.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MapRenderer with optional configuration.
        
        Args:
            config: Optional map configuration dictionary
        """
        # Default configuration
        self.default_config = {
            'tile_layer': 'OpenStreetMap',
            'width': '100%',
            'height': '600px',
            'zoom_level': 10,
            'center_lat': 40.7128,  # Default to NYC
            'center_lon': -74.0060
        }
        
        # Merge with provided config
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config.copy()
    
    def _create_base_map(self, data: List[Dict[str, Any]]) -> folium.Map:
        """
        Create base map with appropriate center and zoom level based on data.
        
        Args:
            data: List of location data dictionaries
            
        Returns:
            Folium Map object with base configuration
            
        Raises:
            ValueError: If data is empty or contains no valid coordinates
        """
        if not data:
            raise ValueError("Cannot create map with empty data")
        
        try:
            # Calculate center point from data
            center_lat, center_lon = calculate_center_point(data)
            
            # Calculate optimal bounds and zoom level
            bounds = calculate_map_bounds(data)
            zoom_level = calculate_optimal_zoom_level(bounds)
            
            # Override config with calculated values
            map_center = [center_lat, center_lon]
            
        except ValueError as e:
            # Fallback to default center if data processing fails
            map_center = [self.config['center_lat'], self.config['center_lon']]
            zoom_level = self.config['zoom_level']
        
        # Create the base map
        base_map = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles=self.config['tile_layer'],
            width=self.config['width'],
            height=self.config['height']
        )
        
        return base_map
    
    def _create_marker_style(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine marker color and size based on affinity and popularity scores.
        
        Args:
            item: Location data dictionary containing affinity and popularity scores
            
        Returns:
            Dictionary containing marker styling properties
        """
        affinity = item.get('affinity', 0.0)
        popularity = item.get('popularity', 0.0)
        
        # Color based on affinity score
        if affinity >= 0.95:
            color = 'red'  # High affinity
        elif affinity >= 0.8:
            color = 'orange'  # Medium-high affinity
        elif affinity >= 0.6:
            color = 'yellow'  # Medium affinity
        elif affinity >= 0.4:
            color = 'lightblue'  # Low-medium affinity
        else:
            color = 'gray'  # Low affinity
        
        # Size based on popularity (radius in pixels)
        if popularity >= 0.8:
            radius = 12
        elif popularity >= 0.6:
            radius = 10
        elif popularity >= 0.4:
            radius = 8
        else:
            radius = 6
        
        return {
            'color': color,
            'radius': radius,
            'opacity': 0.8,
            'fillOpacity': 0.6
        }
    
    def _generate_popup_content(self, item: Dict[str, Any]) -> str:
        """
        Create HTML popup content with location details and proper escaping.
        
        Args:
            item: Location data dictionary
            
        Returns:
            HTML string for popup content with proper escaping
        """
        import html
        
        # Extract and escape data
        location = html.escape(str(item.get('location', 'Unknown Location')))
        affinity = item.get('affinity', 0.0)
        affinity_rank = item.get('affinity_rank', 0.0)
        popularity = item.get('popularity', 0.0)
        
        # Handle None values for numeric fields
        affinity = 0.0 if affinity is None else affinity
        affinity_rank = 0.0 if affinity_rank is None else affinity_rank
        popularity = 0.0 if popularity is None else popularity
        
        # Format numeric values
        affinity_pct = f"{affinity * 100:.1f}%"
        affinity_rank_pct = f"{affinity_rank * 100:.1f}%"
        popularity_pct = f"{popularity * 100:.1f}%"
        
        # Create HTML content with proper structure
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #333; font-size: 14px;">
                {location}
            </h4>
            <div style="font-size: 12px; line-height: 1.4;">
                <div style="margin-bottom: 5px;">
                    <strong>Affinity Score:</strong> {affinity_pct}
                </div>
                <div style="margin-bottom: 5px;">
                    <strong>Affinity Rank:</strong> {affinity_rank_pct}
                </div>
                <div style="margin-bottom: 5px;">
                    <strong>Popularity:</strong> {popularity_pct}
                </div>
            </div>
        </div>
        """
        
        return popup_html
    
    def _add_markers(self, map_obj: folium.Map, data: List[Dict[str, Any]]) -> None:
        """
        Add styled markers with popups to the map.
        
        Args:
            map_obj: Folium Map object to add markers to
            data: List of location data dictionaries
        """
        for item in data:
            # Validate required coordinates
            lat = item.get('latitude')
            lon = item.get('longitude')
            
            if lat is None or lon is None:
                continue  # Skip items without valid coordinates
            
            try:
                lat = float(lat)
                lon = float(lon)
            except (ValueError, TypeError):
                continue  # Skip items with invalid coordinate types
            
            # Validate coordinate ranges
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue  # Skip items with out-of-range coordinates
            
            # Get marker style
            style = self._create_marker_style(item)
            
            # Generate popup content
            popup_content = self._generate_popup_content(item)
            
            # Create and add marker
            marker = folium.CircleMarker(
                location=[lat, lon],
                radius=style['radius'],
                color=style['color'],
                fillColor=style['color'],
                opacity=style['opacity'],
                fillOpacity=style['fillOpacity'],
                popup=folium.Popup(popup_content, max_width=300)
            )
            
            marker.add_to(map_obj)
    
    def render_demographic_map(self, data: List[Dict[str, Any]]) -> folium.Map:
        """
        Main entry point for creating a complete demographic map with markers and popups.
        
        This method orchestrates the entire map creation process:
        1. Validates input data
        2. Creates base map with optimal center and zoom
        3. Adds styled markers based on affinity and popularity
        4. Configures popups with location details
        
        Args:
            data: List of location data dictionaries, each containing:
                - location: str (location name/description)
                - latitude: float (geographic latitude -90 to 90)
                - longitude: float (geographic longitude -180 to 180)
                - affinity: float (affinity score 0.0 to 1.0)
                - affinity_rank: float (affinity ranking 0.0 to 1.0)
                - popularity: float (popularity metric 0.0 to 1.0)
                
        Returns:
            folium.Map: Complete interactive map with markers and popups
            
        Raises:
            ValueError: If data is empty or contains no valid location entries
            TypeError: If data is not a list or contains invalid data types
        """
        # Input validation
        if not isinstance(data, list):
            raise TypeError("Data must be a list of location dictionaries")
        
        if not data:
            raise ValueError("Cannot render map with empty data")
        
        # Filter out entries without valid coordinates
        valid_data = []
        for item in data:
            if not isinstance(item, dict):
                continue
                
            lat = item.get('latitude')
            lon = item.get('longitude')
            
            if lat is None or lon is None:
                continue
                
            try:
                lat = float(lat)
                lon = float(lon)
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    valid_data.append(item)
            except (ValueError, TypeError):
                continue
        
        if not valid_data:
            raise ValueError("No valid location data found (missing or invalid coordinates)")
        
        try:
            # Step 1: Create base map with optimal center and zoom
            map_obj = self._create_base_map(valid_data)
            
            # Step 2: Add all markers with styling and popups
            self._add_markers(map_obj, valid_data)
            
            # Step 3: Fit map bounds to show all markers if we have multiple points
            if len(valid_data) > 1:
                # Calculate bounds for all valid points
                lats = [float(item['latitude']) for item in valid_data]
                lons = [float(item['longitude']) for item in valid_data]
                
                # Add some padding to the bounds
                lat_margin = (max(lats) - min(lats)) * 0.1
                lon_margin = (max(lons) - min(lons)) * 0.1
                
                bounds = [
                    [min(lats) - lat_margin, min(lons) - lon_margin],
                    [max(lats) + lat_margin, max(lons) + lon_margin]
                ]
                
                map_obj.fit_bounds(bounds)
            
            return map_obj
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Failed to render demographic map: {str(e)}") from e