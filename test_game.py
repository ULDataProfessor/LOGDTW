#!/usr/bin/env python3
"""
Test script for LOGDTW2002
Tests basic game functionality
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.player import Player
from game.world import World
from game.combat import CombatSystem
from game.trading import TradingSystem
from game.quests import QuestSystem
from utils.display import DisplayManager

def test_player():
    """Test player functionality"""
    print("Testing Player...")
    
    player = Player("Test Player")
    
    # Test basic stats
    assert player.name == "Test Player"
    assert player.level == 1
    assert player.health == player.max_health
    assert player.credits == 1000
    
    # Test inventory
    assert len(player.inventory) > 0
    print(f"✓ Player created with {len(player.inventory)} starting items")
    
    # Test experience gain
    leveled_up = player.add_experience(50)
    assert player.experience == 50
    print("✓ Experience system working")
    
    # Test item management
    from game.player import Item
    test_item = Item("Test Item", "A test item", 10, "equipment")
    player.add_item(test_item)
    assert player.get_item("Test Item") is not None
    print("✓ Item management working")
    
    print("✓ Player tests passed!\n")

def test_world():
    """Test world functionality"""
    print("Testing World...")
    
    world = World()
    
    # Test location creation
    assert len(world.locations) > 0
    print(f"✓ World created with {len(world.locations)} locations")
    
    # Test current location
    current_loc = world.get_current_location()
    assert current_loc.name == "Earth Station"
    print("✓ Starting location correct")
    
    # Test travel
    success = world.travel_to("Mars Colony")
    assert success
    assert world.current_location == "Mars Colony"
    print("✓ Travel system working")
    
    # Test market availability
    assert world.can_trade() == True
    print("✓ Market system working")
    
    print("✓ World tests passed!\n")

def test_combat():
    """Test combat functionality"""
    print("Testing Combat...")
    
    combat = CombatSystem()
    player = Player("Test Fighter")
    
    # Test combat start
    success = combat.start_combat(player)
    assert success
    assert combat.in_combat
    assert combat.current_enemy is not None
    print("✓ Combat system initialized")
    
    # Test player attack
    result = combat.player_attack()
    assert result['success']
    print("✓ Combat mechanics working")
    
    print("✓ Combat tests passed!\n")

def test_trading():
    """Test trading functionality"""
    print("Testing Trading...")
    
    trading = TradingSystem()
    player = Player("Test Trader")
    
    # Test market info
    market_info = trading.get_market_info("Earth Station")
    assert market_info['available']
    assert len(market_info['goods']) > 0
    print("✓ Market system working")
    
    # Test buying
    result = trading.buy_item(player, "Earth Station", "Computer Chips", 1)
    assert result['success']
    print("✓ Trading mechanics working")
    
    print("✓ Trading tests passed!\n")

def test_quests():
    """Test quest functionality"""
    print("Testing Quests...")
    
    quests = QuestSystem()
    player = Player("Test Adventurer")
    
    # Test available quests
    available = quests.get_available_quests(player)
    assert len(available) > 0
    print(f"✓ Quest system created {len(available)} available quests")
    
    # Test quest acceptance
    if available:
        quest = available[0]
        result = quests.accept_quest(player, quest.id)
        assert result['success']
        print("✓ Quest acceptance working")
    
    print("✓ Quest tests passed!\n")

def test_display():
    """Test display functionality"""
    print("Testing Display...")
    
    display = DisplayManager()
    player = Player("Test Display")
    world = World()
    
    # Test status display
    display.show_status(player)
    print("✓ Status display working")
    
    # Test location display
    location = world.get_current_location()
    display.show_location(location)
    print("✓ Location display working")
    
    print("✓ Display tests passed!\n")

def main():
    """Run all tests"""
    print("LOGDTW2002 - Game Tests")
    print("=" * 40)
    
    try:
        test_player()
        test_world()
        test_combat()
        test_trading()
        test_quests()
        test_display()
        
        print("🎉 All tests passed! The game is ready to play.")
        print("\nTo start the game, run: python main.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 