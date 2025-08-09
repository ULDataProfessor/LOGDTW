"""
Player class for LOGDTW2002
Handles player data, stats, inventory, and progression
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from game.skills import Skill
from game.crew import Crew, CrewMember
from game.ship_customization import ShipCustomization
from game.diplomacy import Diplomacy

@dataclass
class Item:
    """Represents an item in the game"""
    name: str
    description: str
    value: int
    item_type: str  # weapon, armor, consumable, equipment, trade_good
    damage: int = 0
    defense: int = 0
    weight: float = 1.0
    quantity: int = 1

@dataclass
class CargoHold:
    """Represents a cargo hold compartment"""
    name: str
    capacity: int
    current_cargo: List[Item] = field(default_factory=list)
    cargo_type: str = "general"  # general, weapons, perishable, etc.

class Player:
    """Player character with stats, inventory, and progression"""
    
    def __init__(self, name: str = "Captain"):
        # Basic info
        self.name = name
        self.ship_name = "Voyager"
        
        # Core stats
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Health and resources
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        self.mental_health = 100
        self.max_mental_health = 100
        self.fuel = 100
        self.max_fuel = 100

        # Currency and resources
        self.credits = 1000

        # Titles earned through achievements
        self.titles: List[str] = []
        
        # Stats
        self.stats = {
            'strength': 10,
            'intelligence': 10,
            'charisma': 10,
            'agility': 10,
            'endurance': 10,
            'perception': 10
        }
        
        # Skills
        self.skills = {
            'combat': Skill("Combat", "Fighting and weapon skills"),
            'piloting': Skill("Piloting", "Ship navigation and control"),
            'engineering': Skill("Engineering", "Ship and equipment repair"),
            'trading': Skill("Trading", "Commerce and negotiation"),
            'exploration': Skill("Exploration", "Discovery and mapping"),
            'survival': Skill("Survival", "Environmental adaptation"),
            'knowledge': Skill("Knowledge", "Academic and research skills"),
            'tactics': Skill("Tactics", "Strategic planning and combat tactics"),
            'culture': Skill("Culture", "Understanding of different societies")
        }
        
        # Equipment
        self.equipped = {
            'weapon': None,
            'armor': None,
            'shield': None,
            'accessory': None
        }
        
        # Inventory
        self.inventory = []
        self.max_inventory = 20

        # Crafting materials
        self.materials: Dict[str, int] = {}
        
        # Ship information
        self.ship = {
            'name': self.ship_name,
            'class': 'Explorer',
            'cargo_capacity': 50,
            'fuel_efficiency': 1.0,
            'shield_capacity': 100,
            'weapon_systems': 50,
            'engine_power': 100
        }

        # Ship customization
        self.ship_customization = ShipCustomization(self.ship)
        
        # Cargo holds
        self.cargo_holds = self._create_cargo_holds()
        
        # Reputation with different factions
        self.reputation = {
            'Federation': 0,
            'Pirates': 0,
            'Scientists': 0,
            'Traders': 0,
            'Neutral': 0
        }

        # Diplomacy system handles standings and treaties
        self.diplomacy = Diplomacy(list(self.reputation.keys()))
        
        # Coordinates
        self.coordinates = (0, 0, 0)

        # Starting items
        self._add_starting_items()

        # Crew management
        self.crew = Crew()

    # ------------------------------------------------------------------
    # Crew command helpers
    def hire_crew_member(self, name: str, role: str = "unassigned", skills: Optional[Dict[str, int]] = None) -> CrewMember:
        """Recruit a new crew member."""
        member = CrewMember(name=name, role=role, skills=skills or {})
        self.crew.hire(member)
        return member

    def assign_crew_role(self, name: str, role: str) -> bool:
        """Assign a role to an existing crew member."""
        return self.crew.assign_role(name, role)

    def interact_with_crew(self, name: str, interaction: str) -> bool:
        """Interact with a crew member affecting morale."""
        return self.crew.interact(name, interaction)

    def get_crew_bonus(self, category: str) -> float:
        """Return total crew bonus for a category."""
        return self.crew.get_total_bonus(category)
    
    def _create_cargo_holds(self) -> List[CargoHold]:
        """Create cargo holds for the ship"""
        holds = [
            CargoHold("Main Cargo Bay", 20, cargo_type="general"),
            CargoHold("Weapons Locker", 5, cargo_type="weapons"),
            CargoHold("Perishable Storage", 3, cargo_type="perishable"),
            CargoHold("Valuable Cargo", 2, cargo_type="valuable"),
            CargoHold("Bulk Storage", 10, cargo_type="bulk")
        ]
        return holds
    
    def _add_starting_items(self):
        """Add starting items to player inventory"""
        starting_items = [
            Item("Laser Pistol", "Basic energy weapon", 50, "weapon", damage=15),
            Item("Light Armor", "Basic protective suit", 30, "armor", defense=10),
            Item("Med Kit", "Basic medical supplies", 25, "consumable"),
            Item("Energy Shield", "Personal protective field", 40, "shield", defense=5),
            Item("Repair Tool", "Basic repair equipment", 20, "equipment"),
            Item("Navigation Computer", "Advanced navigation system", 60, "equipment"),
        ]
        
        for item in starting_items:
            self.add_item(item)
    
    def change_name(self, new_name: str) -> bool:
        """Change player name"""
        if new_name.strip():
            self.name = new_name.strip()
            return True
        return False
    
    def change_ship_name(self, new_name: str) -> bool:
        """Change ship name"""
        if new_name.strip():
            self.ship_name = new_name.strip()
            self.ship['name'] = new_name.strip()
            return True
        return False
    
    def gain_experience(self, amount: int):
        """Gain experience points"""
        self.experience += amount

        # Check for level up
        while self.experience >= self.experience_to_next:
            self.level_up()

    def add_experience(self, amount: int) -> bool:
        """Add experience and return True if a level up occurred."""
        previous_level = self.level
        self.gain_experience(amount)
        return self.level > previous_level
    
    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.experience -= self.experience_to_next
        
        # Increase stats
        for stat in self.stats:
            self.stats[stat] += random.randint(1, 3)
        
        # Increase max health and energy
        self.max_health += 10
        self.max_energy += 5
        self.max_fuel += 5
        
        # Restore health and energy
        self.health = self.max_health
        self.energy = self.max_energy
        self.fuel = self.max_fuel
        
        # Calculate new experience requirement
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Gain skill points
        for skill in self.skills.values():
            skill.gain_experience(random.randint(5, 15))

    def get_skill_level(self, skill_name: str) -> int:
        """Get the level of the specified skill, or 0 if not found."""
        skill = self.skills.get(skill_name)
        return skill.level if skill else 0
    
    def add_item(self, item: Item) -> bool:
        """Add item to inventory.

        Trade goods with the same name stack using the quantity attribute
        rather than occupying multiple inventory slots.
        """
        # First try to stack trade goods
        if item.item_type == 'trade_good':
            for inv_item in self.inventory:
                if (
                    inv_item.item_type == 'trade_good'
                    and inv_item.name.lower() == item.name.lower()
                ):
                    inv_item.quantity += item.quantity
                    return True

        # No existing stack found; check inventory capacity
        if len(self.inventory) >= self.max_inventory:
            return False

        self.inventory.append(item)
        return True

    # Ship upgrade interface
    def install_upgrade(self, component_name: str) -> bool:
        """Install a ship component upgrade."""
        return self.ship_customization.install_component(component_name)

    def remove_upgrade(self, slot: str) -> bool:
        """Remove an installed ship component."""
        return self.ship_customization.remove_component(slot)
    
    def remove_item(self, item_name: str, quantity: int = 1) -> Optional[Item]:
        """Remove item from inventory by name and quantity"""
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower():
                if item.quantity > quantity:
                    item.quantity -= quantity
                    return item
                else:
                    return self.inventory.pop(i)
        return None
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get item from inventory by name"""
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None
    
    def equip_item(self, item_name: str) -> bool:
        """Equip an item"""
        item = self.get_item(item_name)
        if not item:
            return False
        
        if item.item_type == 'weapon':
            slot = 'weapon'
        elif item.item_type == 'armor':
            slot = 'armor'
        elif item.item_type == 'shield':
            slot = 'shield'
        else:
            slot = 'accessory'
        
        # Unequip current item
        if self.equipped[slot]:
            self.inventory.append(self.equipped[slot])
        
        # Equip new item
        self.equipped[slot] = item
        self.remove_item(item_name)
        return True
    
    def unequip_item(self, slot: str) -> bool:
        """Unequip an item"""
        if slot not in self.equipped:
            return False
        
        if self.equipped[slot]:
            self.inventory.append(self.equipped[slot])
            self.equipped[slot] = None
            return True
        
        return False
    
    def get_total_damage(self) -> int:
        """Calculate total damage including equipped items"""
        total = self.stats['strength'] // 2

        if self.equipped['weapon']:
            total += self.equipped['weapon'].damage

        # Crew combat bonus
        total += int(self.get_crew_bonus('combat'))
        return total
    
    def get_total_defense(self) -> int:
        """Calculate total defense including equipped items"""
        total = self.stats['endurance'] // 2
        
        if self.equipped['armor']:
            total += self.equipped['armor'].defense
        
        if self.equipped['shield']:
            total += self.equipped['shield'].defense
        
        return total
    
    def add_credits(self, amount: int):
        """Add credits to player"""
        self.credits += amount
    
    def spend_credits(self, amount: int) -> bool:
        """Spend credits"""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
    
    def add_health(self, amount: int):
        """Add health to player"""
        self.health = min(self.max_health, self.health + amount)
    
    def take_damage(self, amount: int):
        """Take damage"""
        self.health = max(0, self.health - amount)
    
    def add_energy(self, amount: int):
        """Add energy to player"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def use_energy(self, amount: int) -> bool:
        """Use energy"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def add_mental_health(self, amount: int):
        """Add mental health to player"""
        self.mental_health = min(self.max_mental_health, self.mental_health + amount)

    def use_mental_health(self, amount: int) -> bool:
        """Use mental health"""
        if self.mental_health >= amount:
            self.mental_health -= amount
            return True
        return False

    def add_fuel(self, amount: int):
        """Add fuel to player"""
        self.fuel = min(self.max_fuel, self.fuel + amount)
    
    def use_fuel(self, amount: int) -> bool:
        """Use fuel"""
        if self.fuel >= amount:
            self.fuel -= amount
            return True
        return False

    # Travel ------------------------------------------------------
    def calculate_travel_cost(self, distance: int) -> int:
        """Calculate fuel cost for travel considering crew bonuses."""
        base_cost = distance
        bonus = self.get_crew_bonus('piloting') / 100
        cost = int(base_cost * (1 - bonus))
        return max(1, cost)
    
    def get_cargo_hold(self, hold_name: str) -> Optional[CargoHold]:
        """Get cargo hold by name"""
        for hold in self.cargo_holds:
            if hold.name.lower() == hold_name.lower():
                return hold
        return None
    
    def add_cargo(self, item: Item, hold_name: str = "Main Cargo Bay") -> bool:
        """Add item to cargo hold"""
        hold = self.get_cargo_hold(hold_name)
        if not hold:
            return False
        
        # Check cargo hold capacity
        current_weight = sum(item.weight for item in hold.current_cargo)
        if current_weight + item.weight > hold.capacity:
            return False
        
        hold.current_cargo.append(item)
        return True
    
    def remove_cargo(self, item_name: str, hold_name: str = "Main Cargo Bay") -> Optional[Item]:
        """Remove item from cargo hold"""
        hold = self.get_cargo_hold(hold_name)
        if not hold:
            return None
        
        for i, item in enumerate(hold.current_cargo):
            if item.name.lower() == item_name.lower():
                return hold.current_cargo.pop(i)
        return None
    
    def get_cargo_summary(self) -> Dict:
        """Get summary of all cargo holds"""
        summary = {
            'total_items': 0,
            'total_value': 0,
            'holds': []
        }
        
        for hold in self.cargo_holds:
            hold_summary = {
                'name': hold.name,
                'capacity': hold.capacity,
                'used': len(hold.current_cargo),
                'items': hold.current_cargo,
                'value': sum(item.value for item in hold.current_cargo)
            }
            summary['holds'].append(hold_summary)
            summary['total_items'] += len(hold.current_cargo)
            summary['total_value'] += hold_summary['value']
        
        return summary
    
    def change_reputation(self, faction: str, amount: int):
        """Change reputation with a faction"""
        if faction in self.reputation:
            self.reputation[faction] = max(-100, min(100, self.reputation[faction] + amount))
    
    def get_reputation_level(self, faction: str) -> str:
        """Get reputation level with a faction"""
        if faction not in self.reputation:
            return "Unknown"
        
        rep = self.reputation[faction]
        if rep >= 80:
            return "Hero"
        elif rep >= 60:
            return "Friend"
        elif rep >= 40:
            return "Ally"
        elif rep >= 20:
            return "Neutral"
        elif rep >= 0:
            return "Distrusted"
        elif rep >= -20:
            return "Hostile"
        elif rep >= -40:
            return "Enemy"
        elif rep >= -60:
            return "Hated"
        else:
            return "Wanted"
    
    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health > 0
    
    def can_afford(self, cost: int) -> bool:
        """Check if player can afford something"""
        return self.credits >= cost
    
    def has_item(self, item_name: str) -> bool:
        """Check if player has an item"""
        return self.get_item(item_name) is not None
    
    def get_inventory_value(self) -> int:
        """Calculate total value of inventory"""
        return sum(item.value for item in self.inventory)

    def get_equipment_value(self) -> int:
        """Calculate total value of equipped items"""
        return sum(item.value for item in self.equipped.values() if item)

    def get_total_wealth(self) -> int:
        """Calculate total wealth (credits + inventory + equipment)"""
        return self.credits + self.get_inventory_value() + self.get_equipment_value()

    # -- Diplomacy interactions -----------------------------------------
    def improve_relationship(self, faction: str, amount: int) -> int:
        """Improve standing with a faction and return the new value."""
        new_rep = self.diplomacy.change_standing(faction, abs(amount))
        self.reputation[faction] = new_rep
        return new_rep

    def ruin_relationship(self, faction: str, amount: int) -> int:
        """Decrease standing with a faction and return the new value."""
        new_rep = self.diplomacy.change_standing(faction, -abs(amount))
        self.reputation[faction] = new_rep
        return new_rep

    def form_treaty(self, faction: str, treaty_type: str) -> None:
        """Form a treaty with a faction."""
        self.diplomacy.form_treaty(faction, treaty_type)

    def break_treaty(self, faction: str) -> None:
        """Break an existing treaty with a faction."""
        self.diplomacy.break_treaty(faction)

    def has_treaty(self, faction: str, treaty_type: Optional[str] = None) -> bool:
        """Check if a treaty exists with a faction."""
        return self.diplomacy.has_treaty(faction, treaty_type)
