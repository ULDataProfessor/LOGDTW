import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .dynamic_markets import DynamicMarketSystem, EconomicEvent
from .enhanced_missions import MissionManager
from .player import Player


@dataclass
class GameEvent:
    """Simple representation of an in-game event."""

    name: str
    description: str
    sector_id: Optional[int] = None
    player_specific: bool = False
    resolved: bool = False
    data: Dict = field(default_factory=dict)


class EventEngine:
    """Central event management system.

    The engine coordinates sector-wide and player specific events and can
    interact with other game systems such as missions, markets and travel.
    """

    def __init__(
        self,
        mission_manager: Optional[MissionManager] = None,
        market_system: Optional[DynamicMarketSystem] = None,
        player: Optional[Player] = None,
        travel_event_chance: float = 0.2,
    ):
        self.mission_manager = mission_manager
        self.market_system = market_system
        self.player = player
        self.travel_event_chance = travel_event_chance
        self.forced_travel_event_type: Optional[str] = None
        self.active_events: List[GameEvent] = []

    # ------------------------------------------------------------------
    # Event generation helpers
    # ------------------------------------------------------------------
    def generate_sector_event(self, sector_id: int, event_type: Optional[str] = None) -> GameEvent:
        """Generate a sector-wide event.

        Parameters
        ----------
        sector_id: int
            Sector where the event occurs.
        event_type: Optional[str]
            Optional explicit event type (``"market"``, ``"mission"`` or
            ``"anomaly"``).  When ``None`` a random type is selected.
        """

        if event_type is None:
            event_type = random.choice(["market", "mission", "anomaly"])

        if event_type == "market" and self.market_system:
            self.market_system.trigger_event(EconomicEvent.PIRATE_RAIDS)
            event = GameEvent(
                name="Pirate Activity",
                description="Pirate raids disrupt trade in the sector.",
                sector_id=sector_id,
            )
        elif event_type == "mission" and self.mission_manager:
            mission = self.mission_manager.generate_event_mission(sector_id)
            event = GameEvent(
                name="Mission Available",
                description="A new mission opportunity arises.",
                sector_id=sector_id,
                data={"mission_id": mission.id},
            )
        else:
            event = GameEvent(
                name="Spatial Anomaly",
                description="Strange readings detected in the sector.",
                sector_id=sector_id,
            )

        self.active_events.append(event)
        return event

    def generate_player_event(self, event_type: str) -> Optional[GameEvent]:
        """Generate an event that directly affects the player."""

        if event_type == "pirate_ambush":
            event = GameEvent(
                name="Pirate Ambush",
                description="Pirates attack during travel.",
                player_specific=True,
            )
            if self.player:
                self.player.health = max(0, self.player.health - 20)
        elif event_type == "anomaly":
            event = GameEvent(
                name="Strange Anomaly",
                description="A space-time anomaly is encountered.",
                player_specific=True,
            )
        else:
            return None

        self.active_events.append(event)
        return event

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    def handle_travel(
        self, world, destination: str, force_event: Optional[str] = None
    ) -> Optional[GameEvent]:
        """Handle potential events triggered by travel.

        Parameters
        ----------
        world: World
            The world instance performing the travel.
        destination: str
            Name of the destination location.
        force_event: Optional[str]
            If provided, always triggers this specific event type.
        """

        if force_event is not None:
            event_type = force_event
        else:
            if random.random() > self.travel_event_chance:
                return None
            event_type = self.forced_travel_event_type or random.choice(
                ["pirate_ambush", "anomaly"]
            )

        if event_type in ("pirate_ambush", "anomaly"):
            return self.generate_player_event(event_type)
        else:
            sector = world.locations[destination].sector
            return self.generate_sector_event(sector, event_type)

    # ------------------------------------------------------------------
    def resolve_event(self, event: GameEvent) -> None:
        """Mark an event as resolved and remove it from active events."""

        event.resolved = True
        if event in self.active_events:
            self.active_events.remove(event)
