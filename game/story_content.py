"""Story content module for LOGDTW2002

This module provides a unified interface to all story content types. The actual
content data is stored in separate files for better organization:
- faction_storylines.py: Faction storyline definitions
- campaign_missions.py: Campaign mission definitions
- character_backstories.py: Character backstory definitions
- lore_entries.py: Lore entry definitions

All story content types are defined in story_types.py
"""

from typing import List, Dict, Optional

# Import data from separate files
from game.faction_storylines import FACTION_STORIES
from game.campaign_missions import CAMPAIGN_MISSIONS
from game.character_backstories import CHARACTER_BACKSTORIES
from game.lore_entries import LORE_ENTRIES

# Export types for convenience
from game.story_types import (
    FactionStoryline,
    CampaignMission,
    CharacterBackstory,
    LoreEntry,
)

# Re-export data for backward compatibility
__all__ = [
    "FactionStoryline",
    "CampaignMission",
    "CharacterBackstory",
    "LoreEntry",
    "FACTION_STORIES",
    "CAMPAIGN_MISSIONS",
    "CHARACTER_BACKSTORIES",
    "LORE_ENTRIES",
    "get_faction_storyline",
    "get_campaign_missions",
    "get_campaign_mission_by_id",
    "get_available_campaign_missions",
    "get_faction_campaign_missions",
    "get_character_backstory",
    "get_lore_entry",
]


def get_faction_storyline(faction: str) -> Optional[FactionStoryline]:
    """Retrieve storyline for a faction"""
    return FACTION_STORIES.get(faction)


def get_campaign_missions() -> List[CampaignMission]:
    """Return list of campaign missions"""
    return CAMPAIGN_MISSIONS


def get_campaign_mission_by_id(mission_id: str) -> Optional[CampaignMission]:
    """Get a specific campaign mission by ID"""
    for mission in CAMPAIGN_MISSIONS:
        if mission.mission_id == mission_id:
            return mission
    return None


def get_available_campaign_missions(completed_mission_ids: List[str]) -> List[CampaignMission]:
    """Get campaign missions that are available based on completed prerequisites"""
    available = []
    for mission in CAMPAIGN_MISSIONS:
        if not mission.prerequisites or all(prereq in completed_mission_ids for prereq in mission.prerequisites):
            if mission.mission_id not in completed_mission_ids:
                available.append(mission)
    return available


def get_faction_campaign_missions(faction: str) -> List[CampaignMission]:
    """Get all campaign missions for a specific faction"""
    return [mission for mission in CAMPAIGN_MISSIONS if mission.faction == faction]


def get_character_backstory(name: str) -> Optional[CharacterBackstory]:
    """Get backstory for a character"""
    return CHARACTER_BACKSTORIES.get(name)


def get_lore_entry(topic: str) -> Optional[LoreEntry]:
    """Retrieve lore entry by topic"""
    return LORE_ENTRIES.get(topic)
