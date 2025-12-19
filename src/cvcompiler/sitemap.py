"""Sitemap generator for CV website."""

from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement


def generate_sitemap(canonical_url: str, last_modified: datetime | None = None) -> str:
    """Generate sitemap XML content for a single-page CV website."""
    if last_modified is None:
        last_modified = datetime.now()

    if not canonical_url.startswith(("http://", "https://")):
        raise ValueError(
            f"canonical_url must start with http:// or https://: {canonical_url}"
        )

    canonical_url = canonical_url.rstrip("/")

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = canonical_url
    SubElement(url, "lastmod").text = last_modified.strftime("%Y-%m-%d")
    SubElement(url, "changefreq").text = "monthly"
    SubElement(url, "priority").text = "1.0"

    tree = ElementTree(urlset)
    import io

    buffer = io.BytesIO()
    tree.write(buffer, encoding="utf-8", xml_declaration=True)
    return buffer.getvalue().decode("utf-8")


def write_sitemap(sitemap_xml: str, output_path: Path) -> None:
    """Write generated sitemap XML to file."""
    output_path.write_text(sitemap_xml, encoding="utf-8")
