

bg_color_template = """
{{
        background-color: {color};
        padding: 0.5em;
        border-radius: 1em;
}}
"""

st_markdown_template = """
.stMarkdown {
        padding-right: 1.5em;
    }
"""

def add_properties_to_css(css, **kwargs):
    if not kwargs:
        return css
    return css.format(**kwargs)

