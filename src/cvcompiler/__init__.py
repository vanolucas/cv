"""CV Compiler - Convert Markdown CV to a beautiful static website."""

import logging
from pathlib import Path

from .generator import generate_html, write_output
from .parser import parse_cv
from .themes import Theme, list_available_themes, load_theme

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DEFAULT_LIGHT_THEME = "vivid"
DEFAULT_DARK_THEME = "dark_purple"


def _display_theme_options(themes: list[str], default: str) -> None:
    """Display available themes with their display names."""
    for i, name in enumerate(themes, 1):
        theme = load_theme(name)
        marker = " (default)" if name == default else ""
        logger.info(f"  [{i}] {theme.display_name}{marker}")


def _get_theme_selection(themes: list[str], default: str) -> int:
    """Get valid theme selection index from user input."""
    default_idx = themes.index(default) if default in themes else 0

    while True:
        choice = input("\nSelect theme (number) or Enter for default: ").strip()
        if not choice:
            return default_idx
        try:
            index = int(choice) - 1
            if 0 <= index < len(themes):
                return index
        except ValueError:
            pass
        logger.info(f"Please enter a number between 1 and {len(themes)}")


def _prompt_theme_choice(prompt: str, default: str) -> Theme:
    themes = list_available_themes()
    if not themes:
        logger.error("❌ No themes found in themes/ directory")
        raise SystemExit(1)

    logger.info(f"\n🎨 {prompt}")
    _display_theme_options(themes, default)

    index = _get_theme_selection(themes, default)
    selected = load_theme(themes[index])
    logger.info(f"✅ Using: {selected.display_name}")
    return selected


def select_themes() -> tuple[Theme, Theme]:
    """Prompt user to select light and dark themes."""
    light = _prompt_theme_choice("Select LIGHT theme:", DEFAULT_LIGHT_THEME)
    dark = _prompt_theme_choice("Select DARK theme:", DEFAULT_DARK_THEME)
    return light, dark


def compile_cv(
    source: Path, output_dir: Path, light_theme: Theme, dark_theme: Theme
) -> Path:
    """Compile a CV markdown file to HTML."""
    logger.info(f"📄 Reading {source.name}...")
    content = source.read_text(encoding="utf-8")

    logger.info("🔍 Parsing CV structure...")
    cv = parse_cv(content)

    logger.info("🎨 Generating HTML...")
    html = generate_html(cv, light_theme, dark_theme)

    output_file = output_dir / "index.html"
    write_output(html, output_file)
    logger.info(f"✨ Generated {output_file}")

    return output_file


def main() -> None:
    """Entry point - compile cv.md from project root."""
    project_root = Path(__file__).parent.parent.parent
    cv_path = project_root / "cv.md"

    if not cv_path.exists():
        logger.error(f"❌ CV file not found: {cv_path}")
        raise SystemExit(1)

    light_theme, dark_theme = select_themes()
    compile_cv(cv_path, project_root, light_theme, dark_theme)
    logger.info("\n🚀 Done! Open index.html to view your CV.")
