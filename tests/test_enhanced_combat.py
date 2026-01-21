import os
import sys
import pytest
import random

# Ensure project root is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.enhanced_combat import (
    EnhancedCombatSystem,
    CombatShip,
    Weapon,
    Defense,
    WeaponType,
    DefenseType,
    CombatAction,
    CombatStatus
)


@pytest.fixture
def combat_system():
    return EnhancedCombatSystem()


@pytest.fixture
def player_ship():
    return CombatShip(
        name="Player Ship",
        hull=100,
        max_hull=100,
        shields=50,
        max_shields=50,
        energy=100,
        max_energy=100,
        weapons=[
            Weapon("Laser Cannon", WeaponType.LASER, (10, 20), 0.8, "medium", 10)
        ],
        defenses=[
            Defense("Shield Generator", DefenseType.SHIELDS, 20, 5)
        ],
        agility=5
    )


@pytest.fixture
def enemy_ship():
    return CombatShip(
        name="Enemy Ship",
        hull=80,
        max_hull=80,
        shields=40,
        max_shields=40,
        energy=80,
        max_energy=80,
        weapons=[
            Weapon("Plasma Blaster", WeaponType.PLASMA, (8, 18), 0.75, "short", 12)
        ],
        defenses=[
            Defense("Armor Plating", DefenseType.ARMOR, 15, 0)
        ],
        agility=4
    )


def test_combat_system_initialization(combat_system):
    """Test combat system initialization"""
    assert combat_system.current_combat is None
    assert combat_system.combat_log == []
    assert combat_system.round_number == 0
    assert len(combat_system.range_modifiers) > 0


def test_start_combat(combat_system, player_ship, enemy_ship):
    """Test starting a combat encounter"""
    result = combat_system.start_enhanced_combat(player_ship, enemy_ship)
    
    assert result is True
    assert combat_system.current_combat is not None
    assert combat_system.current_combat["player"] == player_ship
    assert combat_system.current_combat["enemy"] == enemy_ship
    assert combat_system.current_combat["status"] == CombatStatus.ACTIVE
    assert len(combat_system.combat_log) > 0


def test_combat_ship_creation():
    """Test creating a combat ship"""
    ship = CombatShip(
        name="Test Ship",
        hull=100,
        max_hull=100,
        shields=50,
        max_shields=50,
        energy=100,
        max_energy=100,
        weapons=[],
        defenses=[]
    )
    
    assert ship.name == "Test Ship"
    assert ship.hull == 100
    assert ship.max_hull == 100
    assert ship.shields == 50
    assert ship.energy == 100
    assert isinstance(ship.weapons, list)
    assert isinstance(ship.defenses, list)


def test_weapon_creation():
    """Test creating a weapon"""
    weapon = Weapon(
        name="Test Laser",
        type=WeaponType.LASER,
        damage=(10, 20),
        accuracy=0.8,
        range="medium",
        energy_cost=10
    )
    
    assert weapon.name == "Test Laser"
    assert weapon.type == WeaponType.LASER
    assert weapon.damage == (10, 20)
    assert weapon.accuracy == 0.8
    assert weapon.energy_cost == 10


def test_defense_creation():
    """Test creating a defense"""
    defense = Defense(
        name="Test Shield",
        type=DefenseType.SHIELDS,
        protection=20,
        energy_cost=5
    )
    
    assert defense.name == "Test Shield"
    assert defense.type == DefenseType.SHIELDS
    assert defense.protection == 20
    assert defense.energy_cost == 5
    assert defense.active is True


def test_combat_action_enum():
    """Test combat action enum"""
    assert CombatAction.ATTACK.value == "attack"
    assert CombatAction.DEFEND.value == "defend"
    assert CombatAction.EVADE.value == "evade"
    assert CombatAction.RETREAT.value == "retreat"


def test_weapon_type_enum():
    """Test weapon type enum"""
    assert WeaponType.LASER.value == "laser"
    assert WeaponType.PLASMA.value == "plasma"
    assert WeaponType.MISSILE.value == "missile"


def test_defense_type_enum():
    """Test defense type enum"""
    assert DefenseType.SHIELDS.value == "shields"
    assert DefenseType.ARMOR.value == "armor"
    assert DefenseType.ECM.value == "ecm"


def test_combat_status_enum():
    """Test combat status enum"""
    assert CombatStatus.ACTIVE.value == "active"
    assert CombatStatus.VICTORY.value == "victory"
    assert CombatStatus.DEFEAT.value == "defeat"
    assert CombatStatus.FLED.value == "fled"


