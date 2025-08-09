#!/usr/bin/env python3
"""
Enhanced Combat System for LOGDTW2002
More engaging combat mechanics with tactics, positioning, and advanced features
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class CombatAction(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    EVADE = "evade"
    SPECIAL = "special"
    ITEM = "item"
    SCAN = "scan"
    RETREAT = "retreat"
    BOARDING = "boarding"
    RAMMING = "ramming"
    HAIL = "hail"

class WeaponType(Enum):
    LASER = "laser"
    PLASMA = "plasma"
    MISSILE = "missile"
    RAILGUN = "railgun"
    TORPEDO = "torpedo"
    ION = "ion"
    BEAM = "beam"
    PULSE = "pulse"

class DefenseType(Enum):
    SHIELDS = "shields"
    ARMOR = "armor"
    ECM = "ecm"  # Electronic Countermeasures
    POINT_DEFENSE = "point_defense"
    EVASION = "evasion"

class CombatStatus(Enum):
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"
    SURRENDERED = "surrendered"
    BOARDING = "boarding"

@dataclass
class Weapon:
    name: str
    type: WeaponType
    damage: Tuple[int, int]  # min, max damage
    accuracy: float
    range: str  # short, medium, long
    energy_cost: int
    special_effects: List[str] = field(default_factory=list)
    cooldown: int = 0
    current_cooldown: int = 0

@dataclass
class Defense:
    name: str
    type: DefenseType
    protection: int
    energy_cost: int
    special_effects: List[str] = field(default_factory=list)
    active: bool = True
    durability: int = 100
    max_durability: int = 100

@dataclass
class CombatShip:
    name: str
    hull: int
    max_hull: int
    shields: int
    max_shields: int
    energy: int
    max_energy: int
    weapons: List[Weapon]
    defenses: List[Defense]
    position: Tuple[int, int] = (0, 0)
    facing: int = 0  # 0-359 degrees
    speed: int = 0
    max_speed: int = 5
    agility: int = 5
    crew: int = 100
    max_crew: int = 100
    ai_type: str = "standard"
    special_abilities: List[str] = field(default_factory=list)
    status_effects: Dict[str, int] = field(default_factory=dict)
    combat_history: List[str] = field(default_factory=list)

@dataclass
class CombatResult:
    winner: str
    loser: str
    rounds: int
    damage_dealt: int
    damage_taken: int
    experience_gained: int
    loot: List[str]
    reputation_change: int
    special_events: List[str]

class EnhancedCombatSystem:
    def __init__(self):
        self.current_combat = None
        self.combat_log = []
        self.round_number = 0
        self.battlefield_size = (20, 20)
        self.environmental_effects = {}
        
        # Combat modifiers
        self.range_modifiers = {
            "short": {"accuracy": 1.2, "damage": 1.1},
            "medium": {"accuracy": 1.0, "damage": 1.0},
            "long": {"accuracy": 0.8, "damage": 0.9}
        }
        
    def start_enhanced_combat(self, player_ship: CombatShip, enemy_ship: CombatShip, 
                            environment: Dict = None) -> bool:
        """Start an enhanced combat encounter"""
        self.current_combat = {
            "player": player_ship,
            "enemy": enemy_ship,
            "status": CombatStatus.ACTIVE,
            "environment": environment or {},
            "round": 0,
            "initiative": self._roll_initiative(player_ship, enemy_ship)
        }
        
        self.combat_log = [f"Combat initiated between {player_ship.name} and {enemy_ship.name}!"]
        self._apply_environmental_effects()
        
        return True
    
    def _roll_initiative(self, ship1: CombatShip, ship2: CombatShip) -> str:
        """Determine who goes first based on agility and random factor"""
        roll1 = random.randint(1, 20) + ship1.agility
        roll2 = random.randint(1, 20) + ship2.agility
        
        return "player" if roll1 >= roll2 else "enemy"
    
    def _apply_environmental_effects(self):
        """Apply environmental effects to combat"""
        env = self.current_combat["environment"]
        
        if env.get("asteroid_field"):
            self.combat_log.append("⚠️ Asteroid field detected - accuracy reduced, cover available")
        if env.get("nebula"):
            self.combat_log.append("🌌 Nebula interference - sensors disrupted, stealth enhanced")
        if env.get("solar_flare"):
            self.combat_log.append("☀️ Solar flare activity - energy weapons boosted, shields weakened")
    
    def get_combat_options(self, ship: CombatShip) -> List[Dict]:
        """Get available combat options for a ship"""
        options = []
        
        # Basic actions
        options.append({
            "action": CombatAction.ATTACK,
            "description": "Attack with weapons",
            "available": len(ship.weapons) > 0 and ship.energy >= 10
        })
        
        options.append({
            "action": CombatAction.DEFEND,
            "description": "Raise defenses and reduce incoming damage",
            "available": True
        })
        
        options.append({
            "action": CombatAction.EVADE,
            "description": "Evasive maneuvers to avoid attacks",
            "available": ship.energy >= 5
        })
        
        # Special actions
        if "boarding_party" in ship.special_abilities:
            options.append({
                "action": CombatAction.BOARDING,
                "description": "Launch boarding party",
                "available": ship.crew >= 20 and self._get_distance_to_enemy() <= 2
            })
        
        if ship.speed >= 3:
            options.append({
                "action": CombatAction.RAMMING,
                "description": "Ramming attack (high risk/reward)",
                "available": ship.hull >= ship.max_hull * 0.3
            })
        
        options.append({
            "action": CombatAction.SCAN,
            "description": "Scan enemy for weaknesses",
            "available": ship.energy >= 5
        })
        
        options.append({
            "action": CombatAction.HAIL,
            "description": "Attempt to communicate",
            "available": True
        })
        
        options.append({
            "action": CombatAction.RETREAT,
            "description": "Attempt to flee combat",
            "available": True
        })
        
        return options
    
    def execute_combat_action(self, actor: str, action: CombatAction, 
                            target: str = None, weapon_index: int = 0) -> Dict:
        """Execute a combat action"""
        if not self.current_combat or self.current_combat["status"] != CombatStatus.ACTIVE:
            return {"success": False, "message": "No active combat"}
        
        actor_ship = self.current_combat[actor]
        target_ship = self.current_combat[target or ("enemy" if actor == "player" else "player")]
        
        result = {"success": True, "message": "", "effects": []}
        
        if action == CombatAction.ATTACK:
            result = self._execute_attack(actor_ship, target_ship, weapon_index)
        elif action == CombatAction.DEFEND:
            result = self._execute_defend(actor_ship)
        elif action == CombatAction.EVADE:
            result = self._execute_evade(actor_ship)
        elif action == CombatAction.SCAN:
            result = self._execute_scan(actor_ship, target_ship)
        elif action == CombatAction.BOARDING:
            result = self._execute_boarding(actor_ship, target_ship)
        elif action == CombatAction.RAMMING:
            result = self._execute_ramming(actor_ship, target_ship)
        elif action == CombatAction.HAIL:
            result = self._execute_hail(actor_ship, target_ship)
        elif action == CombatAction.RETREAT:
            result = self._execute_retreat(actor_ship)
        
        # Update cooldowns and status effects
        self._update_ship_status(actor_ship)
        self._update_ship_status(target_ship)
        
        # Check for combat end conditions
        self._check_combat_end()
        
        return result
    
    def _execute_attack(self, attacker: CombatShip, target: CombatShip, weapon_index: int) -> Dict:
        """Execute an attack action"""
        if weapon_index >= len(attacker.weapons):
            return {"success": False, "message": "Invalid weapon selection"}
        
        weapon = attacker.weapons[weapon_index]
        
        if weapon.current_cooldown > 0:
            return {"success": False, "message": f"{weapon.name} is cooling down"}
        
        if attacker.energy < weapon.energy_cost:
            return {"success": False, "message": "Insufficient energy"}
        
        # Calculate hit chance
        base_accuracy = weapon.accuracy
        distance = self._get_distance_to_enemy()
        range_modifier = self._get_range_modifier(weapon, distance)
        evasion_modifier = 1.0 - (target.agility * 0.05)
        
        hit_chance = base_accuracy * range_modifier * evasion_modifier
        
        # Environmental modifiers
        env = self.current_combat["environment"]
        if env.get("asteroid_field"):
            hit_chance *= 0.8
        if env.get("nebula"):
            hit_chance *= 0.9
        
        result = {"success": True, "message": "", "effects": []}
        
        if random.random() <= hit_chance:
            # Hit! Calculate damage
            damage = random.randint(weapon.damage[0], weapon.damage[1])
            
            # Apply weapon type modifiers
            damage = self._apply_weapon_modifiers(weapon, target, damage)
            
            # Apply defenses
            damage = self._apply_defenses(target, damage, weapon.type)
            
            # Deal damage
            self._deal_damage(target, damage)
            
            result["message"] = f"{attacker.name} hits {target.name} with {weapon.name} for {damage} damage!"
            result["effects"].append(f"damage_{damage}")
            
            # Special weapon effects
            self._apply_weapon_effects(weapon, target, result)
            
        else:
            result["message"] = f"{attacker.name} misses {target.name} with {weapon.name}!"
        
        # Consume energy and set cooldown
        attacker.energy -= weapon.energy_cost
        weapon.current_cooldown = weapon.cooldown
        
        self.combat_log.append(result["message"])
        return result
    
    def _execute_defend(self, defender: CombatShip) -> Dict:
        """Execute a defend action"""
        # Boost defenses for this round
        defender.status_effects["defending"] = 1
        
        # Regenerate some shields if possible
        if defender.shields < defender.max_shields:
            shield_regen = min(20, defender.max_shields - defender.shields)
            defender.shields += shield_regen
            message = f"{defender.name} raises defenses and regenerates {shield_regen} shield power!"
        else:
            message = f"{defender.name} raises defenses!"
        
        self.combat_log.append(message)
        return {"success": True, "message": message, "effects": ["defending"]}
    
    def _execute_evade(self, evader: CombatShip) -> Dict:
        """Execute an evade action"""
        if evader.energy < 5:
            return {"success": False, "message": "Insufficient energy for evasive maneuvers"}
        
        evader.energy -= 5
        evader.status_effects["evading"] = 1
        
        message = f"{evader.name} executes evasive maneuvers!"
        self.combat_log.append(message)
        return {"success": True, "message": message, "effects": ["evading"]}
    
    def _execute_scan(self, scanner: CombatShip, target: CombatShip) -> Dict:
        """Execute a scan action"""
        if scanner.energy < 5:
            return {"success": False, "message": "Insufficient energy for scanning"}
        
        scanner.energy -= 5
        
        # Reveal information about the target
        scan_info = []
        scan_info.append(f"Hull: {target.hull}/{target.max_hull}")
        scan_info.append(f"Shields: {target.shields}/{target.max_shields}")
        scan_info.append(f"Energy: {target.energy}/{target.max_energy}")
        scan_info.append(f"Weapons: {len(target.weapons)}")
        scan_info.append(f"Crew: {target.crew}/{target.max_crew}")
        
        # Detect weaknesses
        weaknesses = []
        if target.hull < target.max_hull * 0.5:
            weaknesses.append("Hull critically damaged")
        if target.shields < target.max_shields * 0.3:
            weaknesses.append("Shields nearly depleted")
        if target.energy < target.max_energy * 0.2:
            weaknesses.append("Low energy reserves")
        
        message = f"{scanner.name} scans {target.name}"
        result = {
            "success": True, 
            "message": message,
            "scan_data": scan_info,
            "weaknesses": weaknesses
        }
        
        self.combat_log.append(message)
        return result
    
    def _execute_boarding(self, attacker: CombatShip, target: CombatShip) -> Dict:
        """Execute a boarding action"""
        if attacker.crew < 20:
            return {"success": False, "message": "Insufficient crew for boarding party"}
        
        distance = self._get_distance_to_enemy()
        if distance > 2:
            return {"success": False, "message": "Too far away for boarding"}
        
        # Boarding mini-game
        boarding_chance = (attacker.crew / target.crew) * 0.6
        boarding_chance += random.uniform(-0.2, 0.2)
        
        if random.random() <= boarding_chance:
            # Successful boarding
            crew_lost = random.randint(5, 15)
            target_crew_lost = random.randint(10, 25)
            
            attacker.crew -= crew_lost
            target.crew -= target_crew_lost
            
            if target.crew <= 0:
                self.current_combat["status"] = CombatStatus.VICTORY
                message = f"{attacker.name} successfully boards and captures {target.name}!"
            else:
                damage = random.randint(20, 50)
                self._deal_damage(target, damage)
                message = f"{attacker.name} boarding party inflicts {damage} internal damage!"
        else:
            # Failed boarding
            crew_lost = random.randint(10, 20)
            attacker.crew -= crew_lost
            message = f"{attacker.name} boarding attempt fails! {crew_lost} crew members lost!"
        
        self.combat_log.append(message)
        return {"success": True, "message": message}
    
    def _execute_ramming(self, attacker: CombatShip, target: CombatShip) -> Dict:
        """Execute a ramming attack"""
        # High damage to both ships
        attacker_damage = random.randint(30, 60)
        target_damage = random.randint(50, 100)
        
        # Defender can't evade ramming as easily
        if "evading" in target.status_effects:
            target_damage = int(target_damage * 0.7)
        
        self._deal_damage(attacker, attacker_damage)
        self._deal_damage(target, target_damage)
        
        message = f"{attacker.name} rams {target.name}! Both ships take heavy damage!"
        self.combat_log.append(message)
        
        return {"success": True, "message": message, "effects": ["ramming"]}
    
    def _execute_hail(self, hailer: CombatShip, target: CombatShip) -> Dict:
        """Execute a hail/communication attempt"""
        # Chance to end combat peacefully
        surrender_chance = 0.1
        
        if target.hull < target.max_hull * 0.3:
            surrender_chance += 0.3
        if target.crew < target.max_crew * 0.5:
            surrender_chance += 0.2
        
        if random.random() <= surrender_chance:
            self.current_combat["status"] = CombatStatus.SURRENDERED
            message = f"{target.name} surrenders to {hailer.name}!"
        else:
            message = f"{hailer.name} attempts to hail {target.name}, but receives no response!"
        
        self.combat_log.append(message)
        return {"success": True, "message": message}
    
    def _execute_retreat(self, retreater: CombatShip) -> Dict:
        """Execute a retreat attempt"""
        escape_chance = 0.4 + (retreater.agility * 0.05)
        
        if random.random() <= escape_chance:
            self.current_combat["status"] = CombatStatus.FLED
            message = f"{retreater.name} successfully flees from combat!"
        else:
            message = f"{retreater.name} fails to escape!"
        
        self.combat_log.append(message)
        return {"success": True, "message": message}
    
    def _get_distance_to_enemy(self) -> int:
        """Calculate distance between combat ships"""
        player_pos = self.current_combat["player"].position
        enemy_pos = self.current_combat["enemy"].position
        
        dx = abs(player_pos[0] - enemy_pos[0])
        dy = abs(player_pos[1] - enemy_pos[1])
        
        return max(dx, dy)  # Use Chebyshev distance
    
    def _get_range_modifier(self, weapon: Weapon, distance: int) -> float:
        """Get accuracy/damage modifier based on weapon range and distance"""
        if distance <= 3:
            weapon_range = "short"
        elif distance <= 8:
            weapon_range = "medium"
        else:
            weapon_range = "long"
        
        if weapon.range == weapon_range:
            return 1.0
        elif weapon.range == "short" and weapon_range != "short":
            return 0.7
        elif weapon.range == "long" and weapon_range != "long":
            return 0.8
        else:
            return 0.9
    
    def _apply_weapon_modifiers(self, weapon: Weapon, target: CombatShip, damage: int) -> int:
        """Apply weapon type modifiers against target defenses"""
        # Environmental bonuses
        env = self.current_combat["environment"]
        if env.get("solar_flare") and weapon.type in [WeaponType.LASER, WeaponType.PLASMA]:
            damage = int(damage * 1.3)
        
        # Weapon vs defense type modifiers
        for defense in target.defenses:
            if not defense.active:
                continue
                
            if weapon.type == WeaponType.ION and defense.type == DefenseType.SHIELDS:
                damage = int(damage * 1.5)  # Ion weapons vs shields
            elif weapon.type == WeaponType.RAILGUN and defense.type == DefenseType.ARMOR:
                damage = int(damage * 1.3)  # Railgun vs armor
            elif weapon.type == WeaponType.MISSILE and defense.type == DefenseType.POINT_DEFENSE:
                damage = int(damage * 0.5)  # Point defense vs missiles
        
        return damage
    
    def _apply_defenses(self, target: CombatShip, damage: int, weapon_type: WeaponType) -> int:
        """Apply defensive measures to reduce damage"""
        final_damage = damage
        
        # Shield absorption
        if target.shields > 0:
            shield_absorption = min(damage, target.shields)
            target.shields -= shield_absorption
            final_damage -= shield_absorption
        
        # Armor reduction
        for defense in target.defenses:
            if defense.type == DefenseType.ARMOR and defense.active:
                armor_reduction = min(final_damage, defense.protection)
                final_damage -= armor_reduction
                defense.durability -= max(1, damage // 10)
                if defense.durability <= 0:
                    defense.active = False
        
        # Status effect modifiers
        if "defending" in target.status_effects:
            final_damage = int(final_damage * 0.7)
        if "evading" in target.status_effects:
            final_damage = int(final_damage * 0.8)
        
        return max(0, final_damage)
    
    def _deal_damage(self, target: CombatShip, damage: int):
        """Deal damage to a ship's hull"""
        target.hull -= damage
        if target.hull < 0:
            target.hull = 0
    
    def _apply_weapon_effects(self, weapon: Weapon, target: CombatShip, result: Dict):
        """Apply special weapon effects"""
        for effect in weapon.special_effects:
            if effect == "ion_disable":
                target.energy -= 10
                result["effects"].append("energy_drain")
            elif effect == "emp_pulse":
                target.status_effects["systems_disabled"] = 2
                result["effects"].append("emp")
            elif effect == "plasma_burn":
                target.status_effects["burning"] = 3
                result["effects"].append("burning")
    
    def _update_ship_status(self, ship: CombatShip):
        """Update ship status effects and cooldowns"""
        # Update weapon cooldowns
        for weapon in ship.weapons:
            if weapon.current_cooldown > 0:
                weapon.current_cooldown -= 1
        
        # Update status effects
        expired_effects = []
        for effect, duration in ship.status_effects.items():
            ship.status_effects[effect] = duration - 1
            if ship.status_effects[effect] <= 0:
                expired_effects.append(effect)
        
        # Remove expired effects
        for effect in expired_effects:
            del ship.status_effects[effect]
        
        # Apply ongoing effects
        if "burning" in ship.status_effects:
            burn_damage = random.randint(5, 15)
            self._deal_damage(ship, burn_damage)
            self.combat_log.append(f"{ship.name} takes {burn_damage} burn damage!")
    
    def _check_combat_end(self):
        """Check if combat should end"""
        player = self.current_combat["player"]
        enemy = self.current_combat["enemy"]
        
        if player.hull <= 0:
            self.current_combat["status"] = CombatStatus.DEFEAT
        elif enemy.hull <= 0:
            self.current_combat["status"] = CombatStatus.VICTORY
        elif enemy.crew <= 0:
            self.current_combat["status"] = CombatStatus.VICTORY
    
    def get_combat_summary(self) -> Dict:
        """Get current combat status summary"""
        if not self.current_combat:
            return {"active": False}
        
        return {
            "active": self.current_combat["status"] == CombatStatus.ACTIVE,
            "status": self.current_combat["status"].value,
            "round": self.current_combat["round"],
            "player_ship": {
                "hull": f"{self.current_combat['player'].hull}/{self.current_combat['player'].max_hull}",
                "shields": f"{self.current_combat['player'].shields}/{self.current_combat['player'].max_shields}",
                "energy": f"{self.current_combat['player'].energy}/{self.current_combat['player'].max_energy}",
                "status_effects": list(self.current_combat['player'].status_effects.keys())
            },
            "enemy_ship": {
                "name": self.current_combat["enemy"].name,
                "hull": f"{self.current_combat['enemy'].hull}/{self.current_combat['enemy'].max_hull}",
                "shields": f"{self.current_combat['enemy'].shields}/{self.current_combat['enemy'].max_shields}",
                "status_effects": list(self.current_combat['enemy'].status_effects.keys())
            },
            "environment": self.current_combat["environment"],
            "combat_log": self.combat_log[-5:]  # Last 5 messages
        }
    
    def end_combat(self) -> CombatResult:
        """End combat and calculate results"""
        if not self.current_combat:
            return None
        
        status = self.current_combat["status"]
        player = self.current_combat["player"]
        enemy = self.current_combat["enemy"]
        
        if status == CombatStatus.VICTORY:
            winner, loser = "player", "enemy"
            exp_gain = random.randint(50, 200)
            loot = self._generate_combat_loot(enemy)
            rep_change = random.randint(10, 50)
        elif status == CombatStatus.SURRENDERED:
            winner, loser = "player", "enemy"
            exp_gain = random.randint(25, 100)
            loot = self._generate_surrender_loot(enemy)
            rep_change = random.randint(20, 80)
        else:
            winner, loser = "enemy", "player"
            exp_gain = 0
            loot = []
            rep_change = random.randint(-20, -5)
        
        result = CombatResult(
            winner=winner,
            loser=loser,
            rounds=self.current_combat["round"],
            damage_dealt=player.max_hull - player.hull,
            damage_taken=enemy.max_hull - enemy.hull,
            experience_gained=exp_gain,
            loot=loot,
            reputation_change=rep_change,
            special_events=[]
        )
        
        self.current_combat = None
        return result
    
    def _generate_combat_loot(self, enemy: CombatShip) -> List[str]:
        """Generate loot from defeated enemy"""
        loot = []
        
        # Credits
        credits = random.randint(100, 1000)
        loot.append(f"{credits} Credits")
        
        # Possible equipment
        if random.random() < 0.3:
            equipment = random.choice([
                "Weapon Upgrade", "Shield Booster", "Armor Plating",
                "Energy Cell", "Navigation Computer", "Sensor Array"
            ])
            loot.append(equipment)
        
        # Rare materials
        if random.random() < 0.2:
            materials = random.choice([
                "Tritium", "Quantum Crystals", "Advanced Alloys",
                "Antimatter", "Dark Matter", "Zeridium"
            ])
            loot.append(materials)
        
        return loot
    
    def _generate_surrender_loot(self, enemy: CombatShip) -> List[str]:
        """Generate loot from surrendered enemy"""
        loot = []
        
        # More credits for peaceful resolution
        credits = random.randint(200, 800)
        loot.append(f"{credits} Credits")
        
        # Information
        if random.random() < 0.5:
            info = random.choice([
                "Trade Route Information", "Sector Map Data",
                "Faction Intelligence", "Hidden Base Location"
            ])
            loot.append(info)
        
        return loot
    
    def create_combat_ship_from_player(self, player) -> CombatShip:
        """Convert player data to combat ship"""
        weapons = []
        
        # Convert player weapons
        for item in player.inventory:
            if item.type == "weapon":
                weapon = Weapon(
                    name=item.name,
                    type=WeaponType.LASER,  # Default type
                    damage=(item.damage - 5, item.damage + 5),
                    accuracy=0.7 + (item.damage * 0.01),
                    range="medium",
                    energy_cost=10,
                    special_effects=[]
                )
                weapons.append(weapon)
        
        # Default weapon if none equipped
        if not weapons:
            weapons.append(Weapon(
                name="Basic Laser",
                type=WeaponType.LASER,
                damage=(10, 20),
                accuracy=0.75,
                range="medium",
                energy_cost=8
            ))
        
        defenses = [
            Defense(
                name="Energy Shields",
                type=DefenseType.SHIELDS,
                protection=20,
                energy_cost=5
            ),
            Defense(
                name="Hull Armor",
                type=DefenseType.ARMOR,
                protection=15,
                energy_cost=0
            )
        ]

        piloting_skill = player.get_skill_level("piloting")
        leadership_skill = player.get_skill_level("leadership")

        return CombatShip(
            name=player.ship_name,
            hull=player.health,
            max_hull=player.max_health,
            shields=100,
            max_shields=100,
            energy=player.energy,
            max_energy=player.max_energy,
            weapons=weapons,
            defenses=defenses,
            agility=5 + piloting_skill,
            crew=leadership_skill * 10 + 50,
            max_crew=100,
            special_abilities=[]
        )
    
    def create_enemy_combat_ship(self, enemy_type: str) -> CombatShip:
        """Create an enemy combat ship"""
        enemy_templates = {
            "space_pirate": {
                "hull": 80, "shields": 60, "energy": 100,
                "weapons": [("Plasma Cannon", WeaponType.PLASMA, (15, 25))],
                "agility": 6, "crew": 30
            },
            "federation_patrol": {
                "hull": 120, "shields": 100, "energy": 150,
                "weapons": [("Laser Array", WeaponType.LASER, (20, 30))],
                "agility": 4, "crew": 50
            },
            "alien_scout": {
                "hull": 60, "shields": 80, "energy": 120,
                "weapons": [("Ion Beam", WeaponType.ION, (12, 22))],
                "agility": 8, "crew": 20
            }
        }
        
        template = enemy_templates.get(enemy_type, enemy_templates["space_pirate"])
        
        weapons = []
        for weapon_data in template["weapons"]:
            weapons.append(Weapon(
                name=weapon_data[0],
                type=weapon_data[1],
                damage=weapon_data[2],
                accuracy=0.7,
                range="medium",
                energy_cost=12
            ))
        
        defenses = [
            Defense(name="Shields", type=DefenseType.SHIELDS, protection=20, energy_cost=5),
            Defense(name="Armor", type=DefenseType.ARMOR, protection=10, energy_cost=0)
        ]
        
        return CombatShip(
            name=f"{enemy_type.replace('_', ' ').title()}",
            hull=template["hull"],
            max_hull=template["hull"],
            shields=template["shields"],
            max_shields=template["shields"],
            energy=template["energy"],
            max_energy=template["energy"],
            weapons=weapons,
            defenses=defenses,
            agility=template["agility"],
            crew=template["crew"],
            max_crew=template["crew"],
            ai_type=enemy_type
        )
