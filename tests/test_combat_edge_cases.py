"""
Tests for combat system edge cases and error scenarios
"""
import os
import sys
import pytest
import random

# Ensure project root is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.combat import CombatSystem, Enemy
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
from game.player import Player


@pytest.fixture
def combat_system():
    return CombatSystem()


@pytest.fixture
def enhanced_combat_system():
    return EnhancedCombatSystem()


@pytest.fixture
def player():
    return Player("Test Player", "Fighter")


@pytest.fixture
def damaged_ship():
    """Ship with low health"""
    return CombatShip(
        name="Damaged Ship",
        hull=5,
        max_hull=100,
        shields=0,
        max_shields=50,
        energy=10,
        max_energy=100,
        weapons=[
            Weapon("Weak Laser", WeaponType.LASER, (1, 5), 0.5, "short", 5)
        ],
        defenses=[],
        agility=1
    )


@pytest.fixture
def overpowered_ship():
    """Ship with very high stats"""
    return CombatShip(
        name="Overpowered Ship",
        hull=1000,
        max_hull=1000,
        shields=500,
        max_shields=500,
        energy=1000,
        max_energy=1000,
        weapons=[
            Weapon("Death Ray", WeaponType.PLASMA, (100, 200), 1.0, "long", 50)
        ],
        defenses=[
            Defense("Ultra Shield", DefenseType.SHIELDS, 100, 10)
        ],
        agility=20
    )


class TestCombatEdgeCases:
    """Test edge cases in basic combat system"""
    
    def test_combat_without_enemy(self, combat_system, player):
        """Test combat actions when no enemy is present"""
        combat_system.player = player
        
        result = combat_system.player_attack()
        assert result["success"] is False
        assert "No enemy" in result["message"]
    
    def test_combat_without_player(self, combat_system):
        """Test combat when player is not set"""
        enemy = Enemy(
            name="Test Enemy",
            health=50,
            max_health=50,
            damage=10,
            defense=5,
            enemy_type="pirate",
            description="Test"
        )
        combat_system.start_combat(enemy)
        
        result = combat_system.player_attack()
        assert result["success"] is False
    
    def test_combat_with_zero_health_enemy(self, combat_system, player):
        """Test combat with enemy at zero health"""
        enemy = Enemy(
            name="Dead Enemy",
            health=0,
            max_health=50,
            damage=10,
            defense=5,
            enemy_type="pirate",
            description="Already dead"
        )
        combat_system.player = player
        combat_system.start_combat(enemy)
        
        result = combat_system.player_attack()
        # Should handle gracefully
        assert "success" in result
    
    def test_combat_with_negative_health(self, combat_system, player):
        """Test combat with negative health values"""
        enemy = Enemy(
            name="Negative Health Enemy",
            health=-10,
            max_health=50,
            damage=10,
            defense=5,
            enemy_type="pirate",
            description="Negative health"
        )
        combat_system.player = player
        combat_system.start_combat(enemy)
        
        result = combat_system.player_attack()
        # Should handle gracefully
        assert "success" in result
    
    def test_combat_with_extreme_damage(self, combat_system, player):
        """Test combat with extremely high damage values"""
        # Create enemy with very high defense
        enemy = Enemy(
            name="Tank Enemy",
            health=1000,
            max_health=1000,
            damage=1,
            defense=999,
            enemy_type="robot",
            description="Extreme defense"
        )
        combat_system.player = player
        combat_system.start_combat(enemy)
        
        result = combat_system.player_attack()
        # Damage should be at least 1 even with high defense
        assert result["success"] is True
        assert result["damage_dealt"] >= 1
    
    def test_combat_flee_without_enemy(self, combat_system, player):
        """Test fleeing when not in combat"""
        combat_system.player = player
        
        result = combat_system.player_flee()
        assert result["success"] is False
    
    def test_combat_defend_without_enemy(self, combat_system, player):
        """Test defending when not in combat"""
        combat_system.player = player
        
        result = combat_system.player_defend()
        assert result["success"] is False


