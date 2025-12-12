"""Favicon generation with initials on themed gradient."""

import base64
from dataclasses import dataclass

from .themes import Theme


@dataclass
class FaviconConfig:
    size: int = 32
    font_size: int = 18
    font_weight: int = 600


def generate_favicon_svg(
    initials: str, theme: Theme, config: FaviconConfig | None = None
) -> str:
    """Generate SVG favicon with initials on gradient background."""
    cfg = config or FaviconConfig()
    colors = theme.colors

    # Use blob colors for a vibrant gradient matching the theme
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cfg.size} {cfg.size}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{colors.blob_1_start}"/>
      <stop offset="50%" stop-color="{colors.blob_2_start}"/>
      <stop offset="100%" stop-color="{colors.blob_3_end}"/>
    </linearGradient>
  </defs>
  <rect width="{cfg.size}" height="{cfg.size}" rx="6" fill="url(#bg)"/>
  <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
        fill="white" font-family="Inter, system-ui, sans-serif"
        font-size="{cfg.font_size}" font-weight="{cfg.font_weight}">{initials}</text>
</svg>"""


def favicon_to_data_uri(svg: str) -> str:
    """Convert SVG to base64 data URI for inline embedding."""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
