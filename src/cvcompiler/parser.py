"""Parser for CV markdown format."""

import re
from collections.abc import Iterator

from .markdown import extract_html_blocks
from .models import (
    CV,
    Certification,
    Education,
    Experience,
    Language,
    Link,
    Profile,
    Project,
    SkillCategory,
)

# Section headings
SECTION_H2 = "## "
SECTION_H3 = "###"
SECTION_H4 = "####"
SECTION_H5 = "#####"

# Regex patterns
HEADER_PATTERN = re.compile(r"(.+?) @ \[(.+?)\]\((.+?)\)")
PERIOD_LOCATION_PATTERN = re.compile(r"^\*(.+?)\*\s*-\s*(.+)$")
PERIOD_ONLY_PATTERN = re.compile(r"^\*(.+?)\*$")
IMAGE_PATTERN = re.compile(r"!\[.*?\]\((.+?)\)")
DATE_PATTERN = re.compile(r"(\w+)\s*=\s*(\d{4}-\d{2}-\d{2})")
LANGUAGE_PATTERN = re.compile(r"- (.+?): (.+?) \((\d+)%\)")
LINK_PATTERN = re.compile(r"\[(.+?)\]\((.+?)\)")
GOOGLE_ANALYTICS_PATTERN = re.compile(r"^google_analytics_id\s*=\s*(.+)$", re.MULTILINE)
CANONICAL_URL_PATTERN = re.compile(r"^canonical_url\s*=\s*(.+)$", re.MULTILINE)


def parse_cv(content: str) -> CV:
    """Parse markdown CV content into structured data."""
    # Extract metadata from preamble (before first section)
    google_analytics_id = _extract_google_analytics_id(content)
    canonical_url = _extract_canonical_url(content)

    raw_sections = _split_sections(content)

    # Sections that handle HTML embeds at item level (not section level)
    item_level_embed_sections = {"Certification"}

    # Extract HTML blocks from sections that don't handle them at item level
    sections: dict[str, str] = {}
    html_embeds: dict[str, list[str]] = {}
    for name, section_content in raw_sections.items():
        if name in item_level_embed_sections:
            # Pass raw content - parser handles HTML extraction per item
            sections[name] = section_content
        else:
            cleaned, blocks = extract_html_blocks(section_content)
            sections[name] = cleaned
            if blocks:
                html_embeds[name.lower().replace(" ", "_")] = blocks

    return CV(
        profile=_parse_profile(sections.get("Profile", "")),
        experiences=_parse_experiences(sections.get("Experience", "")),
        skills=_parse_skills(sections.get("Skills and Technologies", "")),
        certifications=_parse_certifications(sections.get("Certification", "")),
        education=_parse_education(sections.get("Education", "")),
        languages=_parse_languages(sections.get("Languages", "")),
        contact=_parse_links(sections.get("Contact", "")),
        socials=_parse_links(sections.get("Socials", "")),
        html_embeds=html_embeds,
        google_analytics_id=google_analytics_id,
        canonical_url=canonical_url,
    )


def _extract_google_analytics_id(content: str) -> str:
    """Extract Google Analytics ID from markdown preamble."""
    match = GOOGLE_ANALYTICS_PATTERN.search(content)
    return match.group(1).strip() if match else ""


def _extract_canonical_url(content: str) -> str:
    """Extract canonical URL from markdown preamble."""
    match = CANONICAL_URL_PATTERN.search(content)
    return match.group(1).strip() if match else ""


# -- Section splitting --


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown into top-level (##) sections."""
    sections: dict[str, str] = {}
    current_section = ""
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith(SECTION_H2) and not line.startswith(SECTION_H3):
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = line[len(SECTION_H2) :].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines)

    return sections


def _split_blocks(content: str, prefix: str) -> list[str]:
    """Split content into blocks starting with a markdown heading prefix."""
    pattern = rf"(?=^{re.escape(prefix)} )"
    return [
        b
        for b in re.split(pattern, content, flags=re.MULTILINE)
        if b.startswith(prefix)
    ]


# -- Profile --


def _compute_initials(name: str) -> str:
    return "".join(word[0].upper() for word in name.split() if word)


def _parse_profile(content: str) -> Profile:
    lines = [ln.strip() for ln in content.split("\n") if ln.strip()]

    name = ""
    headline = ""
    image = ""
    dates: dict[str, str] = {}

    for line in lines:
        # Extract image
        url = _extract_image_url(line)
        if url:
            image = url
            continue
        clean = line.replace("**", "").strip()
        if line.startswith("**") and not headline and "•" not in line:
            name = clean
        elif "•" in clean:
            headline = clean
        elif match := DATE_PATTERN.match(line):
            dates[match.group(1)] = match.group(2)

    return Profile(
        name=name,
        initials=_compute_initials(name),
        headline=headline,
        birth_date=dates.get("birth_date", ""),
        career_start=dates.get("career_start", ""),
        image=image,
    )


