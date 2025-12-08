"""Parser for CV markdown format."""

import re
from collections.abc import Iterator

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

# Regex patterns
HEADER_PATTERN = re.compile(r"(.+?) @ \[(.+?)\]\((.+?)\)")
PERIOD_LOCATION_PATTERN = re.compile(r"^\*(.+?)\*\s*-\s*(.+)$")
PERIOD_ONLY_PATTERN = re.compile(r"^\*(.+?)\*$")
IMAGE_PATTERN = re.compile(r"!\[.*?\]\((.+?)\)")
DATE_PATTERN = re.compile(r"(\w+)\s*=\s*(\d{4}-\d{2}-\d{2})")
LANGUAGE_PATTERN = re.compile(r"- (.+?): (.+?) \((\d+)%\)")
LINK_PATTERN = re.compile(r"\[(.+?)\]\((.+?)\)")


def parse_cv(content: str) -> CV:
    """Parse markdown CV content into structured data."""
    sections = _split_sections(content)

    return CV(
        profile=_parse_profile(sections.get("Profile", "")),
        experiences=_parse_experiences(sections.get("Experience", "")),
        skills=_parse_skills(sections.get("Skills and Technologies", "")),
        certifications=_parse_certifications(sections.get("Certification", "")),
        education=_parse_education(sections.get("Education", "")),
        languages=_parse_languages(sections.get("Languages", "")),
        contact=_parse_links(sections.get("Contact", "")),
        socials=_parse_links(sections.get("Socials", "")),
    )


# -- Section splitting --


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown into top-level (##) sections."""
    sections: dict[str, str] = {}
    current_section = ""
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## ") and not line.startswith("### "):
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = line[3:].strip()
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
    dates: dict[str, str] = {}

    for line in lines:
        # Skip images
        if line.startswith("!["):
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


def _is_paragraph_line(line: str) -> bool:
    """Check if line is plain paragraph text (not metadata, heading, bullet, or image)."""
    stripped = line.strip()
    return bool(
        stripped
        and not stripped.startswith("*")
        and not stripped.startswith("#")
        and not stripped.startswith("-")
        and not stripped.startswith("![")
    )


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
        if stripped.startswith("#### Tech stack"):
            in_tech_section = True
            continue

        # Detect any other #### section (stops tech stack parsing)
        if stripped.startswith("#### "):
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


def _parse_experiences(content: str) -> list[Experience]:
    experiences: list[Experience] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        header = lines[0][4:].strip()  # Remove "### "

        match = HEADER_PATTERN.match(header)
        if not match:
            continue

        title, company, company_url = match.groups()
        period, location = _parse_period_location(lines[1:])

        # Check for projects (##### headings)
        has_projects = "##### " in block
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
            )
        )

    return experiences


# -- Projects --


def _parse_bullet_content(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Parse structured bullet content into description, role, and tech_stack."""
    description: list[str] = []
    role: list[str] = []
    tech_stack: list[str] = []
    current = description  # Default target

    for line in lines:
        stripped = line.strip()

        # Category headers
        if stripped == "- Role":
            current = role
        elif stripped == "- Tech stack":
            current = tech_stack
        # Top-level bullets (not sub-items, not category headers)
        elif stripped.startswith("- ") and not stripped.endswith(":"):
            if current is description:
                description.append(stripped[2:])
        # Sub-items (indented with tab or spaces)
        elif line.startswith("\t") or line.startswith("  "):
            item = stripped.lstrip("- ").strip()
            if item:
                current.append(item)

    return description, role, tech_stack


def _parse_projects(block: str) -> Iterator[Project]:
    """Parse ##### project blocks within an experience."""
    for proj_block in _split_blocks(block, "#####"):
        lines = proj_block.split("\n")
        title = lines[0][6:].strip()  # Remove "##### "

        # Extract image URL
        image = ""
        for line in lines[1:]:
            if match := IMAGE_PATTERN.search(line.strip()):
                image = match.group(1)
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
            stripped = line.strip()
            if match := IMAGE_PATTERN.search(stripped):
                image = match.group(1)
            elif stripped.startswith("- "):
                items.append(stripped[2:])

        categories.append(SkillCategory(title=title, image=image, items=items))

    return categories


# -- Certifications --


def _parse_certifications(content: str) -> list[Certification]:
    certs: list[Certification] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        title = lines[0][4:].strip()
        description = " ".join(
            ln.strip() for ln in lines[1:] if ln.strip() and not ln.startswith("#")
        )
        certs.append(Certification(title=title, description=description))

    return certs


# -- Education --


def _parse_education(content: str) -> list[Education]:
    entries: list[Education] = []

    for block in _split_blocks(content, "###"):
        lines = block.split("\n")
        header = lines[0][4:].strip()

        match = HEADER_PATTERN.match(header)
        if not match:
            continue

        degree, institution, institution_url = match.groups()

        # Period and location from line like "2013-2016 - Mons, Belgium"
        period, location = "", ""
        for line in lines[1:]:
            stripped = line.strip()
            if re.match(r"^\d{4}", stripped):
                parts = stripped.split(" - ", 1)
                period = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ""
                break

        # Topics (bullet points) and distinction
        topics: list[str] = []
        distinction = ""
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("- "):
                topics.append(stripped[2:])
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
        if not stripped.startswith("- "):
            continue

        if match := LINK_PATTERN.search(stripped):
            links.append(Link(name=match.group(1), url=match.group(2)))
        elif "@" in stripped:
            email = stripped[2:].strip()
            links.append(Link(name=email, url=f"mailto:{email}"))

    return links
