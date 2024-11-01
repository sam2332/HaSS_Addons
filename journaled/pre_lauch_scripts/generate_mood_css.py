

import logging
from jinja2 import Environment, FileSystemLoader

#import CONST file from parent directory
import sys
import os

# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path if it's not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from CONST import get_mood_colors



def generate_css(template_path: str, output_path: str):
    """
    Renders the Jinja2 CSS template with mood colors and writes the output to a CSS file.

    Args:
        template_path: Path to the Jinja2 CSS template.
        output_path: Path where the generated CSS will be saved.
    """
    # Load mood colors
    mood_colors = get_mood_colors()
    
    if not mood_colors:
        print("No mood colors to process. Exiting.")
        return

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    
    # Load the template
    template = env.get_template(template_path)
    
    # Render the template with mood_colors
    rendered_css = template.render(mood_colors=mood_colors)
    
    # Write the rendered CSS to the output file
    try:
        with open(output_path, 'w') as f:
            f.write(rendered_css)
        print(f"CSS successfully generated at {output_path}")
        logging.error(f"CSS successfully generated at {output_path}")
    except Exception as e:
        print(f"Error writing CSS file: {e}")
        logging.error(f"Error writing CSS file: {e}")

if __name__ == "__main__":
    generate_css('templates/css/mood_styles.css.j2', 'static/mood_styles.css')