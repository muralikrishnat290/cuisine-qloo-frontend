"""
Components package for Kitchen Intel application.

This package contains modular components for the Kitchen Intel application,
organized by functionality for better maintainability and reusability.
"""

# Core data models and validation
from .data_models import LocationData, MarkerStyle, MapConfig, validate_location_data

# Data processing utilities
from .data_processor import (
    calculate_map_bounds, normalize_affinity_scores, calculate_center_point,
    calculate_optimal_zoom_level, filter_data_by_bounds, group_nearby_points
)

# Map rendering components
from .map_renderer import MapRenderer
from .comprehensive_map_renderer import render_map, render_lightweight_map, get_map_data_summary
from .simple_map_renderer import render_simple_map
from .streamlit_map_integration import display_map_component, display_map_controls

# Data conversion and error handling
from .map_data_converter import convert_api_response_to_location_data, convert_api_item_to_location_data
from .map_error_handler import (
    handle_json_parse_error, handle_no_location_data_error, 
    handle_general_map_error, show_map_fallback_options, show_validation_warnings
)

# Response handling
from .response_handler import (
    extract_text_from_response, display_response, show_fallback_response_info
)

# UI components
from .ui_components import (
    render_app_header, render_mvp_notice, render_disclaimer,
    render_sidebar_settings, render_input_section, render_action_buttons,
    validate_inputs, show_error_message, create_containers, render_divider,
    clear_session_keys, check_existing_results, prepare_analysis_payload,
    update_session_state
)

__all__ = [
    # Data models
    'LocationData', 'MarkerStyle', 'MapConfig', 'validate_location_data',
    
    # Data processing
    'calculate_map_bounds', 'normalize_affinity_scores', 'calculate_center_point',
    'calculate_optimal_zoom_level', 'filter_data_by_bounds', 'group_nearby_points',
    
    # Map rendering
    'MapRenderer', 'render_map', 'render_lightweight_map', 'get_map_data_summary',
    'render_simple_map', 'display_map_component', 'display_map_controls',
    
    # Data conversion and error handling
    'convert_api_response_to_location_data', 'convert_api_item_to_location_data',
    'handle_json_parse_error', 'handle_no_location_data_error', 
    'handle_general_map_error', 'show_map_fallback_options', 'show_validation_warnings',
    
    # Response handling
    'extract_text_from_response', 'display_response', 'show_fallback_response_info',
    
    # UI components
    'render_app_header', 'render_mvp_notice', 'render_disclaimer',
    'render_sidebar_settings', 'render_input_section', 'render_action_buttons',
    'validate_inputs', 'show_error_message', 'create_containers', 'render_divider',
    'clear_session_keys', 'check_existing_results', 'prepare_analysis_payload',
    'update_session_state'
]