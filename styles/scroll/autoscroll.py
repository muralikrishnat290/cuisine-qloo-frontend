import streamlit as st

def add_scroll_to_bottom_button():
    """Add a floating button that scrolls to the bottom of the page"""
    
    # CSS for the floating button
    button_css = """
    <style>
    .scroll-to-bottom {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #ff6b6b;
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .scroll-to-bottom:hover {
        background-color: #ff5252;
        transform: scale(1.1);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    .scroll-to-bottom:active {
        transform: scale(0.95);
    }
    </style>
    """
    
    # JavaScript for scroll functionality
    scroll_js = """
    <script>
    function scrollToBottom() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }
    </script>
    """
    
    # HTML button
    button_html = """
    <button class="scroll-to-bottom" onclick="scrollToBottom()" title="Scroll to Bottom">
        ↓
    </button>
    """
    
    # Combine and inject
    full_html = button_css + scroll_js + button_html
    st.components.v1.html(full_html, height=0)