# -- Experience --


def _parse_period_location(lines: list[str]) -> tuple[str, str]:
    """Extract period and location from italic line: *period* - location"""
    for line in lines:
        stripped = line.strip()
        if match := PERIOD_LOCATION_PATTERN.match(stripped):
            return match.group(1).strip(), match.group(2).strip()
        if match := PERIOD_ONLY_PATTERN.match(stripped):
            return match.group(1).strip(), ""
    return "", ""


def _extract_image_url(line: str) -> str:
    """Extract image URL from markdown image syntax. Returns empty string if not found."""
    if match := IMAGE_PATTERN.search(line.strip()):
        return match.group(1)
    return ""


def _extract_logo(lines: list[str]) -> str:
    """Extract logo image (first image after period/location, before content sections)."""
    past_period = False
    for line in lines:
        stripped = line.strip()
        # Skip until we're past the period line
        if PERIOD_LOCATION_PATTERN.match(stripped) or PERIOD_ONLY_PATTERN.match(
            stripped
        ):
            past_period = True
            continue
        # For education: period is just "YYYY-YYYY - Location"
        if re.match(r"^\d{4}", stripped):
            past_period = True
            continue
        if not past_period:
            continue
        # Stop at content sections
        if stripped.startswith("#") or _is_bullet_item(line):
            break
        # Found logo image
        url = _extract_image_url(line)
        if url:
            return url
    return ""


def _is_paragraph_line(line: str) -> bool:
    """Check if line is plain paragraph text (not metadata, heading, bullet, or image)."""
    stripped = line.strip()
    if not stripped:
        return False
    return not any(stripped.startswith(prefix) for prefix in ("*", "#", "-", "!["))


def _is_tech_stack_section(line: str) -> bool:
    """Check if line starts a tech stack section."""
    return line.strip().startswith(f"{SECTION_H4} Tech stack")


def _is_section_heading(line: str, level: str) -> bool:
    """Check if line is a section heading at the specified level."""
    return line.strip().startswith(level)


def _extract_experience_content(lines: list[str]) -> tuple[list[str], list[str]]:
    """Extract description and tech_stack from experience block.

    Returns (description, tech_stack) where description is a list of:
    - Paragraphs (plain text lines), or
    - Bullet points (lines starting with '- ')

    Tech stack is extracted from #### Tech stack section if present.
    Content AFTER #### Tech stack is NOT included in description.
    """
    description: list[str] = []
    tech_stack: list[str] = []
    in_tech_section = False

    for line in lines:
        stripped = line.strip()

        # Detect #### Tech stack section start
        if _is_tech_stack_section(line):
            in_tech_section = True
            continue

        # Detect any other #### section (stops tech stack parsing)
        if _is_section_heading(line, SECTION_H4):
            in_tech_section = False
            continue

        # Parse tech stack bullets
        if in_tech_section and stripped.startswith("- "):
            tech_stack.append(stripped[2:])
            continue

        # Skip if we're in tech section but not a bullet (empty lines, etc.)
        if in_tech_section:
            continue

        # Collect description: paragraphs or bullet points (before any #### section)
        if _is_paragraph_line(line):
            description.append(stripped)
        elif stripped.startswith("- "):
            description.append(stripped[2:])

    return description, tech_stack


def _parse_header_with_link(header: str) -> tuple[str, str, str] | None:
    """Parse 'Title @ [Company](url)' format. Returns (title, company, url) or None."""
    if match := HEADER_PATTERN.match(header):
        title, company, url = match.groups()
        return title, company, url
    return None


def _parse_experiences(content: str) -> list[Experience]:
    experiences: list[Experience] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        header = lines[0][4:].strip()  # Remove "### "

        parsed = _parse_header_with_link(header)
        if not parsed:
            continue

        title, company, company_url = parsed
        period, location = _parse_period_location(lines[1:])

        # Extract logo (first image after period/location, before projects)
        logo = _extract_logo(lines[1:])

        # Check for projects (##### headings)
        has_projects = SECTION_H5 in block
        projects = list(_parse_projects(block)) if has_projects else []

        # Extract description and tech_stack (only relevant for experiences without projects)
        if has_projects:
            description: list[str] = []
            tech_stack: list[str] = []
        else:
            description, tech_stack = _extract_experience_content(lines[1:])

        experiences.append(
            Experience(
                title=title,
                company=company,
                company_url=company_url,
                period=period,
                location=location,
                description=description,
                tech_stack=tech_stack,
                projects=projects,
                logo=logo,
            )
        )

    return experiences


# -- Projects --


BULLET_PREFIX = "- "
INDENT_CHARS = ("\t", "  ")


