import streamlit.components.v1 as components

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