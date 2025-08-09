"""Diplomacy system for managing faction relationships and treaties."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp ``value`` between ``minimum`` and ``maximum``."""
    return max(minimum, min(maximum, value))


@dataclass
class Diplomacy:
    """Maintain faction standings and treaties.

    The system keeps track of how the player is viewed by various factions and
    manages simple treaties with consequences when relationships sour.
    """

    factions: Optional[List[str]] = None
    standings: Dict[str, int] = field(default_factory=dict)
    treaties: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.factions:
            for faction in self.factions:
                self.standings.setdefault(faction, 0)

    # -- standings ---------------------------------------------------------
    def change_standing(self, faction: str, amount: int) -> int:
        """Adjust reputation with ``faction`` by ``amount``.

        Returns the new standing after applying the change. Standings are kept
        within the -100 to 100 range. If a standing drops below -50, any treaty
        with that faction is automatically broken as a consequence.
        """
        current = self.standings.get(faction, 0)
        new_value = _clamp(current + amount, -100, 100)
        self.standings[faction] = new_value
        self._evaluate_consequences(faction)
        return new_value

    # -- treaties ----------------------------------------------------------
    def form_treaty(self, faction: str, treaty_type: str) -> None:
        """Establish a ``treaty_type`` with ``faction``."""
        self.treaties[faction] = treaty_type

    def break_treaty(self, faction: str) -> None:
        """Terminate any existing treaty with ``faction``."""
        self.treaties.pop(faction, None)

    def has_treaty(self, faction: str, treaty_type: Optional[str] = None) -> bool:
        """Return ``True`` if a treaty exists with ``faction``.

        If ``treaty_type`` is provided, the treaty must match that type.
        """
        current = self.treaties.get(faction)
        if treaty_type is None:
            return current is not None
        return current == treaty_type

    # -- internal helpers --------------------------------------------------
    def _evaluate_consequences(self, faction: str) -> None:
        """Handle consequences of the current standing with ``faction``."""
        if self.standings.get(faction, 0) < -50 and faction in self.treaties:
            self.break_treaty(faction)
