"""Crew management system for LOGDTW2002.

Handles recruitment, role assignment, morale and skill bonuses
that affect various game systems such as combat, travel and trading.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CrewMember:
    """Represents a crew member aboard the player's ship."""

    name: str
    role: str = "unassigned"
    skills: Dict[str, int] = field(default_factory=lambda: {
        "combat": 0,
        "piloting": 0,
        "trading": 0,
    })
    morale: int = 100  # 0-100

    def get_bonus(self, category: str) -> float:
        """Return effective bonus for a skill category.

        Bonus is the skill level scaled by morale. Morale acts as a
        percentage effectiveness multiplier.
        """
        base = self.skills.get(category, 0)
        return base * (self.morale / 100)

    def adjust_morale(self, amount: int) -> None:
        """Adjust morale by a given amount keeping it in 0-100."""
        self.morale = max(0, min(100, self.morale + amount))


class Crew:
    """Manages the player's crew."""

    def __init__(self) -> None:
        self.members: List[CrewMember] = []

    # Recruitment -------------------------------------------------
    def hire(self, member: CrewMember) -> None:
        """Add a new crew member to the roster."""
        self.members.append(member)

    # Role management ---------------------------------------------
    def assign_role(self, name: str, role: str) -> bool:
        """Assign a role to a crew member by name."""
        member = self.get_member(name)
        if not member:
            return False
        member.role = role
        return True

    # Interaction -------------------------------------------------
    def interact(self, name: str, interaction: str) -> bool:
        """Interact with a crew member to influence morale.

        Simple interactions:
        - 'praise': increase morale by 10
        - 'scold': decrease morale by 10
        """
        member = self.get_member(name)
        if not member:
            return False
        if interaction == "praise":
            member.adjust_morale(10)
        elif interaction == "scold":
            member.adjust_morale(-10)
        else:
            return False
        return True

    # Utility -----------------------------------------------------
    def get_member(self, name: str) -> Optional[CrewMember]:
        for m in self.members:
            if m.name.lower() == name.lower():
                return m
        return None

    def get_total_bonus(self, category: str) -> float:
        """Aggregate bonus from all crew members for a category."""
        return sum(m.get_bonus(category) for m in self.members)
