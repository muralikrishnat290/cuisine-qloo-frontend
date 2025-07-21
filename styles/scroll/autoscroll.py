import streamlit.components.v1 as components

def auto_scroll_to_bottom():
    """Inject JavaScript to auto-scroll to the bottom of the page"""
    scroll_script = """
    <script>
        function scrollToBottom() {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }
        
        // Scroll immediately
        scrollToBottom();
        
        // Also scroll after a short delay to catch any dynamic content
        setTimeout(scrollToBottom, 100);
        setTimeout(scrollToBottom, 300);
    </script>
    """
    components.html(scroll_script, height=0, width=0)


def auto_scroll_to_element(element_id):
    """Inject JavaScript to auto-scroll to a specific element"""
    scroll_script = f"""
    <script>
        function scrollToElement() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center'
                }});
            }} else {{
                window.scrollTo({{
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                }});
            }}
        }}
        
        // Scroll immediately
        scrollToElement();
        
        // Also scroll after a short delay to catch any dynamic content
        setTimeout(scrollToElement, 100);
        setTimeout(scrollToElement, 300);
    </script>
    """
    components.html(scroll_script, height=0, width=0)