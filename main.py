#!/usr/bin/env python3
"""
LOGDTW2002 - Legend of the Green Dragon meets TW2002
A text-based adventure game combining RPG elements with space exploration
"""

import os
import sys
import time
import random
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
from game.world_generator import WorldGenerator
from game.combat import CombatSystem
from game.trading import TradingSystem
from game.quests import QuestSystem
from game.npcs import NPCSystem
from game.holodeck import HolodeckSystem
from game.stock_market import StockMarket, BankingSystem
from game.sos_system import SOSSystem
from game.skills import Skill
from game.ai_counselor import ShipCounselor
from utils.display import DisplayManager
from utils.input_handler import InputHandler

class Game:
    def __init__(self):
        self.console = Console()
        self.display = DisplayManager()
        self.input_handler = InputHandler()
        self.player = None
        self.world = None
        self.world_generator = None
        self.combat_system = None
        self.trading_system = None
        self.quest_system = None
        self.npc_system = None
        self.holodeck_system = None
        self.stock_market = None
        self.banking_system = None
        self.sos_system = None
        self.running = False

    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_title_screen(self):
        """Display the game title screen with ASCII art"""
        self.clear_screen()
        
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
        
        [bold yellow]Basic Commands:[/bold yellow]
        - ? (show quick command list)
        - help (show detailed help)
        - status, stats (show player status)
        - inventory, inv (show inventory)
        - look, l (examine current location)
        
        [bold yellow]Sector Navigation:[/bold yellow]
        - jump [destination] (jump to connected sector)
        - warp [destination] (instant jump)
        - map (show galactic map)
        - sectors (show all sectors)
        - sector (show current sector info)
        - north, south, east, west (jump in direction)
        
        [bold yellow]Trading & Economy:[/bold yellow]
        - buy [item] [quantity], sell [item] [quantity]
        - market (show market info)
        - trade routes (show best routes)
        - trade history (show recent trades)
        - stocks (show stock market)
        - bank (access banking services)
        
        [bold yellow]NPCs & Social:[/bold yellow]
        - talk [npc_name] (start conversation)
        - npcs (list available NPCs)
        - chat [npc_name] (interact with NPC)
        
        [bold yellow]Entertainment:[/bold yellow]
        - holodeck (access holodeck)
        - programs (list holodeck programs)
        - start [program] (start holodeck program)
        
        [bold yellow]Rescue & Missions:[/bold yellow]
        - sos (show distress signals)
        - rescue [signal_id] (attempt rescue)
        - missions (show available missions)
        
        [bold yellow]Ship & Equipment:[/bold yellow]
        - ship (show ship status)
        - cargo (show cargo holds)
        - equip [item] (equip item)
        - unequip [slot] (unequip item)
        
        [bold yellow]Character:[/bold yellow]
        - rename [new_name] (change player name)
        - shipname [new_name] (change ship name)
        - skills (show skill levels)
        
        [bold yellow]AI Assistant:[/bold yellow]
        - counselor, ai (chat with ship's AI counselor)
        
        [bold yellow]System:[/bold yellow]
        - save, load, quit
        - clear (clear screen)
        """
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        input("\nPress Enter to continue...")

    def show_quick_help(self):
        """Show quick command list"""
        quick_help = """
[bold cyan]Quick Commands:[/bold cyan]
? - This help    status - Player stats    inv - Inventory
map - Show map   jump - Sector jumping   market - Trading
talk - NPCs      holodeck - Entertainment sos - Rescue missions
stocks - Market  bank - Banking          ship - Ship status
cargo - Cargo    skills - Skills         counselor - AI chat
sectors - All sectors  sector - Current sector
        """
        self.console.print(Panel(quick_help, title="Quick Help", border_style="green"))

    def initialize_game(self):
        """Initialize the game systems"""
        self.console.print("[bold green]Initializing game systems...[/bold green]")
        
        # Initialize player
        self.player = Player()
        
        # Initialize world and generator
        self.world = World()
        self.world_generator = WorldGenerator()
        
        # Initialize systems
        self.combat_system = CombatSystem()
        self.trading_system = TradingSystem()
        self.quest_system = QuestSystem()
        self.npc_system = NPCSystem()
        self.holodeck_system = HolodeckSystem()
        self.stock_market = StockMarket()
        self.banking_system = BankingSystem()
        self.sos_system = SOSSystem()
        self.counselor = ShipCounselor()
        
        # Generate NPCs for current location
        current_location = self.world.get_current_location().name
        self.npc_system.generate_random_npcs(current_location, 3)
        
        self.console.print("[bold green]Game systems initialized successfully![/bold green]")
        time.sleep(1)

    def game_loop(self):
        """Main game loop"""
        self.running = True
        
        while self.running:
            try:
                # Check if traveling
                if self.world.is_traveling:
                    travel_status = self.world.update_jump(self.player)
                    if travel_status.get('arrived'):
                        self.console.print(f"[green]{travel_status['message']}[/green]")
                        self.display.show_location(self.world.get_current_location())
                    else:
                        self.console.print(f"[yellow]Jumping to {travel_status['destination']}... {travel_status['progress']:.1f}% complete[/yellow]")
                        time.sleep(1)
                        continue
                
                # Check if on a planet surface
                if self.world.is_on_planet_surface():
                    self.display.show_planet_surface(self.world)
                    self.display.show_planet_surface_instructions(self.world)
                    command = self.input_handler.get_input()
                    if command.lower() in ['quit', 'exit', 'q']:
                        if Confirm.ask("Are you sure you want to quit?"):
                            self.running = False
                            break
                    elif command.lower() in ['leave', 'orbit']:
                        result = self.world.leave_planet_surface()
                        self.console.print(result['message'])
                    elif command.lower() in ['n', 'north', 's', 'south', 'e', 'east', 'w', 'west']:
                        dir_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
                        direction = dir_map.get(command.lower(), command.lower())
                        moved = self.world.move_on_surface(direction)
                        if not moved:
                            self.console.print(f"[red]You can't move {direction} from here.[/red]")
                    else:
                        self.console.print("[yellow]Available commands: n/s/e/w to move, leave/orbit to return to space.[/yellow]")
                    continue
                
                # Check if in holodeck
                holodeck_status = self.holodeck_system.update_program(self.player)
                if holodeck_status.get('active'):
                    self.console.print(f"[cyan]Holodeck: {holodeck_status['program'].name} - {holodeck_status['progress']:.1f}% complete[/cyan]")
                    time.sleep(1)
                    continue
                elif holodeck_status.get('completed'):
                    self.console.print(f"[green]{holodeck_status['message']}[/green]")
                
                # Update systems
                self.stock_market.update_market()
                self.banking_system.update_interest()
                self.sos_system.update_signals()
                
                # Generate random events
                self._check_random_events()
                
                # Display current location and status
                self.display.show_location(self.world.get_current_location())
                self.display.show_status(self.player)
                self.display.show_adjacent_sectors(self.world)
                self.display.show_space_instructions(self.world)
                
                # Get player input
                command = self.input_handler.get_input()
                
                # Process command
                if command.lower() in ['quit', 'exit', 'q']:
                    if Confirm.ask("Are you sure you want to quit?"):
                        self.running = False
                        break
                
                elif command.lower() in ['help', 'h']:
                    self.show_help()
                
                elif command.lower() == '?':
                    self.show_quick_help()
                
                elif command.lower() in ['status', 'stats', 's']:
                    self.display.show_detailed_status(self.player)
                
                elif command.lower() in ['inventory', 'inv', 'i']:
                    self.display.show_inventory(self.player)
                
                elif command.lower() in ['look', 'l']:
                    self.display.show_location_description(self.world.get_current_location())
                
                elif command.lower() in ['north', 'n', 'south', 's', 'east', 'e', 'west', 'w']:
                    self.handle_movement(command.lower())
                
                elif command.lower() == 'land':
                    result = self.world.land_on_planet()
                    self.console.print(result['message'])
                
                elif command.lower().startswith('jump'):
                    self.handle_travel(command)
                
                elif command.lower() == 'map':
                    self.console.print(self.world.get_map_display())
                
                elif command.lower() == 'sectors':
                    self.show_sectors()
                
                elif command.lower() == 'sector':
                    self.show_current_sector()
                
                elif command.lower().startswith('warp'):
                    self.handle_warp(command)
                
                elif command.lower().startswith('buy') or command.lower().startswith('sell'):
                    self.handle_trading(command)
                
                elif command.lower() == 'market':
                    self.show_market_info()
                
                elif command.lower() == 'trade routes':
                    self.show_trade_routes()
                
                elif command.lower() == 'trade history':
                    self.show_trade_history()
                
                elif command.lower().startswith('talk') or command.lower().startswith('chat'):
                    self.handle_npc_interaction(command)
                
                elif command.lower() == 'npcs':
                    self.show_npcs()
                
                elif command.lower() == 'holodeck':
                    self.show_holodeck()
                
                elif command.lower() == 'programs':
                    self.show_holodeck_programs()
                
                elif command.lower().startswith('start'):
                    self.handle_holodeck_program(command)
                
                elif command.lower() == 'stocks':
                    self.show_stock_market()
                
                elif command.lower() == 'bank':
                    self.show_banking()
                
                elif command.lower() == 'sos':
                    self.show_sos_signals()
                
                elif command.lower().startswith('rescue'):
                    self.handle_rescue(command)
                
                elif command.lower() == 'ship':
                    self.show_ship_status()
                
                elif command.lower() == 'cargo':
                    self.show_cargo()
                
                elif command.lower().startswith('equip'):
                    self.handle_equipment(command)
                
                elif command.lower().startswith('rename'):
                    self.handle_rename(command)
                
                elif command.lower().startswith('shipname'):
                    self.handle_ship_rename(command)
                
                elif command.lower() == 'skills':
                    self.show_skills()
                
                elif command.lower() == 'clear':
                    self.clear_screen()
                
                elif command.lower().startswith('attack'):
                    self.handle_combat(command)
                
                elif command.lower() in ['quests', 'missions']:
                    self.display.show_quests(self.quest_system.get_available_quests(self.player))
                
                elif command.lower() in ['genesis', 'fire genesis']:
                    if self.world.is_on_planet_surface():
                        self.console.print("[red]You must be in space to use the Genesis Torpedo.[/red]")
                    else:
                        result = self.world.fire_genesis_torpedo(self.player)
                        self.console.print(result['message'])
                        if result.get('success'):
                            self.console.print(f"[green]You can now 'jump {result['planet']}' or 'land' to visit the new planet![/green]")
                
                elif command.lower() in ['counselor', 'ai']:
                    self.handle_counselor_interaction()
                
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                    self.console.print("Type '?' for quick help or 'help' for full help.")
                
            except KeyboardInterrupt:
                if Confirm.ask("\nAre you sure you want to quit?"):
                    self.running = False
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _check_random_events(self):
        """Check for random events"""
        # Generate distress signals
        if random.random() < 0.05:  # 5% chance
            signal = self.sos_system.generate_distress_signal(self.player.coordinates)
            if signal:
                self.console.print(f"[red]DISTRESS SIGNAL DETECTED: {signal.ship_name} needs help![/red]")
                self.console.print(f"[yellow]Type 'sos' to view distress signals[/yellow]")

    def _show_warp_ports(self):
        """Show available sector jumps"""
        current_location = self.world.get_current_location()
        if current_location and hasattr(current_location, 'connections'):
            if current_location.connections:
                jumps_text = "Available sector jumps: "
                for i, jump in enumerate(current_location.connections):
                    if i > 0:
                        jumps_text += ", "
                    jumps_text += f"[{jump}]"
                self.console.print(f"[cyan]{jumps_text}[/cyan]")

    def handle_movement(self, direction):
        """Handle player movement (now sector jumping)"""
        # Convert old directional commands to sector jumping
        current_location = self.world.get_current_location()
        if not current_location or not current_location.connections:
            self.console.print("[red]No connected sectors available for jumping.[/red]")
            return
        
        # Map directions to available jumps (if any)
        jump_map = {
            'north': current_location.connections[0] if current_location.connections else None,
            'south': current_location.connections[1] if len(current_location.connections) > 1 else None,
            'east': current_location.connections[0] if current_location.connections else None,
            'west': current_location.connections[1] if len(current_location.connections) > 1 else None,
            'n': current_location.connections[0] if current_location.connections else None,
            's': current_location.connections[1] if len(current_location.connections) > 1 else None,
            'e': current_location.connections[0] if current_location.connections else None,
            'w': current_location.connections[1] if len(current_location.connections) > 1 else None,
        }
        
        destination = jump_map.get(direction)
        if destination:
            self.handle_sector_jump(destination)
        else:
            self.console.print(f"[red]No sector available in that direction. Use 'jump [sector_name]' to jump to a specific sector.[/red]")

    def handle_sector_jump(self, destination: str):
        """Handle jumping to a specific sector"""
        jump_info = self.world.get_jump_info(destination)
        if not jump_info['available']:
            self.console.print(f"[red]Cannot jump to {destination}.[/red]")
            return
        
        # Show jump information
        self.console.print(f"[cyan]Jump Information:[/cyan]")
        self.console.print(f"Destination: {destination}")
        self.console.print(f"Sector: {jump_info['sector']}")
        self.console.print(f"Fuel Cost: {jump_info['fuel_cost']}")
        self.console.print(f"Jump Time: {jump_info['travel_time']} minutes")
        self.console.print(f"Danger Level: {jump_info['danger_level']}/10")
        self.console.print(f"Faction: {jump_info['faction']}")
        
        if Confirm.ask("Do you want to jump there?"):
            result = self.world.jump_to_sector(destination, self.player)
            if result['success']:
                self.console.print(f"[green]{result['message']}[/green]")
            else:
                self.console.print(f"[red]{result['message']}[/red]")

    def handle_travel(self, command):
        """Handle travel commands (now sector jumping)"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: jump [destination][/red]")
            return
        
        destination = ' '.join(parts[1:])
        self.handle_sector_jump(destination)

    def handle_warp(self, command):
        """Handle warp commands (instant sector jumping)"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: warp [destination][/red]")
            return
        
        destination = ' '.join(parts[1:])
        
        # Instant jump (warp)
        if self.world.instant_jump(destination):
            self.console.print(f"[green]Warped to {destination}![/green]")
        else:
            self.console.print(f"[red]Cannot warp to {destination}.[/red]")

    def handle_trading(self, command):
        """Handle trading commands"""
        if not self.world.can_trade():
            self.console.print("[red]No trading available here.[/red]")
            return
        
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: buy/sell [item] [quantity][/red]")
            return
        
        action = parts[0].lower()
        item_name = parts[1]
        quantity = int(parts[2]) if len(parts) > 2 else 1
        
        current_location = self.world.get_current_location().name
        
        if action == 'buy':
            result = self.trading_system.buy_item(self.player, current_location, item_name, quantity)
        elif action == 'sell':
            result = self.trading_system.sell_item(self.player, current_location, item_name, quantity)
        else:
            self.console.print("[red]Invalid trading command.[/red]")
            return
        
        if result['success']:
            self.console.print(f"[green]{result['message']}[/green]")
        else:
            self.console.print(f"[red]{result['message']}[/red]")

    def show_market_info(self):
        """Show market information"""
        current_location = self.world.get_current_location().name
        market_info = self.trading_system.get_market_info(current_location)
        
        if market_info['available']:
            self.display.show_market_info(market_info)
        else:
            self.console.print("[red]No market available here.[/red]")

    def show_trade_routes(self):
        """Show best trade routes"""
        routes = self.trading_system.get_best_trade_routes(self.player)
        
        if not routes:
            self.console.print("[yellow]No profitable trade routes found.[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Best Trade Routes[/bold cyan]")
        self.console.print("=" * 50)
        
        for i, route in enumerate(routes, 1):
            self.console.print(f"\n[bold yellow]{i}. {route['item']}[/bold yellow]")
            self.console.print(f"   Buy at {route['buy_location']}: {route['buy_price']} credits")
            self.console.print(f"   Sell at {route['sell_location']}: {route['sell_price']} credits")
            self.console.print(f"   Profit: {route['profit']} credits ({route['profit_margin']:.1f}%)")

    def show_trade_history(self):
        """Show trade history"""
        history = self.trading_system.get_trade_history()
        
        if not history:
            self.console.print("[yellow]No trade history available.[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Recent Trade History[/bold cyan]")
        self.console.print("=" * 50)
        
        for trade in history:
            action = "Bought" if trade['type'] == 'buy' else "Sold"
            self.console.print(f"{action} {trade['quantity']} {trade['item']} at {trade['location']} for {trade['amount']} credits")

    def handle_npc_interaction(self, command):
        """Handle NPC interactions"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: talk/chat [npc_name][/red]")
            return
        
        npc_name = ' '.join(parts[1:])
        result = self.npc_system.start_conversation(self.player, npc_name)
        
        if result['success']:
            self.console.print(f"[cyan]{npc_name}: {result['greeting']}[/cyan]")
            self._handle_conversation(npc_name)
        else:
            self.console.print(f"[red]{result['message']}[/red]")

    def _handle_conversation(self, npc_name):
        """Handle ongoing conversation with NPC"""
        npc = self.npc_system.npcs[npc_name]
        options = self.npc_system.get_conversation_options(npc)
        
        self.console.print("\n[bold yellow]Conversation Options:[/bold yellow]")
        for i, option in enumerate(options, 1):
            self.console.print(f"{i}. {option}")
        
        while True:
            try:
                choice = Prompt.ask("Choose an option", choices=[str(i) for i in range(1, len(options) + 1)])
                choice_index = int(choice) - 1
                selected_option = options[choice_index]
                
                result = self.npc_system.handle_conversation_choice(self.player, npc, selected_option)
                self.console.print(f"[cyan]{result['message']}[/cyan]")
                
                if result.get('end_conversation'):
                    break
                    
            except (ValueError, IndexError):
                self.console.print("[red]Invalid choice.[/red]")

    def show_npcs(self):
        """Show available NPCs"""
        current_location = self.world.get_current_location().name
        npcs = self.npc_system.get_npcs_at_location(current_location)
        
        if not npcs:
            self.console.print("[yellow]No NPCs available here.[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Available NPCs:[/bold cyan]")
        for npc in npcs:
            self.console.print(f"• {npc.name} ({npc.npc_type}) - {npc.personality}")

    def show_holodeck(self):
        """Show holodeck interface"""
        self.console.print("\n[bold cyan]Holodeck Interface[/bold cyan]")
        self.console.print("=" * 30)
        self.console.print("Available commands:")
        self.console.print("• programs - List available programs")
        self.console.print("• start [program] - Start a program")
        self.console.print("• end - End current program")

    def show_holodeck_programs(self):
        """Show available holodeck programs"""
        programs = self.holodeck_system.get_available_programs()
        
        self.console.print("\n[bold cyan]Available Holodeck Programs[/bold cyan]")
        self.console.print("=" * 50)
        
        for program in programs:
            self.console.print(f"\n[bold yellow]{program.name}[/bold yellow]")
            self.console.print(f"   {program.description}")
            self.console.print(f"   Cost: {program.cost} credits")
            self.console.print(f"   Duration: {program.duration} minutes")
            self.console.print(f"   Difficulty: {program.difficulty}/10")

    def handle_holodeck_program(self, command):
        """Handle holodeck program commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: start [program_name][/red]")
            return
        
        program_name = ' '.join(parts[1:])
        result = self.holodeck_system.start_program(self.player, program_name)
        
        if result['success']:
            self.console.print(f"[green]{result['message']}[/green]")
        else:
            self.console.print(f"[red]{result['message']}[/red]")

    def show_stock_market(self):
        """Show stock market interface"""
        stocks = self.stock_market.get_all_stocks()
        
        self.console.print("\n[bold cyan]Galactic Stock Market[/bold cyan]")
        self.console.print("=" * 40)
        
        for stock in stocks:
            self.console.print(f"\n[bold yellow]{stock.symbol}[/bold yellow] - {stock.name}")
            self.console.print(f"   Price: {stock.current_price:.2f} credits")
            self.console.print(f"   Sector: {stock.sector}")
            self.console.print(f"   Dividend: {stock.dividend_yield}%")

    def show_banking(self):
        """Show banking interface"""
        self.console.print("\n[bold cyan]Banking Services[/bold cyan]")
        self.console.print("=" * 30)
        self.console.print("Available commands:")
        self.console.print("• create account [type] - Create new account")
        self.console.print("• deposit [amount] - Deposit credits")
        self.console.print("• withdraw [amount] - Withdraw credits")
        self.console.print("• accounts - List your accounts")

    def show_sos_signals(self):
        """Show active SOS signals"""
        signals = self.sos_system.get_active_signals()
        
        if not signals:
            self.console.print("[yellow]No active distress signals.[/yellow]")
            return
        
        self.console.print("\n[bold red]Active Distress Signals[/bold red]")
        self.console.print("=" * 50)
        
        for signal_id, signal in signals.items():
            self.console.print(f"\n[bold yellow]{signal_id}[/bold yellow] - {signal.ship_name}")
            self.console.print(f"   Type: {signal.ship_type}")
            self.console.print(f"   Emergency: {signal.distress_type}")
            self.console.print(f"   Severity: {signal.severity}/10")
            self.console.print(f"   Reward: {signal.reward} credits")
            self.console.print(f"   {signal.description}")

    def handle_rescue(self, command):
        """Handle rescue commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: rescue [signal_id][/red]")
            return
        
        signal_id = parts[1]
        result = self.sos_system.attempt_rescue(self.player, signal_id)
        
        if result['success']:
            self.console.print(f"[green]{result['message']}[/green]")
            self.console.print(f"[yellow]Reward: {result['reward']} credits[/yellow]")
            self.console.print(f"[yellow]Experience: +{result['experience']}[/yellow]")
        else:
            self.console.print(f"[red]{result['message']}[/red]")

    def show_ship_status(self):
        """Show ship status"""
        ship = self.player.ship
        
        self.console.print("\n[bold cyan]Ship Status[/bold cyan]")
        self.console.print("=" * 30)
        self.console.print(f"Name: {ship['name']}")
        self.console.print(f"Class: {ship['class']}")
        self.console.print(f"Cargo Capacity: {ship['cargo_capacity']}")
        self.console.print(f"Fuel Efficiency: {ship['fuel_efficiency']}")
        self.console.print(f"Shield Capacity: {ship['shield_capacity']}")
        self.console.print(f"Weapon Systems: {ship['weapon_systems']}")
        self.console.print(f"Engine Power: {ship['engine_power']}")

    def show_cargo(self):
        """Show cargo holds"""
        cargo_summary = self.player.get_cargo_summary()
        
        self.console.print("\n[bold cyan]Cargo Holds[/bold cyan]")
        self.console.print("=" * 30)
        
        for hold in cargo_summary['holds']:
            self.console.print(f"\n[bold yellow]{hold['name']}[/bold yellow]")
            self.console.print(f"   Used: {hold['used']}/{hold['capacity']}")
            self.console.print(f"   Value: {hold['value']} credits")
            
            if hold['items']:
                for item in hold['items']:
                    self.console.print(f"     • {item.name} ({item.value} credits)")

    def handle_equipment(self, command):
        """Handle equipment commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: equip [item_name][/red]")
            return
        
        item_name = ' '.join(parts[1:])
        success = self.player.equip_item(item_name)
        
        if success:
            self.console.print(f"[green]Equipped {item_name}.[/green]")
        else:
            self.console.print(f"[red]Could not equip {item_name}.[/red]")

    def handle_rename(self, command):
        """Handle player rename"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: rename [new_name][/red]")
            return
        
        new_name = ' '.join(parts[1:])
        if self.player.change_name(new_name):
            self.console.print(f"[green]Name changed to {new_name}.[/green]")
        else:
            self.console.print("[red]Invalid name.[/red]")

    def handle_ship_rename(self, command):
        """Handle ship rename"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: shipname [new_name][/red]")
            return
        
        new_name = ' '.join(parts[1:])
        if self.player.change_ship_name(new_name):
            self.console.print(f"[green]Ship renamed to {new_name}.[/green]")
        else:
            self.console.print("[red]Invalid ship name.[/red]")

    def show_skills(self):
        """Show player skills"""
        self.console.print("\n[bold cyan]Skills[/bold cyan]")
        self.console.print("=" * 30)
        
        for skill_name, skill in self.player.skills.items():
            self.console.print(f"\n[bold yellow]{skill.name}[/bold yellow]")
            self.console.print(f"   Level: {skill.level}")
            self.console.print(f"   Progress: {skill.get_progress_percentage():.1f}%")
            self.console.print(f"   Bonus: +{skill.get_skill_bonus():.1f}%")

    def handle_combat(self, command):
        """Handle combat commands"""
        if not self.world.is_in_combat():
            self.console.print("[red]There's nothing to attack here.[/red]")
            return
        
        # Combat logic would go here
        self.console.print("[yellow]Combat system not yet implemented.[/yellow]")

    def handle_counselor_interaction(self):
        """Handle interactions with the ship counselor AI"""
        self.console.print("\n[bold cyan]Ship Counselor AI[/bold cyan]")
        self.console.print("=" * 40)
        self.console.print("Chat with your ship's AI counselor. Type 'bye' to exit.")
        self.console.print("The counselor can provide advice on trading, combat, travel, and general gameplay.")
        
        # Initial greeting
        initial_response = self.counselor.chat("hello")
        self.counselor.display_response(initial_response)
        
        while True:
            self.console.print("\n[cyan]You:[/cyan] ", end="")
            user_input = self.input_handler.get_input()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit', 'q']:
                farewell_response = self.counselor.chat("goodbye")
                self.counselor.display_response(farewell_response)
                break
            
            # Get player context for more relevant advice
            player_context = {
                'credits': self.player.credits,
                'health': self.player.health,
                'fuel': getattr(self.player, 'fuel', 100),  # Default if not set
                'level': self.player.level,
                'experience': self.player.experience
            }
            
            # Get counselor response
            response = self.counselor.chat(user_input, player_context)
            self.counselor.display_response(response)

    def handle_unequipment(self, command):
        """Handle unequipment commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: unequip [slot_name][/red]")
            return
        
        slot_name = ' '.join(parts[1:])
        success = self.player.unequip_item(slot_name)
        
        if success:
            self.console.print(f"[green]Unequipped {slot_name}.[/green]")
        else:
            self.console.print(f"[red]Could not unequip {slot_name}.[/red]")

    def show_sectors(self):
        """Show all sectors and their status"""
        all_sectors = self.world.get_all_sectors()
        discovered_sectors = self.world.get_discovered_sectors()
        
        self.console.print("\n[bold cyan]Galactic Sectors[/bold cyan]")
        self.console.print("=" * 40)
        
        for sector in all_sectors:
            sector_info = self.world.get_sector_info(sector)
            if sector in discovered_sectors:
                self.console.print(f"[green]✓ {sector}[/green]")
                self.console.print(f"   Locations: {', '.join(sector_info['locations'])}")
                self.console.print(f"   Danger Level: {sector_info['danger_level']}/10")
                self.console.print(f"   Factions: {', '.join(sector_info['factions'])}")
            else:
                self.console.print(f"[dim]? {sector} (Undiscovered)[/dim]")
            self.console.print()

    def show_current_sector(self):
        """Show information about current sector"""
        current_loc = self.world.get_current_location()
        if not current_loc:
            return
        
        sector_info = self.world.get_sector_info(current_loc.sector)
        
        self.console.print(f"\n[bold cyan]Current Sector: {current_loc.sector}[/bold cyan]")
        self.console.print("=" * 40)
        self.console.print(f"Location: {current_loc.name}")
        self.console.print(f"Type: {current_loc.location_type.title()}")
        self.console.print(f"Danger Level: {current_loc.danger_level}/10")
        self.console.print(f"Faction: {current_loc.faction}")
        
        if current_loc.connections:
            self.console.print(f"Connected Sectors: {', '.join(current_loc.connections)}")
        
        if current_loc.services:
            self.console.print(f"Services: {', '.join(current_loc.services)}")

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