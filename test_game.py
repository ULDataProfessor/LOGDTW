#!/usr/bin/env python3
"""
Test script for LOGDTW2002
Tests all major game systems
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.player import Player
from game.world import World
from game.world_generator import WorldGenerator
from game.combat import CombatSystem
from game.trading import TradingSystem
from game.quests import QuestSystem
from game.npcs import NPCSystem
from game.holodeck import HolodeckSystem
from game.stock_market import StockMarket, BankingSystem
from game.sos_system import SOSSystem
from utils.display import DisplayManager

def test_player():
    """Test player system"""
    print("Testing Player...")
    
    # Create player
    player = Player("Test Player")
    
    # Test basic attributes
    assert player.name == "Test Player"
    assert player.level == 1
    assert player.health == 100
    assert player.energy == 100
    assert player.fuel == 100
    assert player.credits == 1000
    
    # Test starting items
    assert len(player.inventory) == 6
    print("✓ Player created with 6 starting items")
    
    # Test experience system
    player.gain_experience(50)
    assert player.experience == 50
    print("✓ Experience system working")
    
    # Test item management
    assert player.add_item(player.inventory[0])
    assert len(player.inventory) == 7
    print("✓ Item management working")
    
    # Test name and ship name changes
    assert player.change_name("New Name")
    assert player.name == "New Name"
    assert player.change_ship_name("New Ship")
    assert player.ship_name == "New Ship"
    print("✓ Name and ship name changes working")
    
    # Test cargo holds
    cargo_summary = player.get_cargo_summary()
    assert len(cargo_summary['holds']) == 5
    print("✓ Cargo holds working")
    
    print("✓ Player tests passed!")

def test_world():
    """Test world system"""
    print("Testing World...")
    
    # Create world
    world = World()
    
    # Test locations
    assert len(world.locations) == 8
    print("✓ World created with 8 locations")
    
    # Test starting location
    assert world.current_location == "Earth Station"
    print("✓ Starting location correct")
    
    # Test travel
    assert world.travel_to("Mars Colony")
    assert world.current_location == "Mars Colony"
    print("✓ Travel system working")
    
    # Test market system
    assert world.can_trade()
    print("✓ Market system working")
    
    print("✓ World tests passed!")

def test_world_generator():
    """Test world generator"""
    print("Testing World Generator...")
    
    # Create world generator
    generator = WorldGenerator()
    
    # Test sector generation
    sector = generator.generate_sector((100, 100, 100))
    assert sector.name
    assert sector.coordinates == (100, 100, 100)
    print("✓ Sector generation working")
    
    # Test planet generation
    planet = generator.generate_planet(sector)
    assert planet['name']
    assert planet['type']
    print("✓ Planet generation working")
    
    print("✓ World Generator tests passed!")

def test_combat():
    """Test combat system"""
    print("Testing Combat...")
    
    # Create combat system
    combat = CombatSystem()
    
    # Test combat start
    player = Player()
    success = combat.start_combat(player, "space_pirate")
    assert success
    assert combat.in_combat
    assert combat.current_enemy is not None
    print("✓ Combat system initialized")
    
    # Test player attack
    result = combat.player_attack()
    assert result['success']
    print("✓ Combat mechanics working")
    
    print("✓ Combat tests passed!")

def test_trading():
    """Test trading system"""
    print("Testing Trading...")
    
    # Create trading system
    trading = TradingSystem()
    
    # Test market info
    market_info = trading.get_market_info("Earth Station")
    assert market_info['available']
    print("✓ Market system working")
    
    # Test trading mechanics
    player = Player()
    result = trading.buy_item(player, "Earth Station", "Computer Chips", 1)
    assert result['success'] or "not enough" in result['message'].lower()
    print("✓ Trading mechanics working")
    
    print("✓ Trading tests passed!")

def test_quests():
    """Test quest system"""
    print("Testing Quests...")
    
    # Create quest system
    quests = QuestSystem()
    
    # Test quest creation
    available_quests = quests.get_available_quests(Player())
    assert len(available_quests) > 0
    print(f"✓ Quest system created {len(available_quests)} available quests")
    
    # Test quest acceptance
    if available_quests:
        quest = available_quests[0]
        assert quests.accept_quest(Player(), quest.id)
        print("✓ Quest acceptance working")
    
    print("✓ Quest tests passed!")

def test_npcs():
    """Test NPC system"""
    print("Testing NPCs...")
    
    # Create NPC system
    npcs = NPCSystem()
    
    # Test NPC creation
    npc = npcs.create_npc("Test NPC", "trader", "Earth Station")
    assert npc.name == "Test NPC"
    assert npc.npc_type == "trader"
    print("✓ NPC creation working")
    
    # Test conversation
    player = Player()
    result = npcs.start_conversation(player, "Test NPC")
    assert result['success']
    print("✓ NPC conversation working")
    
    print("✓ NPC tests passed!")

def test_holodeck():
    """Test holodeck system"""
    print("Testing Holodeck...")
    
    # Create holodeck system
    holodeck = HolodeckSystem()
    
    # Test program listing
    programs = holodeck.get_available_programs()
    assert len(programs) > 0
    print(f"✓ Holodeck has {len(programs)} programs")
    
    # Test program start
    player = Player()
    result = holodeck.start_program(player, programs[0].name)
    assert result['success'] or "not enough" in result['message'].lower()
    print("✓ Holodeck program start working")
    
    print("✓ Holodeck tests passed!")

def test_stock_market():
    """Test stock market system"""
    print("Testing Stock Market...")
    
    # Create stock market
    market = StockMarket()
    
    # Test stock listing
    stocks = market.get_all_stocks()
    assert len(stocks) > 0
    print(f"✓ Stock market has {len(stocks)} stocks")
    
    # Test stock info
    stock = market.get_stock_info("TECH")
    assert stock.symbol == "TECH"
    print("✓ Stock information working")
    
    print("✓ Stock Market tests passed!")

def test_banking():
    """Test banking system"""
    print("Testing Banking...")
    
    # Create banking system
    banking = BankingSystem()
    
    # Test branch info
    branch_info = banking.get_branch_info("Earth Station")
    assert branch_info['available']
    print("✓ Banking branch info working")
    
    # Test account creation
    player = Player()
    result = banking.create_account(player, "savings", "Earth Station")
    assert result['success']
    print("✓ Account creation working")
    
    print("✓ Banking tests passed!")

def test_sos():
    """Test SOS system"""
    print("Testing SOS System...")
    
    # Create SOS system
    sos = SOSSystem()
    
    # Test signal generation
    signal = sos.generate_distress_signal((0, 0, 0))
    if signal:
        assert signal.ship_name
        assert signal.distress_type
        print("✓ Distress signal generation working")
    else:
        print("✓ Distress signal generation (no signal generated)")
    
    print("✓ SOS System tests passed!")

def test_display():
    """Test display system"""
    print("Testing Display...")
    
    # Create display manager
    display = DisplayManager()
    
    # Test status display
    player = Player("Test Display")
    display.show_status(player)
    print("✓ Status display working")
    
    # Test location display
    world = World()
    location = world.get_current_location()
    display.show_location(location)
    print("✓ Location display working")
    
    print("✓ Display tests passed!")

def main():
    """Run all tests"""
    print("LOGDTW2002 - Game Tests")
    print("=" * 40)
    
    try:
        test_player()
        test_world()
        test_world_generator()
        test_combat()
        test_trading()
        test_quests()
        test_npcs()
        test_holodeck()
        test_stock_market()
        test_banking()
        test_sos()
        test_display()
        
        print("\n🎉 All tests passed! The game is ready to play.")
        print("\nTo start the game, run: python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 