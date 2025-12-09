"""Theme loading and management."""

import json
from dataclasses import dataclass
from pathlib import Path

THEMES_DIR = Path(__file__).parent.parent.parent / "themes"


@dataclass
class ThemeColors:
    # Background
    bg_primary: str
    bg_secondary: str

    # Blobs (animated background)
    blob_1_start: str
    blob_1_end: str
    blob_2_start: str
    blob_2_end: str
    blob_3_start: str
    blob_3_end: str

    # Text
    text_primary: str
    text_secondary: str
    text_muted: str

    # Accents
    accent_primary: str
    accent_secondary: str
    accent_tertiary: str

    # Glass effects
    glass_bg: str
    glass_border: str
    glass_highlight: str

    # Cards overlay
    overlay_dark: str


@dataclass
class ThemeEffects:
    blur_amount: str
    glass_opacity: float
    border_opacity: float


@dataclass
class Theme:
    name: str
    display_name: str
    colors: ThemeColors
    effects: ThemeEffects

    def _color_css_vars(self) -> list[str]:
        """Generate CSS variables for theme colors."""
        lines: list[str] = []
        for field_name in self.colors.__dataclass_fields__:
            css_name = field_name.replace("_", "-")
            value = getattr(self.colors, field_name)
            lines.append(f"    --{css_name}: {value};")
        return lines

    def _effect_css_vars(self) -> list[str]:
        """Generate CSS variables for theme effects."""
        return [
            f"    --blur-amount: {self.effects.blur_amount};",
            f"    --glass-opacity: {self.effects.glass_opacity};",
            f"    --border-opacity: {self.effects.border_opacity};",
        ]

    def _css_variable_lines(self) -> list[str]:
        return [*self._color_css_vars(), *self._effect_css_vars()]

    def to_css_variables(self, selector: str = ":root") -> str:
        return "\n".join([f"{selector} {{", *self._css_variable_lines(), "}"])


def _load_theme_data(theme_path: Path) -> dict:
    """Load and parse theme JSON file."""
    return json.loads(theme_path.read_text(encoding="utf-8"))


def _create_theme_from_data(data: dict) -> Theme:
    """Construct Theme object from parsed data."""
    return Theme(
        name=data["name"],
        display_name=data["display_name"],
        colors=ThemeColors(**data["colors"]),
        effects=ThemeEffects(**data["effects"]),
    )


def load_theme(name: str) -> Theme:
    """Load a theme from JSON file."""
    theme_path = THEMES_DIR / f"{name}.json"
    if not theme_path.exists():
        raise ValueError(f"Theme '{name}' not found at {theme_path}")

    data = _load_theme_data(theme_path)
    return _create_theme_from_data(data)


def list_available_themes() -> list[str]:
    """List all available theme names."""
    if not THEMES_DIR.exists():
        return []
    return sorted(p.stem for p in THEMES_DIR.glob("*.json"))
