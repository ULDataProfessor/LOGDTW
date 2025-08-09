from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ShipComponent:
    """Represents an upgrade component for a ship."""
    name: str
    slot: str
    stats: Dict[str, int]


@dataclass
class ShipCustomization:
    """Manages ship upgrade slots and installation/removal of components."""
    ship: Dict[str, int]
    slots: Dict[str, Optional[ShipComponent]] = field(default_factory=lambda: {
        "engine": None,
        "shield": None,
        "weapon": None,
    })
    catalog: Dict[str, ShipComponent] = field(default_factory=lambda: {
        "engine_mk2": ShipComponent("Engine Mk II", "engine", {"engine_power": 20}),
        "shield_mk2": ShipComponent("Shield Mk II", "shield", {"shield_capacity": 50}),
        "weapon_mk2": ShipComponent("Weapon Mk II", "weapon", {"weapon_systems": 30}),
    })

    def __post_init__(self) -> None:
        # Load any existing upgrades from the ship data without re-applying stats
        upgrades = self.ship.get("upgrades", {})
        self.load_from_dict(upgrades, apply_stats=False)

    def install_component(self, component_name: str) -> bool:
        """Install a component into its designated slot."""
        component = self.catalog.get(component_name)
        if not component:
            return False

        slot = component.slot
        if self.slots.get(slot) is not None:
            return False

        self.slots[slot] = component
        for stat, value in component.stats.items():
            self.ship[stat] = self.ship.get(stat, 0) + value
        self.ship.setdefault("upgrades", {})[slot] = component.name
        return True

    def remove_component(self, slot: str) -> bool:
        """Remove a component from the specified slot."""
        component = self.slots.get(slot)
        if component is None:
            return False

        for stat, value in component.stats.items():
            self.ship[stat] = self.ship.get(stat, 0) - value
        self.slots[slot] = None
        if "upgrades" in self.ship:
            self.ship["upgrades"].pop(slot, None)
        return True

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Return a dictionary representation of installed upgrades."""
        return {slot: comp.name if comp else None for slot, comp in self.slots.items()}

    def load_from_dict(self, upgrades: Dict[str, Optional[str]], apply_stats: bool = True) -> None:
        """Load upgrades from a dictionary representation."""
        for slot, name in upgrades.items():
            component = None
            if name:
                component = next((c for c in self.catalog.values() if c.name == name), None)
            self.slots[slot] = component
            if component and apply_stats:
                for stat, value in component.stats.items():
                    self.ship[stat] = self.ship.get(stat, 0) + value
        if upgrades:
            self.ship["upgrades"] = {slot: name for slot, name in upgrades.items() if name}