def _is_bullet_item(line: str) -> bool:
    """Check if line is a bullet list item."""
    return line.strip().startswith(BULLET_PREFIX)


def _is_indented(line: str) -> bool:
    """Check if line is indented (tab or spaces)."""
    return line.startswith(INDENT_CHARS)


def _extract_bullet_text(line: str) -> str:
    """Remove bullet marker and strip whitespace."""
    return line.strip()[len(BULLET_PREFIX) :].strip()


def _parse_bullet_content(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Parse structured bullet content into description, role, and tech_stack."""
    description: list[str] = []
    role: list[str] = []
    tech_stack: list[str] = []
    current = description  # Default target

    for line in lines:
        stripped = line.strip()

        # Category headers (top-level, not indented)
        if stripped == f"{BULLET_PREFIX}Role":
            current = role
        elif stripped == f"{BULLET_PREFIX}Tech stack":
            current = tech_stack
        # Sub-items (indented) - check BEFORE top-level bullets
        elif _is_indented(line):
            item = _extract_bullet_text(line)
            if item:
                current.append(item)
        # Top-level bullets (description only)
        elif _is_bullet_item(line):
            if current is description:
                description.append(_extract_bullet_text(line))

    return description, role, tech_stack


def _parse_projects(block: str) -> Iterator[Project]:
    """Parse ##### project blocks within an experience."""
    for proj_block in _split_blocks(block, "#####"):
        lines = proj_block.split("\n")
        title = lines[0][6:].strip()  # Remove "##### "

        # Extract image URL
        image = ""
        for line in lines[1:]:
            image = _extract_image_url(line)
            if image:
                break

        description, role, tech_stack = _parse_bullet_content(lines[1:])

        yield Project(
            title=title,
            image=image,
            description=description,
            role=role,
            tech_stack=tech_stack,
        )


# -- Skills --


def _parse_skills(content: str) -> list[SkillCategory]:
    categories: list[SkillCategory] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        title = lines[0][4:].strip()

        image = ""
        items: list[str] = []

        for line in lines[1:]:
            url = _extract_image_url(line)
            if url:
                image = url
            elif _is_bullet_item(line):
                items.append(_extract_bullet_text(line))

        categories.append(SkillCategory(title=title, image=image, items=items))

    return categories


# -- Certifications --


def _parse_certifications(content: str) -> list[Certification]:
    certs: list[Certification] = []

    for block in _split_blocks(content, "###"):
        # Extract HTML blocks embedded in this certification
        cleaned_block, html_blocks = extract_html_blocks(block)
        html_embed = "\n".join(html_blocks)

        lines = cleaned_block.split("\n")
        title = lines[0][4:].strip()
        description = " ".join(
            ln.strip() for ln in lines[1:] if ln.strip() and not ln.startswith("#")
        )
        certs.append(
            Certification(title=title, description=description, html_embed=html_embed)
        )

    return certs


# -- Education --


def _parse_education(content: str) -> list[Education]:
    entries: list[Education] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        header = lines[0][4:].strip()

        parsed = _parse_header_with_link(header)
        if not parsed:
            continue

        degree, institution, institution_url = parsed

        # Period and location from line like "2013-2016 - Mons, Belgium"
        period, location = "", ""
        for line in lines[1:]:
            stripped = line.strip()
            if re.match(r"^\d{4}", stripped):
                parts = stripped.split(" - ", 1)
                period = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ""
                break

        # Extract logo
        logo = _extract_logo(lines[1:])

        # Topics (bullet points) and distinction
        topics: list[str] = []
        distinction = ""
        for line in lines[1:]:
            stripped = line.strip()
            if _is_bullet_item(line):
                topics.append(_extract_bullet_text(line))
            elif "distinction" in stripped.lower() or "obtained" in stripped.lower():
                distinction = stripped

        entries.append(
            Education(
                degree=degree,
                institution=institution,
                institution_url=institution_url,
                period=period,
                location=location,
                topics=topics,
                distinction=distinction,
                logo=logo,
            )
        )

    return entries


# -- Languages --


def _parse_languages(content: str) -> list[Language]:
    languages: list[Language] = []

    for line in content.split("\n"):
        if match := LANGUAGE_PATTERN.match(line.strip()):
            languages.append(
                Language(
                    name=match.group(1),
                    level=match.group(2),
                    percentage=int(match.group(3)),
                )
            )

    return languages


# -- Links (Contact/Socials) --


def _parse_links(content: str) -> list[Link]:
    links: list[Link] = []

    for line in content.split("\n"):
        stripped = line.strip()
        if not _is_bullet_item(line):
            continue

        if match := LINK_PATTERN.search(stripped):
            links.append(Link(name=match.group(1), url=match.group(2)))
        elif "@" in stripped:
            email = _extract_bullet_text(line)
            links.append(Link(name=email, url=f"mailto:{email}"))

    return links
