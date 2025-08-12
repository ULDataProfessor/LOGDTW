#!/usr/bin/env python3
"""
Demo script for TW2002-style Navigation System
Tests the new numbered sectors with connection types
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.world import World
from game.player import Player
from utils.display import DisplayManager
from rich.console import Console


def demo_tw2002_navigation():
    """Demonstrate the TW2002-style navigation system"""
    console = Console()

    console.print("[bold cyan]TW2002 Navigation System Demo[/bold cyan]")
    console.print("=" * 60)
    console.print("Testing numbered sectors with connection types...\n")

    # Initialize systems
    world = World()
    player = Player()
    display = DisplayManager()

    # Show initial sector display
    console.print("[yellow]Initial Sector Display:[/yellow]")
    display.show_tw2002_sector_display(world)

    # Test jumping to different sectors
    test_jumps = [2, 3, 4, 5, 6, 7, 8]

    for sector in test_jumps:
        console.print(f"\n[yellow]Attempting to jump to Sector {sector}:[/yellow]")

        if world.can_jump_to_sector(sector):
            result = world.jump_to_sector(sector, player)
            if result["success"]:
                console.print(f"[green]✓ Successfully jumped to Sector {sector}[/green]")
                console.print(f"[green]  {result['message']}[/green]")

                # Simulate travel completion
                world._complete_jump(player)

                # Show the new sector display
                display.show_tw2002_sector_display(world)
            else:
                console.print(
                    f"[red]✗ Failed to jump to Sector {sector}: {result['message']}[/red]"
                )
        else:
            console.print(f"[red]✗ Cannot jump to Sector {sector} from current location[/red]")

    # Show all available jumps from current sector
    console.print(f"\n[yellow]All available jumps from Sector {world.current_sector}:[/yellow]")
    available_jumps = world.get_available_jumps()

    if available_jumps:
        for jump in available_jumps:
            console.print(
                f"  • Sector {jump['sector']} ({jump['type'].upper()}) - {jump['faction']}"
            )
            console.print(
                f"    Fuel: {jump['fuel_cost']}, Time: {jump['travel_time']}min, Danger: {jump['danger_level']}/10"
            )
    else:
        console.print("  No available jumps")

    # Show sector information
    console.print(f"\n[yellow]Current Sector Information:[/yellow]")
    sector_info = world.get_sector_info()
    if "sector" in sector_info:
        console.print(f"  Sector: {sector_info['sector']}")
        console.print(f"  Locations: {', '.join(sector_info['locations'])}")
        console.print(f"  Faction: {sector_info['faction']}")
        console.print(f"  Danger Level: {sector_info['danger_level']}/10")
        console.print(f"  Discovered: {sector_info['discovered']}")
    else:
        console.print("  Sector information not available")

    console.print(f"\n[bold green]Demo completed![/bold green]")
    console.print("The TW2002 navigation system now provides:")
    console.print("• Numbered sectors (1-8)")
    console.print("• Connection types: Federation, Neutral, Enemy, Hop, Skip, Warp")
    console.print("• Visual indicators for each connection type")
    console.print("• Fuel costs and travel times for each connection")
    console.print("• Faction control information")


if __name__ == "__main__":
    demo_tw2002_navigation()
