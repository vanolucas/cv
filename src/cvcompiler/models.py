"""Data models for CV structure."""

from dataclasses import dataclass, field


@dataclass
class Project:
    title: str
    image: str
    description: list[str]
    role: list[str]
    tech_stack: list[str]


@dataclass
class Experience:
    title: str
    company: str
    company_url: str
    period: str
    location: str
    description: list[str]  # Paragraphs or bullet points
    tech_stack: list[str]
    projects: list[Project]
    logo: str = ""


@dataclass
class SkillCategory:
    title: str
    image: str
    items: list[str]


@dataclass
class Certification:
    title: str
    description: str
    html_embed: str = ""


@dataclass
class Education:
    degree: str
    institution: str
    institution_url: str
    period: str
    location: str
    topics: list[str]
    distinction: str
    logo: str = ""


@dataclass
class Language:
    name: str
    level: str
    percentage: int


@dataclass
class Link:
    name: str
    url: str


@dataclass
class Profile:
    name: str
    initials: str
    headline: str
    birth_date: str  # ISO format for client-side calculation
    career_start: str  # ISO format for client-side calculation
    image: str = ""


@dataclass
class CV:
    profile: Profile
    experiences: list[Experience] = field(default_factory=list)
    skills: list[SkillCategory] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    languages: list[Language] = field(default_factory=list)
    contact: list[Link] = field(default_factory=list)
    socials: list[Link] = field(default_factory=list)
    html_embeds: dict[str, list[str]] = field(
        default_factory=dict
    )  # section -> HTML blocks
    google_analytics_id: str = ""
    canonical_url: str = ""
