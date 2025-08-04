#!/usr/bin/env python3
"""
Demo script for LOGDTW2002 Sector Navigation System
Shows the new sector jumping navigation instead of directional movement
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.player import Player
from game.world import World
from utils.display import DisplayManager

def demo_sector_navigation():
    """Demonstrate the new sector jumping navigation system"""
    print("\n" + "="*60)
    print("SECTOR NAVIGATION SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Initialize systems
    player = Player("Demo Navigator")
    world = World()
    display = DisplayManager()
    
    # Show starting location
    print(f"\nStarting Location: {world.current_location}")
    print(f"Starting Sector: {world.get_current_location().sector}")
    print(f"Player Fuel: {player.fuel}")
    
    # Show available jumps
    print("\n" + "-"*40)
    print("AVAILABLE SECTOR JUMPS")
    print("-"*40)
    available_jumps = world.get_available_jumps()
    for jump in available_jumps:
        jump_info = world.get_jump_info(jump)
        print(f"\n{jump}:")
        print(f"  Sector: {jump_info['sector']}")
        print(f"  Fuel Cost: {jump_info['fuel_cost']}")
        print(f"  Jump Time: {jump_info['travel_time']} minutes")
        print(f"  Danger Level: {jump_info['danger_level']}/10")
        print(f"  Faction: {jump_info['faction']}")
    
    # Show galactic map
    print("\n" + "-"*40)
    print("GALACTIC MAP")
    print("-"*40)
    print(world.get_map_display())
    
    # Demonstrate sector jumping
    print("\n" + "-"*40)
    print("DEMONSTRATING SECTOR JUMPING")
    print("-"*40)
    
    # Jump to Mars Colony
    print("Jumping to Mars Colony...")
    result = world.jump_to_sector("Mars Colony", player)
    print(f"Jump Result: {result['message']}")
    
    # Show new location
    print(f"\nNew Location: {world.current_location}")
    print(f"New Sector: {world.get_current_location().sector}")
    print(f"Remaining Fuel: {player.fuel}")
    
    # Show discovered sectors
    print(f"\nDiscovered Sectors: {', '.join(world.get_discovered_sectors())}")
    
    # Demonstrate instant warp
    print("\n" + "-"*40)
    print("DEMONSTRATING INSTANT WARP")
    print("-"*40)
    
    print("Warping to Luna Base...")
    if world.instant_jump("Luna Base"):
        print("✓ Successfully warped to Luna Base!")
        print(f"Current Location: {world.current_location}")
        print(f"Current Sector: {world.get_current_location().sector}")
    else:
        print("✗ Warp failed!")
    
    # Show sector information
    print("\n" + "-"*40)
    print("SECTOR INFORMATION")
    print("-"*40)
    
    all_sectors = world.get_all_sectors()
    discovered_sectors = world.get_discovered_sectors()
    
    print("All Sectors:")
    for sector in all_sectors:
        if sector in discovered_sectors:
            print(f"  [green]✓ {sector}[/green]")
        else:
            print(f"  [dim]? {sector} (Undiscovered)[/dim]")
    
    print(f"\nDiscovered Sectors: {', '.join(discovered_sectors)}")

def demo_navigation_commands():
    """Show the new navigation commands"""
    print("\n" + "="*60)
    print("NEW NAVIGATION COMMANDS")
    print("="*60)
    
    commands = [
        ("jump [destination]", "Jump to a connected sector"),
        ("warp [destination]", "Instant jump to a connected sector"),
        ("map", "Show galactic map with sectors"),
        ("sectors", "Show all sectors and their status"),
        ("sector", "Show current sector information"),
        ("north/south/east/west", "Jump in a direction (if sectors available)"),
        ("look", "Examine current location"),
        ("status", "Show player status")
    ]
    
    print("\nAvailable Navigation Commands:")
    for command, description in commands:
        print(f"  • {command:<25} - {description}")
    
    print("\nKey Features:")
    print("  • Sector-based navigation instead of directional movement")
    print("  • Discover new sectors as you explore")
    print("  • Fuel costs for jumps between sectors")
    print("  • Different sectors have different danger levels")
    print("  • Each sector has unique locations and factions")
    print("  • Visual map shows sector connections")

def main():
    """Run the sector navigation demo"""
    print("\n" + "="*60)
    print("LOGDTW2002 - SECTOR NAVIGATION DEMO")
    print("="*60)
    
    print("\nThis demonstration shows the new sector jumping navigation system:")
    print("• Sector-based navigation instead of directional movement")
    print("• Jump between connected sectors on the galactic map")
    print("• Discover new sectors as you explore")
    print("• Fuel costs and travel times for jumps")
    print("• Visual galactic map with sector connections")
    
    # Run demonstrations
    demo_sector_navigation()
    demo_navigation_commands()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nTo play the full game with sector navigation, run: python main.py")
    print("\nThe game now features:")
    print("• Sector-based navigation system")
    print("• Galactic map with visual connections")
    print("• Sector discovery and exploration")
    print("• Fuel-based jump costs")
    print("• Multiple sectors with unique characteristics")

if __name__ == "__main__":
    main() 