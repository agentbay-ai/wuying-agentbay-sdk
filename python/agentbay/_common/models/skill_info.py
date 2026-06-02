"""Data models for Skills feature."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SkillInfo:
    """Represents a single skill's metadata.

    Attributes:
        name: The unique name of the skill (kebab-case).
        description: A human-readable description of the skill.
        skill_id: The unique identifier of the skill.
    """
    name: str
    description: str
    skill_id: str = ""


@dataclass
class SkillsMetadataResult:
    """Result returned by AsyncSkillsService.get_metadata().

    Attributes:
        skills: List of SkillInfo items.
        skills_root_path: The root directory path where skills are stored in the sandbox.
    """
    skills: List[SkillInfo] = field(default_factory=list)
    skills_root_path: str = ""
