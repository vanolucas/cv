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
    description: str
    tech_stack: list[str]
    projects: list[Project]


@dataclass
class SkillCategory:
    title: str
    image: str
    items: list[str]


@dataclass
class Certification:
    title: str
    description: str


@dataclass
class Education:
    degree: str
    institution: str
    institution_url: str
    period: str
    location: str
    topics: list[str]
    distinction: str


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
