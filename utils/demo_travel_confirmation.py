#!/usr/bin/env python3
"""
Demo script for Travel Confirmation System
Tests the new travel estimates and confirmation prompts
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.world import World
from game.player import Player
from rich.console import Console
from rich.prompt import Confirm


def demo_travel_confirmation():
    """Demonstrate the travel confirmation system"""
    console = Console()

    console.print("[bold cyan]Travel Confirmation System Demo[/bold cyan]")
    console.print("=" * 60)
    console.print("Testing travel estimates and confirmation prompts...\n")

    # Initialize systems
    world = World()
    player = Player()

    # Show current sector
    console.print("[yellow]Current Sector:[/yellow]")
    console.print(f"  Sector: {world.current_sector}")
    console.print(f"  Location: {world.get_current_location().name}")
    console.print(f"  Fuel: {player.fuel}")
    console.print()

    # Test different sector jumps with confirmation
    test_sectors = [2, 3, 4, 5]

    for sector in test_sectors:
        console.print(f"\n[bold yellow]Testing jump to Sector {sector}:[/bold yellow]")

        if world.can_jump_to_sector(sector):
            # Find the connection details
            connection = None
            for conn in world.sector_connections[world.current_sector]:
                if conn.destination_sector == sector:
                    connection = conn
                    break

            if connection:
                # Show travel estimate
                console.print(f"\n[bold cyan]Travel Estimate to Sector {sector}:[/bold cyan]")
                console.print(f"  Connection Type: {connection.connection_type.upper()}")
                console.print(f"  Fuel Cost: {connection.fuel_cost}")
                console.print(f"  Travel Time: {connection.travel_time} minutes")
                console.print(f"  Danger Level: {connection.danger_level}/10")
                console.print(f"  Faction: {world.sector_factions.get(sector, 'Unknown')}")

                # Check fuel
                if player.fuel < connection.fuel_cost:
                    console.print(
                        f"\n[red]Insufficient fuel! Need {connection.fuel_cost}, have {player.fuel}.[/red]"
                    )
                else:
                    console.print(
                        f"\n[yellow]Are you sure you want to commit {connection.travel_time} minutes to travel to Sector {sector}?[/yellow]"
                    )

                    # Simulate user confirmation (in demo, we'll auto-confirm)
                    console.print("[green]Demo: Auto-confirming jump...[/green]")

                    # Proceed with jump
                    result = world.jump_to_sector(sector, player)
                    if result["success"]:
                        console.print(f"[green]✓ {result['message']}[/green]")

                        # Simulate travel completion
                        world._complete_jump(player)

                        console.print(
                            f"[green]Arrived at Sector {world.current_sector} ({world.get_current_location().name})[/green]"
                        )
                        console.print(f"[green]Fuel remaining: {player.fuel}[/green]")
                    else:
                        console.print(f"[red]✗ {result['message']}[/red]")
            else:
                console.print(f"[red]No connection found to Sector {sector}[/red]")
        else:
            console.print(f"[red]Cannot jump to Sector {sector} from current location[/red]")

    # Test warp command
    console.print(f"\n[bold yellow]Testing warp to Sector 3:[/bold yellow]")

    if world.can_jump_to_sector(3):
        connection = None
        for conn in world.sector_connections[world.current_sector]:
            if conn.destination_sector == 3:
                connection = conn
                break

        if connection:
            console.print(f"\n[bold cyan]Warp Estimate to Sector 3:[/bold cyan]")
            console.print(f"  Connection Type: {connection.connection_type.upper()}")
            console.print(f"  Fuel Cost: {connection.fuel_cost} (instant travel)")
            console.print(f"  Travel Time: Instant")
            console.print(f"  Danger Level: {connection.danger_level}/10")
            console.print(f"  Faction: {world.sector_factions.get(3, 'Unknown')}")

            if player.fuel < connection.fuel_cost:
                console.print(
                    f"\n[red]Insufficient fuel! Need {connection.fuel_cost}, have {player.fuel}.[/red]"
                )
            else:
                console.print(f"\n[yellow]Are you sure you want to warp to Sector 3?[/yellow]")
                console.print("[green]Demo: Auto-confirming warp...[/green]")

                # Find destination location
                destination = None
                for loc in world.locations.values():
                    if loc.sector == 3:
                        destination = loc.name
                        break

                if destination and world.instant_jump(destination):
                    console.print(f"[green]✓ Warped to Sector 3 ({destination})![/green]")
                else:
                    console.print(f"[red]✗ Cannot warp to Sector 3.[/red]")

    console.print(f"\n[bold green]Demo completed![/bold green]")
    console.print("The travel confirmation system now provides:")
    console.print("• Detailed travel estimates before jumping")
    console.print("• Fuel cost and travel time information")
    console.print("• Danger level and faction warnings")
    console.print("• User confirmation prompts")
    console.print("• Fuel sufficiency checks")


if __name__ == "__main__":
    demo_travel_confirmation()
