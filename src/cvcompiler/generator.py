"""HTML generator using Jinja2 templates."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .favicon import favicon_to_data_uri, generate_favicon_svg
from .markdown import process_text
from .models import CV
from .themes import Theme

TEMPLATES_DIR = Path(__file__).parent / "templates"


def create_template_env() -> Environment:
    """Create Jinja2 environment with custom configuration."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["md"] = process_text
    return env


def generate_html(cv: CV, light_theme: Theme, dark_theme: Theme) -> str:
    """Render CV data to HTML using templates."""
    env = create_template_env()
    template = env.get_template("base.html")

    # Generate favicon using initials and light theme colors
    favicon_svg = generate_favicon_svg(cv.profile.initials, light_theme)
    favicon_uri = favicon_to_data_uri(favicon_svg)

    return template.render(
        cv=cv,
        light_theme=light_theme,
        dark_theme=dark_theme,
        favicon_uri=favicon_uri,
    )


def write_output(html: str, output_path: Path) -> None:
    """Write generated HTML to file."""
    output_path.write_text(html, encoding="utf-8")
