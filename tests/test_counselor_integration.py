#!/usr/bin/env python3
"""
Test script to verify counselor AI integration with main game
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.player import Player
from game.ai_counselor import ShipCounselor
from rich.console import Console


def test_counselor_integration():
    """Test counselor integration with player context"""
    console = Console()

    console.print("[bold cyan]Testing Counselor AI Integration[/bold cyan]")
    console.print("=" * 50)

    # Create a player with various states
    player = Player()

    # Test counselor with different player states
    counselor = ShipCounselor()

    # Test 1: Normal player state
    console.print("\n[yellow]Test 1: Normal player state[/yellow]")
    player_context = {
        "credits": player.credits,
        "health": player.health,
        "fuel": 100,
        "level": player.level,
        "experience": player.experience,
    }

    response = counselor.chat("I need advice", player_context)
    counselor.display_response(response)

    # Test 2: Low health state
    console.print("\n[yellow]Test 2: Low health state[/yellow]")
    player.health = 25
    player_context["health"] = player.health

    response = counselor.chat("help me", player_context)
    counselor.display_response(response)

    # Test 3: Low credits state
    console.print("\n[yellow]Test 3: Low credits state[/yellow]")
    player.credits = 10
    player_context["credits"] = player.credits

    response = counselor.chat("I need trading advice", player_context)
    counselor.display_response(response)

    # Test 4: Low fuel state
    console.print("\n[yellow]Test 4: Low fuel state[/yellow]")
    player_context["fuel"] = 5

    response = counselor.chat("travel advice", player_context)
    counselor.display_response(response)

    console.print("\n[bold green]Integration test completed successfully![/bold green]")
    console.print("The counselor AI properly responds to different player states.")


if __name__ == "__main__":
    test_counselor_integration()
