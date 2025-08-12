"""Story content for LOGDTW2002"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class FactionStoryline:
    faction: str
    summary: str
    missions: List[str]


@dataclass
class CampaignMission:
    title: str
    description: str
    faction: str
    reward: int


@dataclass
class CharacterBackstory:
    name: str
    backstory: str


@dataclass
class LoreEntry:
    topic: str
    content: str


# Sample data for story content
FACTION_STORIES: Dict[str, FactionStoryline] = {
    "Federation": FactionStoryline(
        faction="Federation",
        summary="Protect the core worlds and maintain order.",
        missions=["Secure trade routes", "Investigate anomalies"],
    ),
    "Pirates": FactionStoryline(
        faction="Pirates",
        summary="Rule the outskirts through fear and profit.",
        missions=["Raid convoys", "Smuggle goods"],
    ),
}

CAMPAIGN_MISSIONS: List[CampaignMission] = [
    CampaignMission(
        title="First Contact",
        description="Meet with the alien envoy.",
        faction="Federation",
        reward=5000,
    ),
    CampaignMission(
        title="Black Market Deal",
        description="Secure illegal goods for profit.",
        faction="Pirates",
        reward=3000,
    ),
]

CHARACTER_BACKSTORIES: Dict[str, CharacterBackstory] = {
    "Captain Steele": CharacterBackstory(
        name="Captain Steele", backstory="A decorated Federation officer seeking redemption."
    ),
    "Trader McKenzie": CharacterBackstory(
        name="Trader McKenzie", backstory="A seasoned merchant with a mysterious past."
    ),
}

LORE_ENTRIES: Dict[str, LoreEntry] = {
    "Genesis Torpedo": LoreEntry(
        topic="Genesis Torpedo", content="A mythical weapon said to create worlds."
    ),
    "Old Earth": LoreEntry(
        topic="Old Earth", content="The birthplace of humanity and center of the Federation."
    ),
}


def get_faction_storyline(faction: str) -> Optional[FactionStoryline]:
    """Retrieve storyline for a faction"""
    return FACTION_STORIES.get(faction)


def get_campaign_missions() -> List[CampaignMission]:
    """Return list of campaign missions"""
    return CAMPAIGN_MISSIONS


def get_character_backstory(name: str) -> Optional[CharacterBackstory]:
    """Get backstory for a character"""
    return CHARACTER_BACKSTORIES.get(name)


def get_lore_entry(topic: str) -> Optional[LoreEntry]:
    """Retrieve lore entry by topic"""
    return LORE_ENTRIES.get(topic)
