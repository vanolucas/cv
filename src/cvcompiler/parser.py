"""Parser for CV markdown format."""

import re
from typing import Iterator

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


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown into top-level sections."""
    sections: dict[str, str] = {}
    current_section = ""
    current_content: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## ") and not line.startswith("### "):
            if current_section:
                sections[current_section] = "\n".join(current_content)
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content)

    return sections


def _parse_profile(content: str) -> Profile:
    """Extract profile info with date placeholders."""
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    headline = lines[0].replace("**", "").strip() if lines else ""

    # Extract dates from template syntax: {(now - YYYY-MM-DD)}
    birth_date = ""
    career_start = ""
    for line in lines:
        if "years old" in line:
            match = re.search(r"\{?\(now - (\d{4}-\d{2}-\d{2})\)\}?", line)
            if match:
                birth_date = match.group(1)
        if "years of professional experience" in line:
            match = re.search(r"\{?\(now - (\d{4}-\d{2}-\d{2})\)\}?", line)
            if match:
                career_start = match.group(1)

    return Profile(headline=headline, birth_date=birth_date, career_start=career_start)


def _parse_experiences(content: str) -> list[Experience]:
    """Parse experience section into structured data."""
    experiences: list[Experience] = []
    exp_blocks = re.split(r"(?=^### )", content, flags=re.MULTILINE)

    for block in exp_blocks:
        if not block.strip() or not block.startswith("### "):
            continue

        lines = block.split("\n")
        header = lines[0][4:].strip()

        # Parse "Title @ [Company](url)"
        match = re.match(r"(.+?) @ \[(.+?)\]\((.+?)\)", header)
        if not match:
            continue

        title, company, company_url = match.groups()

        # Parse period and location
        period, location = "", ""
        for line in lines[1:]:
            if line.startswith("*") and "-" in line:
                parts = line.strip("*").split(" - ")
                period = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ""
                break

        # Description (non-project text)
        description = ""
        for line in lines[1:]:
            if (
                line.strip()
                and not line.startswith("*")
                and not line.startswith("#")
                and not line.startswith("-")
            ):
                description = line.strip()
                break

        # Tech stack at experience level
        tech_stack = _extract_tech_stack(block)

        # Parse projects
        projects = list(_parse_projects(block))

        experiences.append(
            Experience(
                title=title,
                company=company,
                company_url=company_url,
                period=period,
                location=location,
                description=description,
                tech_stack=tech_stack if not projects else [],
                projects=projects,
            )
        )

    return experiences


def _parse_projects(block: str) -> Iterator[Project]:
    """Parse projects within an experience block."""
    project_blocks = re.split(r"(?=^##### )", block, flags=re.MULTILINE)

    for proj in project_blocks:
        if not proj.startswith("##### "):
            continue

        lines = proj.split("\n")
        title = lines[0][6:].strip()

        # Extract image
        image = ""
        for line in lines:
            if line.strip().startswith("!["):
                match = re.search(r"!\[.*?\]\((.+?)\)", line)
                if match:
                    image = match.group(1)
                break

        # Parse bullet points
        description: list[str] = []
        role: list[str] = []
        tech_stack: list[str] = []
        current_category = "description"

        for line in lines[1:]:
            stripped = line.strip()
            if stripped == "- Role":
                current_category = "role"
            elif stripped == "- Tech stack":
                current_category = "tech_stack"
            elif stripped.startswith("- ") and not stripped.endswith(":"):
                if current_category == "description":
                    description.append(stripped[2:])
            elif stripped.startswith("\t- ") or stripped.startswith("  - "):
                item = stripped.lstrip("\t- ").lstrip("  - ").strip("- ")
                if current_category == "role":
                    role.append(item)
                elif current_category == "tech_stack":
                    tech_stack.append(item)
                elif current_category == "description":
                    description.append(item)

        yield Project(
            title=title,
            image=image,
            description=description,
            role=role,
            tech_stack=tech_stack,
        )


def _extract_tech_stack(content: str) -> list[str]:
    """Extract tech stack from #### Tech stack section."""
    if "#### Tech stack" not in content:
        return []

    parts = content.split("#### Tech stack")
    if len(parts) < 2:
        return []

    stack_section = parts[1].split("####")[0]
    items = []
    for line in stack_section.split("\n"):
        if line.strip().startswith("- "):
            items.append(line.strip()[2:])
    return items


def _parse_skills(content: str) -> list[SkillCategory]:
    """Parse skills section into categories."""
    categories: list[SkillCategory] = []
    cat_blocks = re.split(r"(?=^### )", content, flags=re.MULTILINE)

    for block in cat_blocks:
        if not block.startswith("### "):
            continue

        lines = block.split("\n")
        title = lines[0][4:].strip()

        # Extract image
        image = ""
        items: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("!["):
                match = re.search(r"!\[.*?\]\((.+?)\)", stripped)
                if match:
                    image = match.group(1)
            elif stripped.startswith("- "):
                items.append(stripped[2:])

        categories.append(SkillCategory(title=title, image=image, items=items))

    return categories


def _parse_certifications(content: str) -> list[Certification]:
    """Parse certification section."""
    certs: list[Certification] = []
    cert_blocks = re.split(r"(?=^### )", content, flags=re.MULTILINE)

    for block in cert_blocks:
        if not block.startswith("### "):
            continue

        lines = block.split("\n")
        title = lines[0][4:].strip()
        description = " ".join(
            line.strip()
            for line in lines[1:]
            if line.strip() and not line.startswith("#")
        )

        certs.append(Certification(title=title, description=description))

    return certs


def _parse_education(content: str) -> list[Education]:
    """Parse education section."""
    entries: list[Education] = []
    edu_blocks = re.split(r"(?=^### )", content, flags=re.MULTILINE)

    for block in edu_blocks:
        if not block.startswith("### "):
            continue

        lines = block.split("\n")
        header = lines[0][4:].strip()

        # Parse "Degree @ [Institution](url)"
        match = re.match(r"(.+?) @ \[(.+?)\]\((.+?)\)", header)
        if not match:
            continue

        degree, institution, institution_url = match.groups()

        # Parse period and location
        period, location = "", ""
        for line in lines[1:]:
            stripped = line.strip()
            if re.match(r"^\d{4}", stripped):
                parts = stripped.split(" - ")
                period = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ""
                break

        # Topics and distinction
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


def _parse_languages(content: str) -> list[Language]:
    """Parse languages section."""
    languages: list[Language] = []

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        # Parse "- French: native (100%)"
        match = re.match(r"- (.+?): (.+?) \((\d+)%\)", stripped)
        if match:
            languages.append(
                Language(
                    name=match.group(1),
                    level=match.group(2),
                    percentage=int(match.group(3)),
                )
            )

    return languages


def _parse_links(content: str) -> list[Link]:
    """Parse links section (Contact/Socials)."""
    links: list[Link] = []

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        # Parse markdown link or email
        link_match = re.search(r"\[(.+?)\]\((.+?)\)", stripped)
        if link_match:
            links.append(Link(name=link_match.group(1), url=link_match.group(2)))
        elif "@" in stripped:
            email = stripped[2:].strip()
            links.append(Link(name=email, url=f"mailto:{email}"))

    return links
