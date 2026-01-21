"""
Combat system for LOGDTW2002
Handles turn-based combat, enemies, and battle mechanics
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from game.player import Player, Item


@dataclass
class Enemy:
    """Represents an enemy in combat"""

    name: str
    health: int
    max_health: int
    damage: int
    defense: int
    enemy_type: str  # pirate, alien, robot, etc.
    description: str
    loot: List[Item] = None
    experience_reward: int = 0
    credits_reward: int = 0

    def __post_init__(self):
        if self.loot is None:
            self.loot = []


class CombatSystem:
    """Handles combat mechanics and battles"""

    def __init__(self):
        self.in_combat = False
        self.current_enemy = None
        self.player = None
        self.combat_round = 0
        self.combat_log = []

        # Enemy templates - expanded with more variety and difficulty scaling
        self.enemy_templates = {
            # Low-level enemies (levels 1-5)
            "space_pirate": {
                "name": "Space Pirate",
                "health": 50,
                "damage": 15,
                "defense": 5,
                "enemy_type": "pirate",
                "description": "A ruthless space pirate with a laser rifle.",
                "experience_reward": 25,
                "credits_reward": 50,
                "difficulty_level": 1,
            },
            "security_drone": {
                "name": "Security Drone",
                "health": 30,
                "damage": 12,
                "defense": 3,
                "enemy_type": "robot",
                "description": "An automated security system.",
                "experience_reward": 15,
                "credits_reward": 25,
                "difficulty_level": 1,
            },
            "rogue_trader": {
                "name": "Rogue Trader",
                "health": 45,
                "damage": 18,
                "defense": 6,
                "enemy_type": "pirate",
                "description": "A disreputable trader with illegal weapons.",
                "experience_reward": 30,
                "credits_reward": 75,
                "difficulty_level": 2,
            },
            # Mid-level enemies (levels 5-10)
            "alien_raider": {
                "name": "Alien Raider",
                "health": 75,
                "damage": 20,
                "defense": 8,
                "enemy_type": "alien",
                "description": "A mysterious alien with advanced weaponry.",
                "experience_reward": 40,
                "credits_reward": 100,
                "difficulty_level": 3,
            },
            "space_slug": {
                "name": "Space Slug",
                "health": 100,
                "damage": 8,
                "defense": 12,
                "enemy_type": "creature",
                "description": "A massive space-dwelling creature.",
                "experience_reward": 60,
                "credits_reward": 150,
                "difficulty_level": 3,
            },
            "federation_patrol": {
                "name": "Federation Patrol",
                "health": 90,
                "damage": 22,
                "defense": 10,
                "enemy_type": "military",
                "description": "A Federation patrol ship that mistakes you for a threat.",
                "experience_reward": 50,
                "credits_reward": 120,
                "difficulty_level": 4,
            },
            "pirate_captain": {
                "name": "Pirate Captain",
                "health": 120,
                "damage": 25,
                "defense": 12,
                "enemy_type": "pirate",
                "description": "A notorious pirate captain with upgraded weapons.",
                "experience_reward": 75,
                "credits_reward": 200,
                "difficulty_level": 5,
            },
            "alien_scout": {
                "name": "Alien Scout",
                "health": 65,
                "damage": 24,
                "defense": 7,
                "enemy_type": "alien",
                "description": "A fast alien scout ship with advanced sensors.",
                "experience_reward": 55,
                "credits_reward": 140,
                "difficulty_level": 4,
            },
            # High-level enemies (levels 10+)
            "bounty_hunter": {
                "name": "Bounty Hunter",
                "health": 150,
                "damage": 30,
                "defense": 15,
                "enemy_type": "mercenary",
                "description": "A professional bounty hunter with top-tier equipment.",
                "experience_reward": 100,
                "credits_reward": 300,
                "difficulty_level": 6,
            },
            "alien_cruiser": {
                "name": "Alien Cruiser",
                "health": 200,
                "damage": 28,
                "defense": 18,
                "enemy_type": "alien",
                "description": "A massive alien warship with devastating firepower.",
                "experience_reward": 150,
                "credits_reward": 400,
                "difficulty_level": 7,
            },
            "space_kraken": {
                "name": "Space Kraken",
                "health": 250,
                "damage": 20,
                "defense": 20,
                "enemy_type": "creature",
                "description": "A legendary space-dwelling leviathan.",
                "experience_reward": 200,
                "credits_reward": 500,
                "difficulty_level": 8,
            },
            "rogue_ai": {
                "name": "Rogue AI Ship",
                "health": 180,
                "damage": 35,
                "defense": 16,
                "enemy_type": "robot",
                "description": "An autonomous AI-controlled warship gone rogue.",
                "experience_reward": 175,
                "credits_reward": 450,
                "difficulty_level": 8,
            },
            "federation_destroyer": {
                "name": "Federation Destroyer",
                "health": 220,
                "damage": 32,
                "defense": 20,
                "enemy_type": "military",
                "description": "A heavily armed Federation destroyer.",
                "experience_reward": 180,
                "credits_reward": 500,
                "difficulty_level": 9,
            },
        }

    def start_combat(self, player: Player, enemy_type: str = None, difficulty_modifier: float = 1.0) -> bool:
        """Start a combat encounter
        
        Args:
            player: The player character
            enemy_type: Specific enemy type to spawn, or None for random
            difficulty_modifier: Multiplier for enemy stats based on player level/sector
        """
        if self.in_combat:
            return False

        self.player = player
        self.in_combat = True
        self.combat_round = 0
        self.combat_log = []

        # Select enemy based on player level and difficulty
        if enemy_type is None:
            enemy_type = self._select_enemy_by_difficulty(player.level, difficulty_modifier)

        template = self.enemy_templates[enemy_type]
        
        # Scale enemy stats based on player level and difficulty modifier
        level_scaling = 1.0 + (player.level - 1) * 0.1  # 10% per level above 1
        total_scaling = level_scaling * difficulty_modifier
        
        scaled_health = int(template["health"] * total_scaling)
        scaled_damage = int(template["damage"] * total_scaling)
        scaled_defense = int(template["defense"] * total_scaling)
        scaled_exp = int(template["experience_reward"] * total_scaling)
        scaled_credits = int(template["credits_reward"] * total_scaling)
        
        self.current_enemy = Enemy(
            name=template["name"],
            health=scaled_health,
            max_health=scaled_health,
            damage=scaled_damage,
            defense=scaled_defense,
            enemy_type=template["enemy_type"],
            description=template["description"],
            experience_reward=scaled_exp,
            credits_reward=scaled_credits,
        )

        self.combat_log.append(f"A {self.current_enemy.name} appears!")
        self.combat_log.append(self.current_enemy.description)
        return True
    
    def _select_enemy_by_difficulty(self, player_level: int, difficulty_modifier: float) -> str:
        """Select an appropriate enemy based on player level and difficulty"""
        # Filter enemies by difficulty level
        available_enemies = []
        target_difficulty = min(9, max(1, int(player_level / 2) + int(difficulty_modifier * 2)))
        
        for enemy_key, template in self.enemy_templates.items():
            enemy_difficulty = template.get("difficulty_level", 1)
            # Allow enemies within 2 difficulty levels of target
            if abs(enemy_difficulty - target_difficulty) <= 2:
                available_enemies.append(enemy_key)
        
        # If no enemies match, use all enemies
        if not available_enemies:
            available_enemies = list(self.enemy_templates.keys())
        
        # Weight selection: prefer enemies closer to target difficulty
        weights = []
        for enemy_key in available_enemies:
            enemy_difficulty = self.enemy_templates[enemy_key].get("difficulty_level", 1)
            distance = abs(enemy_difficulty - target_difficulty)
            weight = max(0.1, 1.0 - (distance * 0.2))  # Higher weight for closer difficulty
            weights.append(weight)
        
        return random.choices(available_enemies, weights=weights)[0]

    def end_combat(self):
        """End the current combat"""
        self.in_combat = False
        self.current_enemy = None
        self.combat_round = 0
        self.combat_log = []

    def player_attack(self) -> Dict:
        """Player attacks the enemy"""
        if not self.in_combat or not self.current_enemy:
            return {"success": False, "message": "No enemy to attack"}

        self.combat_round += 1

        # Calculate damage
        player_damage = self.player.get_total_damage()
        enemy_defense = self.current_enemy.defense

        # Apply random variation
        damage_variation = random.uniform(0.8, 1.2)
        final_damage = max(1, int((player_damage - enemy_defense) * damage_variation))

        # Apply damage
        self.current_enemy.health = max(0, self.current_enemy.health - final_damage)

        result = {
            "success": True,
            "damage_dealt": final_damage,
            "enemy_health": self.current_enemy.health,
            "message": f"You attack the {self.current_enemy.name} for {final_damage} damage!",
        }

        self.combat_log.append(result["message"])

        # Check if enemy is defeated
        if self.current_enemy.health <= 0:
            result["enemy_defeated"] = True
            result["message"] += f"\nYou defeated the {self.current_enemy.name}!"
            self._give_rewards()
            self.end_combat()
        else:
            # Enemy counter-attack
            enemy_result = self._enemy_attack()
            result["enemy_attack"] = enemy_result

        return result

    def player_defend(self) -> Dict:
        """Player takes defensive stance"""
        if not self.in_combat or not self.current_enemy:
            return {"success": False, "message": "No enemy to defend against"}

        self.combat_round += 1

        # Defending reduces incoming damage
        result = {"success": True, "message": "You take a defensive stance.", "defending": True}

        self.combat_log.append(result["message"])

        # Enemy still attacks but with reduced damage
        enemy_result = self._enemy_attack(defending=True)
        result["enemy_attack"] = enemy_result

        return result

    def player_flee(self) -> Dict:
        """Player attempts to flee from combat"""
        if not self.in_combat:
            return {"success": False, "message": "Not in combat"}

        # Fleeing chance based on player agility
        flee_chance = min(0.8, self.player.stats["agility"] / 20)

        if random.random() < flee_chance:
            result = {"success": True, "message": "You successfully flee from combat!"}
            self.end_combat()
        else:
            result = {"success": False, "message": "You failed to flee!"}
            # Enemy gets a free attack
            enemy_result = self._enemy_attack()
            result["enemy_attack"] = enemy_result

        self.combat_log.append(result["message"])
        return result

    def use_item(self, item_name: str) -> Dict:
        """Use an item during combat"""
        if not self.in_combat:
            return {"success": False, "message": "Not in combat"}

        item = self.player.get_item(item_name)
        if not item:
            return {"success": False, "message": f"You don't have {item_name}"}

        if item.item_type == "consumable":
            return self._use_consumable(item)
        elif item.item_type == "weapon":
            return self._equip_weapon(item)
        else:
            return {"success": False, "message": f"{item_name} cannot be used in combat"}

    def _use_consumable(self, item: Item) -> Dict:
        """Use a consumable item"""
        if item.name == "Med Kit":
            heal_amount = 50
            self.player.heal(heal_amount)
            self.player.remove_item(item.name)
            return {
                "success": True,
                "message": f"You use {item.name} and restore {heal_amount} health!",
            }
        elif item.name == "Energy Cell":
            energy_amount = 30
            self.player.restore_energy(energy_amount)
            self.player.remove_item(item.name)
            return {
                "success": True,
                "message": f"You use {item.name} and restore {energy_amount} energy!",
            }
        else:
            return {"success": False, "message": f"Unknown consumable: {item.name}"}

    def _equip_weapon(self, item: Item) -> Dict:
        """Equip a weapon during combat"""
        if item.item_type != "weapon":
            return {"success": False, "message": f"{item.name} is not a weapon"}

        self.player.equip_item(item.name)
        return {"success": True, "message": f"You equip {item.name}!"}

    def _enemy_attack(self, defending: bool = False) -> Dict:
        """Enemy attacks the player"""
        if not self.current_enemy or not self.player:
            return {"success": False, "message": "No enemy or player"}

        # Calculate damage
        enemy_damage = self.current_enemy.damage
        player_defense = self.player.get_total_defense()

        # Apply random variation
        damage_variation = random.uniform(0.8, 1.2)
        base_damage = max(1, int((enemy_damage - player_defense) * damage_variation))

        # If defending, reduce damage
        if defending:
            base_damage = max(1, base_damage // 2)

        # Apply damage
        self.player.take_damage(base_damage)

        result = {
            "success": True,
            "damage_dealt": base_damage,
            "player_health": self.player.health,
            "message": f"The {self.current_enemy.name} attacks you for {base_damage} damage!",
        }

        self.combat_log.append(result["message"])

        # Check if player is defeated
        if self.player.health <= 0:
            result["player_defeated"] = True
            result["message"] += "\nYou have been defeated!"
            self.end_combat()

        return result

    def _give_rewards(self):
        """Give rewards for defeating the enemy"""
        if not self.current_enemy or not self.player:
            return

        # Give experience using player.add_experience wrapper
        exp_gained = self.current_enemy.experience_reward
        leveled_up = self.player.add_experience(exp_gained)

        # Give credits
        credits_gained = self.current_enemy.credits_reward
        self.player.add_credits(credits_gained)

        # Give loot
        for item in self.current_enemy.loot:
            if self.player.add_item(item):
                self.combat_log.append(f"You found {item.name}!")

        # Add to combat log
        self.combat_log.append(f"You gained {exp_gained} experience and {credits_gained} credits!")

        if leveled_up:
            self.combat_log.append("You leveled up!")

    def get_combat_status(self) -> Dict:
        """Get current combat status"""
        if not self.in_combat:
            return {"in_combat": False}

        return {
            "in_combat": True,
            "round": self.combat_round,
            "enemy": {
                "name": self.current_enemy.name,
                "health": self.current_enemy.health,
                "max_health": self.current_enemy.max_health,
                "description": self.current_enemy.description,
            },
            "player": {
                "health": self.player.health,
                "max_health": self.player.max_health,
                "energy": self.player.energy,
                "max_energy": self.player.max_energy,
            },
            "log": self.combat_log[-5:],  # Last 5 combat messages
        }

    def get_available_actions(self) -> List[str]:
        """Get available combat actions"""
        if not self.in_combat:
            return []

        actions = ["attack", "defend", "flee"]

        # Add item actions based on inventory
        for item in self.player.inventory:
            if item.item_type in ["consumable", "weapon"]:
                actions.append(f"use {item.name}")

        return actions
    
    def get_combat_scenario(self) -> Dict:
        """Generate a random combat scenario description"""
        scenarios = [
            {
                "name": "Ambush",
                "description": "You are ambushed! The enemy has the advantage.",
                "enemy_initiative_bonus": 0.2,
            },
            {
                "name": "Fair Fight",
                "description": "Both combatants spot each other simultaneously.",
                "enemy_initiative_bonus": 0.0,
            },
            {
                "name": "You Have Advantage",
                "description": "You catch the enemy by surprise!",
                "enemy_initiative_bonus": -0.2,
            },
            {
                "name": "Multiple Enemies",
                "description": "You face multiple opponents!",
                "enemy_initiative_bonus": 0.1,
            },
            {
                "name": "Environmental Hazard",
                "description": "Combat takes place in a dangerous environment!",
                "enemy_initiative_bonus": 0.0,
            },
        ]
        
        return random.choice(scenarios)
