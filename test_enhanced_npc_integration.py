#!/usr/bin/env python3
"""
Test script to verify enhanced NPC system integration with main game
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.player import Player
from game.npcs import NPCSystem
from game.world import World
from rich.console import Console

def test_enhanced_npc_integration():
    """Test enhanced NPC integration with main game systems"""
    console = Console()
    
    console.print("[bold cyan]Testing Enhanced NPC System Integration[/bold cyan]")
    console.print("=" * 60)
    
    # Initialize game systems
    player = Player()
    world = World()
    npc_system = NPCSystem()
    
    # Test NPC generation at different locations
    test_locations = ["Alpha Centauri", "Beta Station", "Gamma Outpost"]
    
    for location in test_locations:
        console.print(f"\n[yellow]Testing NPCs at {location}:[/yellow]")
        
        # Generate NPCs for the location
        npcs = npc_system.generate_random_npcs(location, 4)
        
        for npc in npcs:
            console.print(f"  • {npc.name} ({npc.npc_type}) - {npc.personality}")
            
            # Test conversation options
            options = npc_system.get_conversation_options(npc)
            console.print(f"    Options: {', '.join(options[:3])}...")
            
            # Test a few dialogue options
            test_options = ['Ask about rumors', 'Ask about secrets']
            if 'Ask about secrets' in options:
                test_options.append('Ask about secrets')
            
            for option in test_options:
                if option in options:
                    result = npc_system.handle_conversation_choice(player, npc, option)
                    console.print(f"    {option}: {result['message'][:50]}...")
    
    # Test specific NPC types
    console.print(f"\n[yellow]Testing specific NPC types:[/yellow]")
    
    special_npcs = [
        ('Mystic Oracle', 'mystic', 'Mystic Temple'),
        ('Classified Scientist', 'scientist', 'Research Lab'),
        ('Underworld Trader', 'trader', 'Smuggler\'s Den'),
        ('Corrupt Official', 'official', 'Government Station'),
        ('Ruthless Pirate', 'pirate', 'Pirate Haven'),
        ('Famous Entertainer', 'entertainer', 'Entertainment District')
    ]
    
    for name, npc_type, location in special_npcs:
        npc = npc_system.create_npc(name, npc_type, location)
        console.print(f"  • {npc.name} ({npc_type})")
        
        # Test secrets dialogue
        if 'secrets' in npc.dialogue:
            secret = npc.dialogue['secrets'][0]
            console.print(f"    Secret: {secret[:60]}...")
        
        # Test rumors dialogue
        if 'rumors' in npc.dialogue:
            rumor = npc.dialogue['rumors'][0]
            console.print(f"    Rumor: {rumor[:60]}...")
    
    console.print(f"\n[bold green]Integration test completed successfully![/bold green]")
    console.print("The enhanced NPC system provides:")
    console.print("• Rich dialogue with game world secrets")
    console.print("• Context-specific information about sectors and events")
    console.print("• Mystical prophecies and classified data")
    console.print("• Trade secrets and dangerous information")
    console.print("• Stories that reveal hidden game lore")

if __name__ == "__main__":
    test_enhanced_npc_integration() 