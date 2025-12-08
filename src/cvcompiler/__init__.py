"""CV Compiler - Convert Markdown CV to a beautiful static website."""

import logging
from pathlib import Path

from .generator import generate_html, write_output
from .parser import parse_cv
from .themes import Theme, list_available_themes, load_theme

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def select_theme() -> Theme:
    """Prompt user to select a theme from available options."""
    themes = list_available_themes()

    if not themes:
        logger.error("❌ No themes found in themes/ directory")
        raise SystemExit(1)

    logger.info("\n🎨 Available themes:")
    for i, name in enumerate(themes, 1):
        theme = load_theme(name)
        logger.info(f"  [{i}] {theme.display_name}")

    while True:
        try:
            choice = input("\nSelect a theme (number): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(themes):
                selected = load_theme(themes[index])
                logger.info(f"✅ Using theme: {selected.display_name}\n")
                return selected
        except (ValueError, IndexError):
            pass
        logger.info(f"Please enter a number between 1 and {len(themes)}")


def compile_cv(source: Path, output_dir: Path, theme: Theme) -> Path:
    """Compile a CV markdown file to HTML."""
    logger.info(f"📄 Reading {source.name}...")
    content = source.read_text(encoding="utf-8")

    logger.info("🔍 Parsing CV structure...")
    cv = parse_cv(content)

    logger.info("🎨 Generating HTML...")
    html = generate_html(cv, theme)

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

    theme = select_theme()
    compile_cv(cv_path, project_root, theme)
    logger.info("🚀 Done! Open index.html to view your CV.")
