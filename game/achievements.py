from dataclasses import dataclass
from typing import Callable, Dict, List, Set

from game.player import Player
from game.world import World


@dataclass
class Achievement:
    """Represents a single achievement definition"""

    id: str
    name: str
    description: str
    criteria: Callable[[Player, World], bool]
    title_reward: str


class AchievementSystem:
    """Manages achievement definitions and unlocking"""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {
            "rich_captain": Achievement(
                id="rich_captain",
                name="Rich Captain",
                description="Accumulate 2000 credits.",
                criteria=lambda player, world: player.credits >= 2000,
                title_reward="Wealthy Trader",
            ),
            "sector_explorer": Achievement(
                id="sector_explorer",
                name="Sector Explorer",
                description="Discover 3 sectors.",
                criteria=lambda player, world: len(getattr(world, "discovered_sectors", [])) >= 3,
                title_reward="Explorer",
            ),
            "seasoned_captain": Achievement(
                id="seasoned_captain",
                name="Seasoned Captain",
                description="Reach level 5.",
                criteria=lambda player, world: player.level >= 5,
                title_reward="Veteran",
            ),
        }
        self.unlocked: Set[str] = set()

    def check(self, player: Player, world: World) -> List[Achievement]:
        """Check all achievements and unlock those whose criteria are met"""
        newly_unlocked = []
        for ach in self.achievements.values():
            if ach.id not in self.unlocked and ach.criteria(player, world):
                self.unlocked.add(ach.id)
                newly_unlocked.append(ach)
                if ach.title_reward and hasattr(player, "titles"):
                    if ach.title_reward not in player.titles:
                        player.titles.append(ach.title_reward)
        return newly_unlocked

    def get_unlocked(self) -> List[str]:
        return list(self.unlocked)

    def get_unlocked_names(self) -> List[str]:
        return [self.achievements[a_id].name for a_id in self.unlocked if a_id in self.achievements]

    def load(self, unlocked_ids: List[str], player: Player = None):
        """Load unlocked achievements from a list"""
        self.unlocked = set(unlocked_ids or [])
        if player is not None:
            player.titles = [
                self.achievements[a_id].title_reward
                for a_id in self.unlocked
                if a_id in self.achievements and self.achievements[a_id].title_reward
            ]

    def reset(self):
        self.unlocked.clear()
