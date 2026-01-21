"""Shared dataclasses for story content types"""

from dataclasses import dataclass
from typing import List


@dataclass
class FactionStoryline:
    """Represents a faction's storyline with missions, objectives, and progression"""
    faction: str
    summary: str
    missions: List[str]
    objectives: List[str] = None
    progression_stages: List[str] = None

    def __post_init__(self):
        if self.objectives is None:
            self.objectives = []
        if self.progression_stages is None:
            self.progression_stages = []


@dataclass
class CampaignMission:
    """Represents a campaign mission with story, objectives, and prerequisites"""
    title: str
    description: str
    faction: str
    reward: int
    mission_id: str = ""
    prerequisites: List[str] = None
    story_text: str = ""
    objectives: List[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.objectives is None:
            self.objectives = []
        if not self.mission_id:
            self.mission_id = self.title.lower().replace(" ", "_")


@dataclass
class CharacterBackstory:
    """Represents a character's backstory"""
    name: str
    backstory: str


@dataclass
class LoreEntry:
    """Represents a lore entry about the game world"""
    topic: str
    content: str