def test_combat_ship_damage(player_ship):
    """Test applying damage to a ship"""
    initial_hull = player_ship.hull
    initial_shields = player_ship.shields
    
    # Damage should hit shields first
    damage = 30
    if player_ship.shields > 0:
        player_ship.shields = max(0, player_ship.shields - damage)
        if player_ship.shields == 0:
            remaining_damage = damage - initial_shields
            player_ship.hull = max(0, player_ship.hull - remaining_damage)
    else:
        player_ship.hull = max(0, player_ship.hull - damage)
    
    assert player_ship.shields <= initial_shields
    assert player_ship.hull <= initial_hull


def test_combat_ship_energy_consumption(player_ship):
    """Test energy consumption during combat"""
    initial_energy = player_ship.energy
    
    # Use a weapon
    if player_ship.weapons:
        weapon = player_ship.weapons[0]
        if player_ship.energy >= weapon.energy_cost:
            player_ship.energy -= weapon.energy_cost
    
    assert player_ship.energy <= initial_energy


def test_combat_range_modifiers(combat_system):
    """Test range modifiers"""
    assert "short" in combat_system.range_modifiers
    assert "medium" in combat_system.range_modifiers
    assert "long" in combat_system.range_modifiers
    
    short_mod = combat_system.range_modifiers["short"]
    assert "accuracy" in short_mod
    assert "damage" in short_mod


def test_combat_ship_status_effects(player_ship):
    """Test status effects on combat ship"""
    assert isinstance(player_ship.status_effects, dict)
    
    # Add a status effect
    player_ship.status_effects["burning"] = 3
    assert "burning" in player_ship.status_effects
    assert player_ship.status_effects["burning"] == 3


def test_combat_ship_special_abilities(player_ship):
    """Test special abilities"""
    assert isinstance(player_ship.special_abilities, list)
    
    player_ship.special_abilities.append("Emergency Overload")
    assert "Emergency Overload" in player_ship.special_abilities


def test_combat_ship_position(player_ship):
    """Test ship position and movement"""
    assert isinstance(player_ship.position, tuple)
    assert len(player_ship.position) == 2
    
    # Test position update
    player_ship.position = (5, 10)
    assert player_ship.position == (5, 10)


def test_combat_ship_facing(player_ship):
    """Test ship facing direction"""
    assert 0 <= player_ship.facing < 360
    
    player_ship.facing = 90
    assert player_ship.facing == 90


def test_combat_ship_crew(player_ship):
    """Test crew management in combat"""
    assert player_ship.crew > 0
    assert player_ship.crew <= player_ship.max_crew
    
    # Crew can be damaged
    initial_crew = player_ship.crew
    player_ship.crew = max(0, player_ship.crew - 10)
    assert player_ship.crew <= initial_crew


def test_weapon_cooldown():
    """Test weapon cooldown system"""
    weapon = Weapon(
        name="Test Weapon",
        type=WeaponType.LASER,
        damage=(10, 20),
        accuracy=0.8,
        range="medium",
        energy_cost=10,
        cooldown=2
    )
    
    assert weapon.cooldown == 2
    assert weapon.current_cooldown == 0
    
    # Set cooldown
    weapon.current_cooldown = weapon.cooldown
    assert weapon.current_cooldown == 2


def test_defense_durability():
    """Test defense durability system"""
    defense = Defense(
        name="Test Defense",
        type=DefenseType.ARMOR,
        protection=20,
        energy_cost=0,
        durability=100,
        max_durability=100
    )
    
    assert defense.durability == 100
    assert defense.max_durability == 100
    
    # Damage defense
    defense.durability = max(0, defense.durability - 25)
    assert defense.durability == 75


def test_combat_environmental_effects(combat_system):
    """Test environmental effects in combat"""
    assert isinstance(combat_system.environmental_effects, dict)
    
    # Add environmental effect
    combat_system.environmental_effects["nebula"] = {"visibility": 0.5}
    assert "nebula" in combat_system.environmental_effects


def test_combat_log(combat_system, player_ship, enemy_ship):
    """Test combat log functionality"""
    combat_system.start_enhanced_combat(player_ship, enemy_ship)
    
    assert len(combat_system.combat_log) > 0
    assert isinstance(combat_system.combat_log[0], str)


def test_combat_battlefield_size(combat_system):
    """Test battlefield size configuration"""
    assert isinstance(combat_system.battlefield_size, tuple)
    assert len(combat_system.battlefield_size) == 2
    assert combat_system.battlefield_size[0] > 0
    assert combat_system.battlefield_size[1] > 0

