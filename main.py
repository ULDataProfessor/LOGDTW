#!/usr/bin/env python3
"""
LOGDTW2002 - Legend of the Green Dragon meets TW2002
A text-based adventure game combining RPG elements with space exploration
"""

import os
import sys
import time
from colorama import init, Fore, Back, Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add the game directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from game.player import Player
from game.world import World
from game.combat import CombatSystem
from game.trading import TradingSystem
from game.quests import QuestSystem
from utils.display import DisplayManager
from utils.input_handler import InputHandler

class Game:
    def __init__(self):
        self.console = Console()
        self.display = DisplayManager()
        self.input_handler = InputHandler()
        self.player = None
        self.world = None
        self.combat_system = None
        self.trading_system = None
        self.quest_system = None
        self.running = False

    def show_title_screen(self):
        """Display the game title screen with ASCII art"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        title_text = Text("LOGDTW2002", style="bold magenta")
        subtitle_text = Text("Legend of the Green Dragon meets TW2002", style="cyan")
        
        # ASCII art for the title
        ascii_art = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██╗      ██████╗ ██████╗ ██████╗ ████████╗██████╗     ║
    ║    ██║     ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔══██╗    ║
    ║    ██║     ██║     ██║   ██║██║  ██║   ██║   ██████╔╝    ║
    ║    ██║     ██║     ██║   ██║██║  ██║   ██║   ██╔══██╗    ║
    ║    ███████╗╚██████╗╚██████╔╝██████╔╝   ██║   ██║  ██║    ║
    ║    ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝    ║
    ║                                                              ║
    ║    ████████╗██████╗ ██████╗ ███████╗██████╗ ███████╗      ║
    ║    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝      ║
    ║       ██║   ██████╔╝██║  ██║█████╗  ██████╔╝███████╗      ║
    ║       ██║   ██╔══██╗██║  ██║██╔══╝  ██╔══██╗╚════██║      ║
    ║       ██║   ██║  ██║██████╔╝███████╗██║  ██║███████║      ║
    ║       ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝      ║
    ║                                                              ║
    ║              A Text-Based Adventure Game                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(ascii_art, style="cyan")
        self.console.print("\n")
        
        # Show menu options
        menu_table = Table(title="Main Menu", show_header=False, box=None)
        menu_table.add_column("Option", style="yellow")
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1", "Start New Game")
        menu_table.add_row("2", "Load Game")
        menu_table.add_row("3", "Help")
        menu_table.add_row("4", "Quit")
        
        self.console.print(menu_table)
        self.console.print("\n")

    def get_menu_choice(self):
        """Get the player's menu choice"""
        while True:
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            if choice == "1":
                return "new_game"
            elif choice == "2":
                return "load_game"
            elif choice == "3":
                return "help"
            elif choice == "4":
                return "quit"

    def show_help(self):
        """Display help information"""
        help_text = """
        [bold cyan]LOGDTW2002 - Game Controls[/bold cyan]
        
        [bold yellow]Movement:[/bold yellow]
        - north, south, east, west (or n, s, e, w)
        - up, down, in, out
        
        [bold yellow]Actions:[/bold yellow]
        - look, examine, search
        - take, drop, use, inventory
        - talk, ask, say
        
        [bold yellow]Combat:[/bold yellow]
        - attack, defend, flee
        - use [weapon/item]
        
        [bold yellow]Space Travel:[/bold yellow]
        - travel [destination]
        - land, takeoff
        - scan, navigate
        
        [bold yellow]Trading:[/bold yellow]
        - buy [item], sell [item]
        - trade, market
        
        [bold yellow]System:[/bold yellow]
        - status, stats
        - save, load, quit
        - help
        
        [bold yellow]Special Commands:[/bold yellow]
        - quests, missions
        - skills, abilities
        - equipment, ship
        """
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        input("\nPress Enter to continue...")

    def initialize_game(self):
        """Initialize the game systems"""
        self.console.print("[bold green]Initializing game systems...[/bold green]")
        
        # Initialize player
        self.player = Player()
        
        # Initialize world
        self.world = World()
        
        # Initialize systems
        self.combat_system = CombatSystem()
        self.trading_system = TradingSystem()
        self.quest_system = QuestSystem()
        
        self.console.print("[bold green]Game systems initialized successfully![/bold green]")
        time.sleep(1)

    def game_loop(self):
        """Main game loop"""
        self.running = True
        
        while self.running:
            try:
                # Display current location and status
                self.display.show_location(self.world.get_current_location())
                self.display.show_status(self.player)
                
                # Get player input
                command = self.input_handler.get_input()
                
                # Process command
                if command.lower() in ['quit', 'exit', 'q']:
                    if Confirm.ask("Are you sure you want to quit?"):
                        self.running = False
                        break
                
                elif command.lower() in ['help', 'h']:
                    self.show_help()
                
                elif command.lower() in ['status', 'stats', 's']:
                    self.display.show_detailed_status(self.player)
                
                elif command.lower() in ['inventory', 'inv', 'i']:
                    self.display.show_inventory(self.player)
                
                elif command.lower() in ['look', 'l']:
                    self.display.show_location_description(self.world.get_current_location())
                
                elif command.lower() in ['north', 'n', 'south', 's', 'east', 'e', 'west', 'w']:
                    self.handle_movement(command.lower())
                
                elif command.lower().startswith('travel'):
                    self.handle_travel(command)
                
                elif command.lower().startswith('attack'):
                    self.handle_combat(command)
                
                elif command.lower().startswith('buy') or command.lower().startswith('sell'):
                    self.handle_trading(command)
                
                elif command.lower() in ['quests', 'missions']:
                    self.display.show_quests(self.quest_system.get_available_quests())
                
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                    self.console.print("Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                if Confirm.ask("\nAre you sure you want to quit?"):
                    self.running = False
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def handle_movement(self, direction):
        """Handle player movement"""
        direction_map = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'north': 'north', 'south': 'south', 'east': 'east', 'west': 'west'
        }
        
        actual_direction = direction_map.get(direction, direction)
        success = self.world.move_player(actual_direction)
        
        if success:
            self.console.print(f"[green]You move {actual_direction}.[/green]")
        else:
            self.console.print(f"[red]You cannot go {actual_direction} from here.[/red]")

    def handle_travel(self, command):
        """Handle space travel commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: travel [destination][/red]")
            return
        
        destination = ' '.join(parts[1:])
        success = self.world.travel_to(destination)
        
        if success:
            self.console.print(f"[green]Traveling to {destination}...[/green]")
        else:
            self.console.print(f"[red]Cannot travel to {destination}.[/red]")

    def handle_combat(self, command):
        """Handle combat commands"""
        if not self.world.is_in_combat():
            self.console.print("[red]There's nothing to attack here.[/red]")
            return
        
        # Combat logic would go here
        self.console.print("[yellow]Combat system not yet implemented.[/yellow]")

    def handle_trading(self, command):
        """Handle trading commands"""
        if not self.world.can_trade():
            self.console.print("[red]No trading available here.[/red]")
            return
        
        # Trading logic would go here
        self.console.print("[yellow]Trading system not yet implemented.[/yellow]")

    def run(self):
        """Main game run method"""
        while True:
            self.show_title_screen()
            choice = self.get_menu_choice()
            
            if choice == "new_game":
                self.initialize_game()
                self.game_loop()
            elif choice == "load_game":
                self.console.print("[yellow]Load game feature not yet implemented.[/yellow]")
                input("Press Enter to continue...")
            elif choice == "help":
                self.show_help()
            elif choice == "quit":
                self.console.print("[green]Thanks for playing LOGDTW2002![/green]")
                break

def main():
    """Main entry point"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()