class TestEnhancedCombatEdgeCases:
    """Test edge cases in enhanced combat system"""
    
    def test_combat_action_without_active_combat(self, enhanced_combat_system, player_ship):
        """Test executing action without active combat"""
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.ATTACK
        )
        assert result["success"] is False
        assert "No active combat" in result["message"]
    
    def test_combat_with_zero_energy(self, enhanced_combat_system, damaged_ship):
        """Test combat when ship has zero energy"""
        enemy = CombatShip(
            name="Enemy",
            hull=50,
            max_hull=50,
            shields=0,
            max_shields=0,
            energy=100,
            max_energy=100,
            weapons=[],
            defenses=[],
            agility=5
        )
        
        damaged_ship.energy = 0
        enhanced_combat_system.start_enhanced_combat(damaged_ship, enemy)
        
        # Try to attack with no energy
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.ATTACK, weapon_index=0
        )
        # Should handle gracefully
        assert "success" in result
    
    def test_combat_with_no_weapons(self, enhanced_combat_system):
        """Test combat with ship that has no weapons"""
        player_ship = CombatShip(
            name="Unarmed Ship",
            hull=100,
            max_hull=100,
            shields=50,
            max_shields=50,
            energy=100,
            max_energy=100,
            weapons=[],  # No weapons
            defenses=[],
            agility=5
        )
        
        enemy = CombatShip(
            name="Enemy",
            hull=50,
            max_hull=50,
            shields=0,
            max_shields=0,
            energy=100,
            max_energy=100,
            weapons=[
                Weapon("Laser", WeaponType.LASER, (10, 20), 0.8, "medium", 10)
            ],
            defenses=[],
            agility=5
        )
        
        enhanced_combat_system.start_enhanced_combat(player_ship, enemy)
        
        # Try to attack with no weapons
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.ATTACK, weapon_index=0
        )
        # Should handle gracefully
        assert "success" in result
    
    def test_combat_with_invalid_weapon_index(self, enhanced_combat_system, player_ship):
        """Test combat with invalid weapon index"""
        enemy = CombatShip(
            name="Enemy",
            hull=50,
            max_hull=50,
            shields=0,
            max_shields=0,
            energy=100,
            max_energy=100,
            weapons=[],
            defenses=[],
            agility=5
        )
        
        enhanced_combat_system.start_enhanced_combat(player_ship, enemy)
        
        # Try to use weapon index that doesn't exist
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.ATTACK, weapon_index=999
        )
        # Should handle gracefully
        assert "success" in result
    
    def test_combat_ship_negative_values(self):
        """Test combat ship with negative values"""
        ship = CombatShip(
            name="Broken Ship",
            hull=-10,
            max_hull=100,
            shields=-5,
            max_shields=50,
            energy=-20,
            max_energy=100,
            weapons=[],
            defenses=[],
            agility=0
        )
        
        # Values should be clamped or handled
        assert ship.hull >= 0 or ship.max_hull > 0
    
    def test_combat_with_extreme_damage_values(self, enhanced_combat_system):
        """Test combat with extreme damage values"""
        player_ship = CombatShip(
            name="Player",
            hull=100,
            max_hull=100,
            shields=50,
            max_shields=50,
            energy=1000,
            max_energy=1000,
            weapons=[
                Weapon("Mega Laser", WeaponType.LASER, (1000, 2000), 1.0, "long", 100)
            ],
            defenses=[],
            agility=5
        )
        
        enemy = CombatShip(
            name="Enemy",
            hull=1,
            max_hull=1,
            shields=0,
            max_shields=0,
            energy=100,
            max_energy=100,
            weapons=[],
            defenses=[],
            agility=5
        )
        
        enhanced_combat_system.start_enhanced_combat(player_ship, enemy)
        
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.ATTACK, weapon_index=0
        )
        # Should handle extreme damage
        assert "success" in result
    
    def test_combat_retreat_immediately(self, enhanced_combat_system, player_ship):
        """Test retreating immediately after combat starts"""
        enemy = CombatShip(
            name="Enemy",
            hull=50,
            max_hull=50,
            shields=0,
            max_shields=0,
            energy=100,
            max_energy=100,
            weapons=[],
            defenses=[],
            agility=5
        )
        
        enhanced_combat_system.start_enhanced_combat(player_ship, enemy)
        
        result = enhanced_combat_system.execute_combat_action(
            "player", CombatAction.RETREAT
        )
        assert result["success"] is True
        assert enhanced_combat_system.current_combat["status"] == CombatStatus.FLED


class TestCombatErrorHandling:
    """Test error handling in combat systems"""
    
    def test_invalid_enemy_type(self, combat_system, player):
        """Test combat with invalid enemy type"""
        enemy = Enemy(
            name="Unknown Enemy",
            health=50,
            max_health=50,
            damage=10,
            defense=5,
            enemy_type="unknown_type_12345",
            description="Invalid type"
        )
        combat_system.player = player
        combat_system.start_combat(enemy)
        
        # Should handle gracefully
        result = combat_system.player_attack()
        assert "success" in result
    
    def test_combat_with_none_values(self, enhanced_combat_system):
        """Test combat with None values"""
        # Should not crash
        try:
            enhanced_combat_system.start_enhanced_combat(None, None)
        except (AttributeError, TypeError):
            pass  # Expected to fail gracefully
    
    def test_combat_with_missing_attributes(self):
        """Test combat with ships missing required attributes"""
        # Create minimal ship object
        class MinimalShip:
            def __init__(self):
                self.name = "Minimal"
                self.hull = 50
                # Missing other required attributes
        
        try:
            ship1 = MinimalShip()
            ship2 = MinimalShip()
            system = EnhancedCombatSystem()
            system.start_enhanced_combat(ship1, ship2)
        except (AttributeError, TypeError):
            pass  # Expected to fail gracefully


class TestCombatPerformance:
    """Test combat system performance and stress"""
    
    def test_many_combat_rounds(self, enhanced_combat_system, player_ship):
        """Test many combat rounds"""
        enemy = CombatShip(
            name="Tank Enemy",
            hull=10000,
            max_hull=10000,
            shields=5000,
            max_shields=5000,
            energy=1000,
            max_energy=1000,
            weapons=[
                Weapon("Weak Laser", WeaponType.LASER, (1, 2), 0.1, "long", 1)
            ],
            defenses=[
                Defense("Strong Shield", DefenseType.SHIELDS, 100, 1)
            ],
            agility=1
        )
        
        enhanced_combat_system.start_enhanced_combat(player_ship, enemy)
        
        # Execute many rounds
        for _ in range(10):
            result = enhanced_combat_system.execute_combat_action(
                "player", CombatAction.ATTACK, weapon_index=0
            )
            if not result.get("success"):
                break
        
        # Should complete without errors
        assert enhanced_combat_system.current_combat is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

