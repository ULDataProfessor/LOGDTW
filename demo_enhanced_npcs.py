#!/usr/bin/env python3
"""
Demo script for Enhanced NPC Dialogue System
Tests the new dialogue options with secrets and hidden information
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.npcs import NPCSystem
from game.player import Player
from rich.console import Console
from rich.panel import Panel

def demo_enhanced_npcs():
    """Demonstrate the enhanced NPC dialogue system"""
    console = Console()
    
    console.print("[bold cyan]Enhanced NPC Dialogue System Demo[/bold cyan]")
    console.print("=" * 60)
    console.print("Testing the new dialogue options with secrets and hidden information...\n")
    
    # Initialize systems
    npc_system = NPCSystem()
    player = Player()
    
    # Create different types of NPCs
    npc_types = ['trader', 'scientist', 'pirate', 'official', 'entertainer', 'mystic']
    
    for npc_type in npc_types:
        console.print(f"\n[bold yellow]{npc_type.upper()} NPC[/bold yellow]")
        console.print("-" * 40)
        
        # Create NPC
        npc = npc_system.create_npc(f"Test {npc_type.title()}", npc_type, "Test Station")
        
        # Start conversation
        conversation = npc_system.start_conversation(player, npc.name)
        if conversation['success']:
            console.print(f"[green]{npc.name}:[/green] {conversation['greeting']}")
            
            # Get conversation options
            options = npc_system.get_conversation_options(npc)
            console.print(f"\n[cyan]Available options:[/cyan] {', '.join(options)}")
            
            # Test different dialogue options
            test_options = ['Ask about rumors', 'Ask about secrets']
            if npc_type == 'trader':
                test_options.append('Ask about trade secrets')
            elif npc_type == 'scientist':
                test_options.append('Ask about classified data')
            elif npc_type == 'entertainer':
                test_options.append('Ask for stories')
            elif npc_type == 'official':
                test_options.append('Ask about classified information')
            elif npc_type == 'pirate':
                test_options.append('Ask about dangerous information')
            elif npc_type == 'mystic':
                test_options.append('Seek prophecy')
                test_options.append('Ask about the void')
            
            for option in test_options:
                if option in options:
                    result = npc_system.handle_conversation_choice(player, npc, option)
                    console.print(f"\n[blue]You:[/blue] {option}")
                    console.print(f"[green]{npc.name}:[/green] {result['message']}")
            
            # End conversation
            end_result = npc_system.handle_conversation_choice(player, npc, 'End conversation')
            console.print(f"\n[green]{npc.name}:[/green] {end_result['message']}")
        
        console.print()  # Empty line for spacing
    
    console.print("\n[bold green]Demo completed![/bold green]")
    console.print("The enhanced NPC system now provides:")
    console.print("• Rich dialogue with secrets and hidden information")
    console.print("• Context-specific rumors and classified data")
    console.print("• Mystical prophecies and void knowledge")
    console.print("• Trade secrets and dangerous information")
    console.print("• Stories based on real events")

if __name__ == "__main__":
    demo_enhanced_npcs() 