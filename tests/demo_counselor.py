#!/usr/bin/env python3
"""
Demo script for the Ship Counselor AI
Tests the cheeky AI assistant functionality
"""

import sys
import os

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.ai_counselor import ShipCounselor
from rich.console import Console


def demo_counselor():
    """Demonstrate the ship counselor AI functionality"""
    console = Console()

    console.print("[bold cyan]Ship Counselor AI Demo[/bold cyan]")
    console.print("=" * 50)
    console.print("Testing the cheeky AI assistant...\n")

    # Initialize the counselor
    counselor = ShipCounselor()

    # Test different types of interactions
    test_inputs = [
        "hello",
        "I need help with trading",
        "What should I do about combat?",
        "I'm low on fuel",
        "I'm broke",
        "I'm injured",
        "This is stupid",
        "What's your advice?",
        "goodbye",
    ]

    # Simulate player context
    player_context = {
        "credits": 50,  # Low credits
        "health": 30,  # Low health
        "fuel": 15,  # Low fuel
        "level": 5,
        "experience": 250,
    }

    console.print("[yellow]Starting conversation with the Counselor AI...[/yellow]\n")

    for user_input in test_inputs:
        console.print(f"[cyan]You:[/cyan] {user_input}")

        # Get counselor response
        response = counselor.chat(user_input, player_context)
        counselor.display_response(response)

        console.print()  # Empty line for spacing

    # Show conversation summary
    console.print(f"\n[bold green]Conversation Summary:[/bold green]")
    console.print(counselor.get_conversation_summary())

    console.print("\n[bold green]Demo completed![/bold green]")
    console.print("In the main game, use 'counselor' or 'ai' to chat with your ship's AI.")


if __name__ == "__main__":
    demo_counselor()
