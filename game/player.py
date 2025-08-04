"""
Player class for LOGDTW2002
Handles player stats, inventory, and progression
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Item:
    """Represents an item in the game"""
    name: str
    description: str
    value: int
    item_type: str  # weapon, armor, consumable, trade_good, etc.
    damage: int = 0
    defense: int = 0
    weight: float = 0.0

@dataclass
class Skill:
    """Represents a player skill"""
    name: str
    level: int = 1
    experience: int = 0
    max_level: int = 100
    
    def add_experience(self, amount: int) -> bool:
        """Add experience to skill, return True if leveled up"""
        self.experience += amount
        if self.experience >= self.level * 100:
            if self.level < self.max_level:
                self.level += 1
                self.experience = 0
                return True
        return False

class Player:
    """Player character with stats, inventory, and progression"""
    
    def __init__(self, name: str = "Adventurer"):
        self.name = name
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Core stats
        self.stats = {
            'strength': 10,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10
        }
        
        # Combat stats
        self.max_health = 100
        self.health = self.max_health
        self.max_energy = 100
        self.energy = self.max_energy
        
        # Space travel stats
        self.fuel = 100
        self.max_fuel = 100
        self.credits = 1000
        
        # Skills
        self.skills = {
            'combat': Skill('Combat'),
            'pilot': Skill('Pilot'),
            'trading': Skill('Trading'),
            'engineering': Skill('Engineering'),
            'navigation': Skill('Navigation'),
            'diplomacy': Skill('Diplomacy')
        }
        
        # Inventory
        self.inventory: List[Item] = []
        self.equipped = {
            'weapon': None,
            'armor': None,
            'shield': None
        }
        
        # Starting equipment
        self._give_starting_equipment()
        
        # Ship stats
        self.ship = {
            'name': 'Rusty Freighter',
            'class': 'Freighter',
            'cargo_capacity': 100,
            'fuel_efficiency': 1.0,
            'weapon_slots': 2,
            'defense_rating': 5
        }
        
        # Quest progress
        self.active_quests = []
        self.completed_quests = []
        
        # Reputation with different factions
        self.reputation = {
            'Federation': 0,
            'Pirates': 0,
            'Traders': 0,
            'Scientists': 0
        }

    def _give_starting_equipment(self):
        """Give player starting equipment"""
        starting_items = [
            Item("Laser Pistol", "A basic energy weapon", 50, "weapon", damage=15),
            Item("Light Armor", "Basic protective gear", 30, "armor", defense=5),
            Item("Med Kit", "Restores health", 25, "consumable"),
            Item("Energy Cell", "Power source for weapons", 10, "consumable"),
            Item("Repair Kit", "Fixes ship damage", 40, "consumable"),
            Item("Navigation Computer", "Helps with space travel", 100, "equipment")
        ]
        
        for item in starting_items:
            self.add_item(item)

    def add_experience(self, amount: int) -> bool:
        """Add experience to player, return True if leveled up"""
        self.experience += amount
        if self.experience >= self.experience_to_next:
            self.level_up()
            return True
        return False

    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = self.level * 100
        
        # Increase stats
        for stat in self.stats:
            self.stats[stat] += random.randint(1, 3)
        
        # Increase max health and energy
        self.max_health += 10
        self.max_energy += 5
        self.health = self.max_health
        self.energy = self.max_energy
        
        return True

    def add_item(self, item: Item) -> bool:
        """Add item to inventory"""
        if len(self.inventory) < 50:  # Max inventory size
            self.inventory.append(item)
            return True
        return False

    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove item from inventory by name"""
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower():
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
            self.equipped['weapon'] = item
        elif item.item_type == 'armor':
            self.equipped['armor'] = item
        elif item.item_type == 'shield':
            self.equipped['shield'] = item
        
        return True

    def unequip_item(self, slot: str) -> Optional[Item]:
        """Unequip an item"""
        if slot in self.equipped and self.equipped[slot]:
            item = self.equipped[slot]
            self.equipped[slot] = None
            return item
        return None

    def heal(self, amount: int):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)

    def take_damage(self, amount: int):
        """Take damage"""
        self.health = max(0, self.health - amount)

    def use_energy(self, amount: int) -> bool:
        """Use energy, return False if not enough"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def restore_energy(self, amount: int):
        """Restore energy"""
        self.energy = min(self.max_energy, self.energy + amount)

    def use_fuel(self, amount: int) -> bool:
        """Use fuel, return False if not enough"""
        if self.fuel >= amount:
            self.fuel -= amount
            return True
        return False

    def add_fuel(self, amount: int):
        """Add fuel"""
        self.fuel = min(self.max_fuel, self.fuel + amount)

    def add_credits(self, amount: int):
        """Add credits"""
        self.credits += amount

    def spend_credits(self, amount: int) -> bool:
        """Spend credits, return False if not enough"""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False

    def get_total_damage(self) -> int:
        """Get total damage from equipped weapon"""
        base_damage = self.stats['strength'] // 2
        weapon_damage = self.equipped['weapon'].damage if self.equipped['weapon'] else 0
        return base_damage + weapon_damage

    def get_total_defense(self) -> int:
        """Get total defense from equipped armor"""
        base_defense = self.stats['constitution'] // 2
        armor_defense = self.equipped['armor'].defense if self.equipped['armor'] else 0
        shield_defense = self.equipped['shield'].defense if self.equipped['shield'] else 0
        return base_defense + armor_defense + shield_defense

    def get_skill_level(self, skill_name: str) -> int:
        """Get level of a specific skill"""
        if skill_name in self.skills:
            return self.skills[skill_name].level
        return 0

    def add_skill_experience(self, skill_name: str, amount: int) -> bool:
        """Add experience to a skill, return True if leveled up"""
        if skill_name in self.skills:
            return self.skills[skill_name].add_experience(amount)
        return False

    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health > 0

    def get_status_summary(self) -> Dict:
        """Get a summary of player status"""
        return {
            'name': self.name,
            'level': self.level,
            'health': f"{self.health}/{self.max_health}",
            'energy': f"{self.energy}/{self.max_energy}",
            'fuel': f"{self.fuel}/{self.max_fuel}",
            'credits': self.credits,
            'experience': f"{self.experience}/{self.experience_to_next}",
            'location': 'Unknown'  # Will be set by world
        }