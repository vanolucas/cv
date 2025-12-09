"""Markdown to HTML conversion utilities."""

import re
from markupsafe import Markup

# Pattern for markdown links: [text](url)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Pattern for HTML code blocks: ```html ... ```
HTML_BLOCK_PATTERN = re.compile(r"```html\s*\n(.*?)\n```", re.DOTALL)


def convert_links(text: str) -> str:
    """Convert markdown links to HTML anchor tags that open in new tab."""

    def replace_link(match: re.Match[str]) -> str:
        link_text, url = match.group(1), match.group(2)
        return f'<a href="{url}" target="_blank" rel="noopener">{link_text}</a>'

    return LINK_PATTERN.sub(replace_link, text)


def process_text(text: str) -> Markup:
    """Process markdown text and return safe HTML markup."""
    return Markup(convert_links(text))


def extract_html_blocks(content: str) -> tuple[str, list[str]]:
    """Extract HTML code blocks from markdown content.

    Returns:
        Tuple of (content with blocks removed, list of extracted HTML blocks)
    """
    blocks: list[str] = []

    def collect_block(match: re.Match[str]) -> str:
        blocks.append(match.group(1).strip())
        return ""

    cleaned = HTML_BLOCK_PATTERN.sub(collect_block, content)
    return cleaned, blocks
