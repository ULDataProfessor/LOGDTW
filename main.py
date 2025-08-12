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
sys.path.append(os.path.join(os.path.dirname(__file__), "game"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from game.player import Player, Item
from game.world import World
from game.world_generator import WorldGenerator
from game.combat import CombatSystem
from game.dynamic_markets import DynamicMarketSystem
from game.quests import QuestSystem
from game.npcs import NPCSystem
from game.holodeck import HolodeckSystem
from game.stock_market import StockMarket, BankingSystem
from game.sos_system import SOSSystem
from game.skills import Skill
from game.ai_counselor import ShipCounselor
from game.ship_customization import ShipCustomization
from game.empire import EmpireSystem
from utils.display import DisplayManager
from utils.input_handler import InputHandler
from game.save_system import SaveGameSystem
from game.achievements import AchievementSystem


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
        self.save_system = SaveGameSystem()
        # Auto-save settings
        self._last_auto_save_ts = 0.0
        self._auto_save_interval_s = 300  # 5 minutes
        self.achievements = AchievementSystem()
        self.running = False
        self.save_system = SaveGameSystem()
        self.empire = EmpireSystem()

    def clear_screen(self):
        """Clear the console screen"""
        os.system("clear" if os.name == "posix" else "cls")

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
        menu_table.add_row("2", "Save Game")
        menu_table.add_row("3", "Load Game")
        menu_table.add_row("4", "Help")
        menu_table.add_row("5", "Quit")

        self.console.print(menu_table)
        self.console.print("\n")

    def get_menu_choice(self):
        """Get the player's menu choice"""
        while True:
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            if choice == "1":
                return "new_game"
            elif choice == "2":
                self.save()
            elif choice == "3":
                self.load()
            elif choice == "4":
                return "help"
            elif choice == "5":
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
        
        [bold yellow]TW2002 Sector Navigation:[/bold yellow]
        - jump [sector_number] (jump to connected sector with confirmation)
        - warp [sector_number] (instant jump with confirmation)
        - map (show galactic map)
        - sectors (show all sectors)
        - sector (show current sector info)
        - Travel estimates show fuel cost, time, danger level, and faction
        - Connected sectors shown with types: Federation, Neutral, Enemy, Hop, Skip, Warp
        
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
        - Ask about rumors, secrets, classified data, trade secrets
        - Seek prophecies from mystics, request stories from entertainers
        
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
        - ship install [component] (install upgrade)
        - ship remove [slot] (remove upgrade)
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
ship install/remove - Manage upgrades
cargo - Cargo    skills - Skills         counselor - AI chat
sectors - All sectors  sector - Current sector
        """
        self.console.print(Panel(quick_help, title="Quick Help", border_style="green"))

    def _create_game_state(self):
        """Collect current game objects into a GameState"""
        self.player.ship["upgrades"] = self.player.ship_customization.to_dict()
        state = self.save_system.create_game_state(
            self.player,
            self.world,
            self.quest_system,
            self.npc_system,
            self.trading_system,
            self.player.skills,
            self.combat_system,
            {},
            {"play_time": 0},
            achievements=self.achievements.get_unlocked(),
        )
        # Inject empire owned planets into world_data for persistence
        try:
            state.world_data["empire_owned"] = getattr(self.empire, "owned", {})
        except Exception:
            pass
        return state

    def _apply_game_state(self, game_state):
        """Apply a loaded GameState to current game objects"""
        if not game_state:
            return False

        pd = game_state.player_data
        self.player.name = pd.get("name", self.player.name)
        self.player.ship = pd.get("ship", self.player.ship)
        self.player.ship_name = self.player.ship.get("name", self.player.ship_name)
        self.player.level = pd.get("level", self.player.level)
        self.player.credits = pd.get("credits", self.player.credits)
        self.player.experience = pd.get("experience", self.player.experience)
        self.player.ship_customization = ShipCustomization(self.player.ship)

        # Restore empire owned planets if present
        try:
            empire_owned = game_state.world_data.get("empire_owned")
            if empire_owned:
                self.empire.owned = empire_owned
        except Exception:
            pass

        wd = game_state.world_data
        self.world.current_sector = wd.get("current_sector", self.world.current_sector)
        self.world.current_location = wd.get("current_location", self.world.current_location)
        self.world.player_coordinates = wd.get("player_coordinates", self.world.player_coordinates)
        self.achievements.load(getattr(game_state, "achievements", []), self.player)
        return True

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
        self.trading_system = DynamicMarketSystem()
        # Initialize dynamic market sectors based on world locations
        for loc in self.world.locations.values():
            self.trading_system.initialize_sector_economy(loc.sector)
        self.quest_system = QuestSystem()
        self.npc_system = NPCSystem(self.quest_system, self.trading_system)
        self.holodeck_system = HolodeckSystem()
        self.stock_market = StockMarket()
        self.banking_system = BankingSystem()
        self.sos_system = SOSSystem()
        self.counselor = ShipCounselor()
        self.achievements.reset()

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
                    if travel_status.get("arrived"):
                        self.console.print(f"[green]{travel_status['message']}[/green]")
                        self.display.show_location(self.world.get_current_location())
                    else:
                        self.console.print(
                            f"[yellow]Jumping to {travel_status['destination']}... {travel_status['progress']:.1f}% complete[/yellow]"
                        )
                        time.sleep(1)
                        self._auto_save()
                        continue

                # Check if on a planet surface
                if self.world.is_on_planet_surface():
                    self.display.show_planet_surface(self.world)
                    self.display.show_planet_surface_instructions(self.world)
                    command = self.input_handler.get_input()
                    if command.lower() in ["quit", "exit", "q"]:
                        if Confirm.ask("Are you sure you want to quit?"):
                            self.running = False
                            break
                    elif command.lower() in ["leave", "orbit"]:
                        result = self.world.leave_planet_surface()
                        self.console.print(result["message"])
                    elif command.lower() in ["n", "north", "s", "south", "e", "east", "w", "west"]:
                        dir_map = {"n": "north", "s": "south", "e": "east", "w": "west"}
                        direction = dir_map.get(command.lower(), command.lower())
                        result = self.world.move_on_surface(direction)
                        if not result["moved"]:
                            self.console.print(f"[red]You can't move {direction} from here.[/red]")
                        else:
                            for event in result["events"]:
                                if event["type"] == "combat":
                                    self.console.print("[red]Hostile encounter![/red]")
                                    self.combat_system.start_combat(
                                        self.player, event.get("enemy_type")
                                    )
                                elif event["type"] == "item":
                                    names = ", ".join([item.name for item in event["items"]])
                                    self.console.print(
                                        f"[green]You found: {names}. Use 'take <item>' to pick up.[/green]"
                                    )
                                elif event["type"] == "npc":
                                    names = ", ".join(event["npcs"])
                                    self.console.print(
                                        f"[cyan]You encounter: {names}. Use 'talk <npc>' to interact. They may assist your mission.[/cyan]"
                                    )
                                elif event["type"] == "resource":
                                    self.console.print(
                                        f"[yellow]Resource detected: {event['resource']}. Use 'gather' to collect.[/yellow]"
                                    )

                            # Update surface mission progress from tile events
                            if hasattr(self, "surface_mission") and self.surface_mission:
                                try:
                                    self.surface_mission = (
                                        self.quest_system.update_surface_mission_with_events(
                                            self.surface_mission,
                                            self.world.planet_surface,
                                            result["events"],
                                        )
                                    )
                                    if self.surface_mission.get("completed"):
                                        rewards = self.surface_mission.get("rewards", {})
                                        self.player.add_credits(rewards.get("credits", 0))
                                        self.player.add_experience(rewards.get("experience", 0))
                                        self.console.print(
                                            "[bold green]Surface mission completed! Rewards granted.[/bold green]"
                                        )
                                        self.surface_mission = None
                                except Exception:
                                    pass
                    elif command.startswith("take "):
                        item_name = command[5:]
                        result = self.world.collect_surface_item(self.player, item_name)
                        self.console.print(result["message"])
                    elif command.startswith("talk "):
                        npc_name = command[5:]
                        result = self.world.talk_to_surface_npc(npc_name)
                        self.console.print(result["message"])
                    elif command.lower() in ["gather", "collect"]:
                        result = self.world.collect_surface_resource(self.player)
                        self.console.print(result["message"])
                        if hasattr(self, "surface_mission") and self.surface_mission:
                            try:
                                self.surface_mission = (
                                    self.quest_system.update_surface_mission_with_events(
                                        self.surface_mission,
                                        self.world.planet_surface,
                                        [
                                            {
                                                "type": "resource",
                                                "resource": self.world.get_surface_area().get(
                                                    "resource"
                                                ),
                                            }
                                        ],
                                    )
                                )
                                if self.surface_mission.get("completed"):
                                    rewards = self.surface_mission.get("rewards", {})
                                    self.player.add_credits(rewards.get("credits", 0))
                                    self.player.add_experience(rewards.get("experience", 0))
                                    self.console.print(
                                        "[bold green]Surface mission completed! Rewards granted.[/bold green]"
                                    )
                                    self.surface_mission = None
                            except Exception:
                                pass
                    elif command.lower() == "look":
                        self.display.show_planet_surface(self.world)
                    else:
                        self.console.print(
                            "[yellow]Available commands: n/s/e/w to move, take <item>, talk <npc>, gather, leave/orbit to return to space.[/yellow]"
                        )
                    continue

                # Check if in holodeck
                holodeck_status = self.holodeck_system.update_program(self.player)
                if holodeck_status.get("active"):
                    self.console.print(
                        f"[cyan]Holodeck: {holodeck_status['program'].name} - {holodeck_status['progress']:.1f}% complete[/cyan]"
                    )
                    time.sleep(1)
                    self._auto_save()
                    continue
                elif holodeck_status.get("completed"):
                    self.console.print(f"[green]{holodeck_status['message']}[/green]")

                # Update systems
                self.stock_market.update_market()
                # Advance dynamic market simulation
                self.trading_system.update_market(self.trading_system.current_turn + 1)
                self.banking_system.update_interest()
                self.sos_system.update_signals()

                # Generate random events
                self._check_random_events()

                # Empire per-turn production
                try:
                    yields = self.empire.update(self.player, self.world)
                    if (yields.get("credits", 0) >= 100) or (yields.get("soldiers", 0) >= 5):
                        self.console.print(
                            f"[cyan]Empire yields: +{int(yields.get('credits', 0))} credits, +{int(yields.get('soldiers', 0))} soldiers[/cyan]"
                        )
                except Exception:
                    pass

                # Display current location and status
                self.display.show_location(self.world.get_current_location())
                self.display.show_status(self.player, self.achievements.get_unlocked_names())
                self.display.show_tw2002_sector_display(self.world)
                self.display.show_space_instructions(self.world)

                # Get player input
                command = self.input_handler.get_input()
                if isinstance(command, str):
                    command = command.strip()

                # Process command (case-insensitive)
                cmd_lower = command.lower() if isinstance(command, str) else ""
                if cmd_lower in ["quit", "exit", "q"]:
                    if Confirm.ask("Are you sure you want to quit?"):
                        self.running = False
                        break

                elif cmd_lower in ["help", "h"]:
                    self.show_help()

                elif cmd_lower == "?":
                    self.show_quick_help()

                elif cmd_lower in ["status", "stats", "s"]:
                    self.display.show_detailed_status(self.player)

                elif cmd_lower in ["inventory", "inv", "i"]:
                    self.display.show_inventory(self.player)

                elif cmd_lower in ["look", "l"]:
                    self.display.show_location_description(self.world.get_current_location())

                elif cmd_lower in ["north", "n", "south", "s", "east", "e", "west", "w"]:
                    self.handle_movement(command.lower())

                elif cmd_lower == "land":
                    result = self.world.land_on_planet()
                    self.console.print(result["message"])
                    if result.get("success"):
                        try:
                            self.surface_mission = (
                                self.quest_system.generate_surface_exploration_mission(
                                    self.world, self.player
                                )
                            )
                            if self.surface_mission:
                                self.console.print(
                                    "[bold cyan]Surface Mission:[/bold cyan] Explore tiles, collect a resource, defeat a threat, meet an NPC, then return to start."
                                )
                        except Exception:
                            self.surface_mission = None

                elif cmd_lower.startswith("jump"):
                    self.handle_travel(command)

                elif cmd_lower == "map":
                    self.console.print(self.world.get_map_display())

                elif cmd_lower == "sectors":
                    self.show_sectors()
                
                elif cmd_lower.startswith("db sector"):
                    # db sector <id>
                    parts = command.split()
                    if len(parts) < 3:
                        self.console.print("[yellow]Usage: db sector <id>[/yellow]")
                    else:
                        try:
                            sid = int(parts[2])
                            rec = self.world.get_or_create_sector(sid)
                            self.console.print(f"[bold cyan]Sector {sid}[/bold cyan] {rec['name']} | faction={rec['faction']} region={rec['region']} danger={rec['danger_level']}")
                            self.console.print(f"services: market={rec['has_market']} outpost={rec['has_outpost']} station={rec['has_station']} research={rec['has_research']} mining={rec['has_mining']}")
                            self.console.print(f"connections: {', '.join(map(str, rec['connections']))}")
                        except Exception as e:
                            self.console.print(f"[red]Error: {e}[/red]")

                elif cmd_lower.startswith("db neighbors"):
                    # db neighbors <id>
                    parts = command.split()
                    if len(parts) < 3:
                        self.console.print("[yellow]Usage: db neighbors <id>[/yellow]")
                    else:
                        try:
                            sid = int(parts[2])
                            rec = self.world.get_or_create_sector(sid)
                            neigh = rec.get('connections', [])
                            self.console.print(f"[bold cyan]Neighbors of Sector {sid}[/bold cyan]: {', '.join(map(str, neigh))}")
                        except Exception as e:
                            self.console.print(f"[red]Error: {e}[/red]")

                elif cmd_lower.startswith("capture"):
                    result = self.empire.capture_current_planet(self.player, self.world)
                    self.console.print(result["message"])

                elif cmd_lower.startswith("policy"):
                    try:
                        parts = command.split()[1:]
                        kwargs = {}
                        for part in parts:
                            if "=" in part:
                                k, v = part.split("=", 1)
                                kwargs[k] = int(v)
                        loc = self.world.get_current_location()
                        res = self.empire.set_policy(loc.name, self.world.current_sector, **kwargs)
                        self.console.print(res["message"])
                    except Exception:
                        self.console.print(
                            "[yellow]Usage: policy agriculture=30 industry=30 defense=20 research=20 tax=10[/yellow]"
                        )

                elif cmd_lower.startswith("raise soldiers"):
                    try:
                        amount = int(command.split()[-1])
                        loc = self.world.get_current_location()
                        res = self.empire.raise_soldiers(
                            loc.name, self.world.current_sector, amount, self.player
                        )
                        self.console.print(res["message"])
                    except Exception:
                        self.console.print("[yellow]Usage: raise soldiers <amount>[/yellow]")

                elif cmd_lower == "empire":
                    status = self.empire.status()
                    if not status:
                        self.console.print("[dim]No owned planets.[/dim]")
                    else:
                        self.console.print("[bold cyan]Empire Status[/bold cyan]")
                        for p in status:
                            self.console.print(
                                f"- {p['name']} (Sector {p['sector']}) pop={p['population']} morale={p['morale']} garrison={p['garrison']} policies={p['policies']}"
                            )

                elif cmd_lower == "sector":
                    self.show_current_sector()

                elif cmd_lower.startswith("warp"):
                    self.handle_warp(command)

                elif cmd_lower.startswith("buy") or cmd_lower.startswith("sell"):
                    self.handle_trading(command)

                elif cmd_lower == "market":
                    self.show_market_info()

                elif cmd_lower == "trade routes":
                    self.show_trade_routes()

                elif cmd_lower == "trade history":
                    self.show_trade_history()

                elif cmd_lower.startswith("talk") or cmd_lower.startswith("chat"):
                    self.handle_npc_interaction(command)

                elif cmd_lower == "npcs":
                    self.show_npcs()

                elif cmd_lower == "holodeck":
                    self.show_holodeck()

                elif cmd_lower == "programs":
                    self.show_holodeck_programs()

                elif cmd_lower.startswith("start"):
                    self.handle_holodeck_program(command)

                elif cmd_lower == "stocks":
                    self.show_stock_market()

                elif cmd_lower == "bank":
                    self.show_banking()

                elif cmd_lower == "sos":
                    self.show_sos_signals()

                elif cmd_lower.startswith("rescue"):
                    self.handle_rescue(command)

                elif cmd_lower.startswith("ship install"):
                    self.handle_ship_install(command)
                elif cmd_lower.startswith("ship remove"):
                    self.handle_ship_remove(command)
                elif cmd_lower == "ship":
                    self.show_ship_status()

                elif cmd_lower == "cargo":
                    self.show_cargo()

                elif cmd_lower.startswith("equip"):
                    self.handle_equipment(command)

                elif cmd_lower.startswith("rename"):
                    self.handle_rename(command)

                elif cmd_lower.startswith("shipname"):
                    self.handle_ship_rename(command)

                elif cmd_lower == "skills":
                    self.show_skills()
                elif cmd_lower == "save":
                    save_name = Prompt.ask("Save name", default="save")
                    state = self._create_game_state()
                    self.save_system.save_game(state, save_name, "Manual save", overwrite=True)

                elif cmd_lower == "load":
                    saves = self.save_system.get_save_list()
                    if not saves:
                        self.console.print("[yellow]No save games available.[/yellow]")
                    else:
                        for i, meta in enumerate(saves, 1):
                            self.console.print(f"{i}. {meta.save_id} - {meta.player_name}")
                        choice = Prompt.ask(
                            "Select save", choices=[str(i) for i in range(1, len(saves) + 1)]
                        )
                        save_id = saves[int(choice) - 1].save_id
                        state = self.save_system.load_game(save_id)
                        if state:
                            self._apply_game_state(state)

                elif cmd_lower == "clear":
                    self.clear_screen()

                elif cmd_lower.startswith("attack"):
                    self.handle_combat(command)

                elif cmd_lower in ["quests", "missions"]:
                    self.quest_system.generate_dynamic_quest(self.player)
                    self.display.show_quests(self.quest_system.get_available_quests(self.player))

                elif cmd_lower in ["genesis", "fire genesis"]:
                    if self.world.is_on_planet_surface():
                        self.console.print(
                            "[red]You must be in space to use the Genesis Torpedo.[/red]"
                        )
                    else:
                        result = self.world.fire_genesis_torpedo(self.player)
                        self.console.print(result["message"])
                        if result.get("success"):
                            self.console.print(
                                f"[green]You can now 'jump {result['planet']}' or 'land' to visit the new planet![/green]"
                            )

                elif cmd_lower in ["counselor", "ai"]:
                    self.handle_counselor_interaction()

                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                    self.console.print("Type '?' for quick help or 'help' for full help.")

                self._auto_save()

            except KeyboardInterrupt:
                if Confirm.ask("\nAre you sure you want to quit?"):
                    self.running = False
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _auto_save(self):
        """Perform periodic autosave using SaveGameSystem.auto_save."""
        try:
            now = time.time()
            if now - self._last_auto_save_ts < self._auto_save_interval_s:
                return
            game_state = self._create_game_state()
            did_save = self.save_system.auto_save(game_state)
            if did_save:
                self._last_auto_save_ts = now
                self.console.print("[dim]Auto-saved game.[/dim]")
        except Exception as e:
            # Do not crash game loop on autosave errors
            self.console.print(f"[yellow]Auto-save skipped: {e}[/yellow]")

    def _check_random_events(self):
        """Check for random events"""
        # Generate distress signals
        if random.random() < 0.05:  # 5% chance
            signal = self.sos_system.generate_distress_signal(self.player.coordinates)
            if signal:
                self.console.print(
                    f"[red]DISTRESS SIGNAL DETECTED: {signal.ship_name} needs help![/red]"
                )
                self.console.print(f"[yellow]Type 'sos' to view distress signals[/yellow]")

    def _show_warp_ports(self):
        """Show available sector jumps"""
        current_location = self.world.get_current_location()
        if current_location and hasattr(current_location, "connections"):
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
            "north": current_location.connections[0] if current_location.connections else None,
            "south": (
                current_location.connections[1] if len(current_location.connections) > 1 else None
            ),
            "east": current_location.connections[0] if current_location.connections else None,
            "west": (
                current_location.connections[1] if len(current_location.connections) > 1 else None
            ),
            "n": current_location.connections[0] if current_location.connections else None,
            "s": current_location.connections[1] if len(current_location.connections) > 1 else None,
            "e": current_location.connections[0] if current_location.connections else None,
            "w": current_location.connections[1] if len(current_location.connections) > 1 else None,
        }

        destination = jump_map.get(direction)
        if destination:
            self.handle_sector_jump(destination)
        else:
            self.console.print(
                f"[red]No sector available in that direction. Use 'jump [sector_name]' to jump to a specific sector.[/red]"
            )

    def handle_sector_jump(self, destination: str):
        """Handle jumping to a specific sector"""
        jump_info = self.world.get_jump_info(destination)
        if not jump_info["available"]:
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
            if result["success"]:
                self.console.print(f"[green]{result['message']}[/green]")
            else:
                self.console.print(f"[red]{result['message']}[/red]")

    def handle_travel(self, command):
        """Handle travel commands (now sector jumping)"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: jump [sector_number][/red]")
            return

        try:
            sector_number = int(parts[1])

            # Get travel estimate first
            if self.world.can_jump_to_sector(sector_number):
                # Find the connection details
                connection = None
                for conn in self.world.sector_connections[self.world.current_sector]:
                    if conn.destination_sector == sector_number:
                        connection = conn
                        break

                if connection:
                    # Show travel estimate
                    self.console.print(
                        f"\n[bold cyan]Travel Estimate to Sector {sector_number}:[/bold cyan]"
                    )
                    self.console.print(f"  Connection Type: {connection.connection_type.upper()}")
                    self.console.print(f"  Fuel Cost: {connection.fuel_cost}")
                    self.console.print(f"  Travel Time: {connection.travel_time} minutes")
                    self.console.print(f"  Danger Level: {connection.danger_level}/10")
                    self.console.print(
                        f"  Faction: {self.world.sector_factions.get(sector_number, 'Unknown')}"
                    )

                    # Check if player has enough fuel
                    if self.player.fuel < connection.fuel_cost:
                        self.console.print(
                            f"\n[red]Insufficient fuel! You need {connection.fuel_cost} fuel but only have {self.player.fuel}.[/red]"
                        )
                        return

                    # Ask for confirmation
                    self.console.print(
                        f"\n[yellow]Are you sure you want to commit {connection.travel_time} minutes to travel to Sector {sector_number}?[/yellow]"
                    )
                    if not Confirm.ask("Proceed with jump?"):
                        self.console.print("[yellow]Jump cancelled.[/yellow]")
                        return

                    # Proceed with jump
                    result = self.world.jump_to_sector(sector_number, self.player)

                    if result["success"]:
                        self.console.print(f"[green]{result['message']}[/green]")
                    else:
                        self.console.print(f"[red]{result['message']}[/red]")
                else:
                    self.console.print(f"[red]No connection found to Sector {sector_number}[/red]")
            else:
                self.console.print(
                    f"[red]Cannot jump to Sector {sector_number} from current location[/red]"
                )
        except ValueError:
            self.console.print("[red]Sector number must be a number (e.g., 'jump 2')[/red]")

    def handle_warp(self, command):
        """Handle warp commands (instant sector jumping)"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: warp [sector_number][/red]")
            return

        try:
            sector_number = int(parts[1])

            # Get travel estimate first
            if self.world.can_jump_to_sector(sector_number):
                # Find the connection details
                connection = None
                for conn in self.world.sector_connections[self.world.current_sector]:
                    if conn.destination_sector == sector_number:
                        connection = conn
                        break

                if connection:
                    # Show warp estimate
                    self.console.print(
                        f"\n[bold cyan]Warp Estimate to Sector {sector_number}:[/bold cyan]"
                    )
                    self.console.print(f"  Connection Type: {connection.connection_type.upper()}")
                    self.console.print(f"  Fuel Cost: {connection.fuel_cost} (instant travel)")
                    self.console.print(f"  Travel Time: Instant")
                    self.console.print(f"  Danger Level: {connection.danger_level}/10")
                    self.console.print(
                        f"  Faction: {self.world.sector_factions.get(sector_number, 'Unknown')}"
                    )

                    # Check if player has enough fuel
                    if self.player.fuel < connection.fuel_cost:
                        self.console.print(
                            f"\n[red]Insufficient fuel! You need {connection.fuel_cost} fuel but only have {self.player.fuel}.[/red]"
                        )
                        return

                    # Ask for confirmation
                    self.console.print(
                        f"\n[yellow]Are you sure you want to warp to Sector {sector_number}?[/yellow]"
                    )
                    if not Confirm.ask("Proceed with warp?"):
                        self.console.print("[yellow]Warp cancelled.[/yellow]")
                        return

                    # Proceed with warp
                    result = self.world.jump_to_sector(sector_number, self.player)

                    if result["success"]:
                        # Complete the jump immediately (warp)
                        self.world._complete_jump(self.player)
                        self.console.print(f"[green]Warped to Sector {sector_number}![/green]")
                    else:
                        self.console.print(f"[red]{result['message']}[/red]")
                else:
                    self.console.print(f"[red]No connection found to Sector {sector_number}[/red]")
            else:
                self.console.print(
                    f"[red]Cannot warp to Sector {sector_number} from current location[/red]"
                )
        except ValueError:
            self.console.print("[red]Sector number must be a number (e.g., 'warp 2')[/red]")

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

        current_loc = self.world.get_current_location()
        sector_id = current_loc.sector

        prices = self.trading_system.get_sector_prices(sector_id)
        if item_name not in prices:
            self.console.print(f"[red]{item_name} not available in this market.[/red]")
            return

        price_per_unit = prices[item_name]
        total_price = price_per_unit * quantity

        if action == "buy":
            if self.player.credits < total_price:
                self.console.print("[red]Not enough credits.[/red]")
                return
            trade = self.trading_system.execute_trade(item_name, quantity, sector_id, True)
            if trade.get("success"):
                self.player.credits -= total_price
                for _ in range(quantity):
                    self.player.add_item(
                        Item(item_name, f"{item_name} commodity", price_per_unit, "trade_good")
                    )
                self.console.print(
                    f"[green]Bought {quantity} {item_name} for {total_price} credits[/green]"
                )
            else:
                self.console.print(f"[red]{trade.get('error', 'Trade failed')}[/red]")
        elif action == "sell":
            owned = [i for i in self.player.inventory if i.name == item_name]
            if len(owned) < quantity:
                self.console.print("[red]You don't have enough to sell.[/red]")
                return
            trade = self.trading_system.execute_trade(item_name, quantity, sector_id, False)
            if trade.get("success"):
                self.player.credits += trade["price_per_unit"] * quantity
                to_remove = quantity
                for item in list(self.player.inventory):
                    if item.name == item_name and to_remove > 0:
                        self.player.inventory.remove(item)
                        to_remove -= 1
                self.console.print(
                    f"[green]Sold {quantity} {item_name} for {trade['price_per_unit'] * quantity} credits[/green]"
                )
            else:
                self.console.print(f"[red]{trade.get('error', 'Trade failed')}[/red]")
        else:
            self.console.print("[red]Invalid trading command.[/red]")

    def show_market_info(self):
        """Show market information using dynamic market system"""
        current_location = self.world.get_current_location()
        sector_id = current_location.sector
        prices = self.trading_system.get_sector_prices(sector_id)

        if not prices:
            self.console.print("[red]No market data available here.[/red]")
            return

        self.console.print("\n[bold cyan]Market Prices[/bold cyan]")
        self.console.print("=" * 40)
        for name, price in prices.items():
            self.console.print(f"{name}: {price} credits")

    def show_trade_routes(self):
        """Show best trade opportunities between connected sectors"""
        current_location = self.world.get_current_location()
        current_sector = current_location.sector
        accessible_sectors = []
        for name in current_location.connections:
            if name in self.world.locations:
                accessible_sectors.append(self.world.locations[name].sector)

        routes = self.trading_system.get_best_trade_opportunities(
            current_sector, accessible_sectors
        )

        if not routes:
            self.console.print("[yellow]No profitable trade routes found.[/yellow]")
            return

        self.console.print("\n[bold cyan]Best Trade Opportunities[/bold cyan]")
        self.console.print("=" * 50)

        for i, route in enumerate(routes, 1):
            self.console.print(f"\n[bold yellow]{i}. {route['commodity']}[/bold yellow]")
            self.console.print(
                f"   Buy in Sector {route['buy_sector']}: {route['buy_price']} credits"
            )
            self.console.print(
                f"   Sell in Sector {route['sell_sector']}: {route['sell_price']} credits"
            )
            self.console.print(
                f"   Profit/unit: {route['profit_per_unit']} ({route['profit_margin']*100:.1f}% margin)"
            )

    def show_trade_history(self):
        """Show trade history"""
        history = []
        for commodity, trades in self.trading_system.trade_volumes.items():
            for trade in trades:
                entry = trade.copy()
                entry["commodity"] = commodity
                history.append(entry)

        if not history:
            self.console.print("[yellow]No trade history available.[/yellow]")
            return

        self.console.print("\n[bold cyan]Recent Trade History[/bold cyan]")
        self.console.print("=" * 50)

        for trade in history[-10:]:
            action = "Bought" if trade["type"] == "buy" else "Sold"
            self.console.print(
                f"{action} {trade['quantity']} {trade['commodity']} in Sector {trade['sector']} for {trade['price']} credits"
            )

    def handle_npc_interaction(self, command):
        """Handle NPC interactions"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: talk/chat [npc_name][/red]")
            return

        npc_name = " ".join(parts[1:])
        result = self.npc_system.start_conversation(self.player, npc_name)

        if result["success"]:
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
                choice = Prompt.ask(
                    "Choose an option", choices=[str(i) for i in range(1, len(options) + 1)]
                )
                choice_index = int(choice) - 1
                selected_option = options[choice_index]

                result = self.npc_system.handle_conversation_choice(
                    self.player, npc, selected_option
                )
                self.console.print(f"[cyan]{result['message']}[/cyan]")

                if result.get("quest_offer"):
                    quest_id = result["quest_offer"]
                    quest = self.quest_system.available_quests.get(quest_id)
                    if quest and Confirm.ask(f"Accept quest '{quest.name}'?"):
                        q_result = self.quest_system.accept_quest(self.player, quest_id)
                        self.console.print(f"[green]{q_result['message']}[/green]")

                if result.get("price_modifier"):
                    self.console.print(f"[green]Market prices adjusted at {npc.location}![/green]")

                if result.get("rep_change"):
                    self.console.print(
                        f"[magenta]Relationship with {npc.name} changed by {result['rep_change']}[/magenta]"
                    )

                if result.get("end_conversation"):
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

        program_name = " ".join(parts[1:])
        result = self.holodeck_system.start_program(self.player, program_name)

        if result["success"]:
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

        if result["success"]:
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
        upgrades = ship.get("upgrades", {})
        if upgrades:
            self.console.print("Upgrades:")
            for slot, name in upgrades.items():
                self.console.print(f"  {slot}: {name}")
        else:
            self.console.print("No upgrades installed.")

    def handle_ship_install(self, command):
        """Install a ship upgrade component."""
        parts = command.split()
        if len(parts) < 3:
            self.console.print("[red]Usage: ship install [component][/red]")
            return
        component = parts[2]
        if self.player.install_upgrade(component):
            self.console.print(f"[green]{component} installed.[/green]")
        else:
            self.console.print(f"[red]Failed to install {component}.[/red]")

    def handle_ship_remove(self, command):
        """Remove an installed ship upgrade."""
        parts = command.split()
        if len(parts) < 3:
            self.console.print("[red]Usage: ship remove [slot][/red]")
            return
        slot = parts[2]
        if self.player.remove_upgrade(slot):
            self.console.print(f"[green]{slot} upgrade removed.[/green]")
        else:
            self.console.print(f"[red]No upgrade installed in {slot} slot.[/red]")

    def show_cargo(self):
        """Show cargo holds"""
        cargo_summary = self.player.get_cargo_summary()

        self.console.print("\n[bold cyan]Cargo Holds[/bold cyan]")
        self.console.print("=" * 30)

        for hold in cargo_summary["holds"]:
            self.console.print(f"\n[bold yellow]{hold['name']}[/bold yellow]")
            self.console.print(f"   Used: {hold['used']}/{hold['capacity']}")
            self.console.print(f"   Value: {hold['value']} credits")

            if hold["items"]:
                for item in hold["items"]:
                    self.console.print(f"     • {item.name} ({item.value} credits)")

    def handle_equipment(self, command):
        """Handle equipment commands"""
        parts = command.split()
        if len(parts) < 2:
            self.console.print("[red]Usage: equip [item_name][/red]")
            return

        item_name = " ".join(parts[1:])
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

        new_name = " ".join(parts[1:])
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

        new_name = " ".join(parts[1:])
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
        self.console.print(
            "The counselor can provide advice on trading, combat, travel, and general gameplay."
        )

        # Initial greeting
        initial_response = self.counselor.chat("hello")
        self.counselor.display_response(initial_response)

        while True:
            self.console.print("\n[cyan]You:[/cyan] ", end="")
            user_input = self.input_handler.get_input()

            if user_input.lower() in ["bye", "goodbye", "exit", "quit", "q"]:
                farewell_response = self.counselor.chat("goodbye")
                self.counselor.display_response(farewell_response)
                break

            # Get player context for more relevant advice
            player_context = {
                "credits": self.player.credits,
                "health": self.player.health,
                "fuel": getattr(self.player, "fuel", 100),  # Default if not set
                "level": self.player.level,
                "experience": self.player.experience,
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

        slot_name = " ".join(parts[1:])
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
                saves = self.save_system.get_save_list()
                if not saves:
                    self.console.print("[yellow]No saved games available.[/yellow]")
                    input("Press Enter to continue...")
                else:
                    for i, meta in enumerate(saves, 1):
                        self.console.print(f"{i}. {meta.save_id} - {meta.player_name}")
                    choice_idx = Prompt.ask(
                        "Select save", choices=[str(i) for i in range(1, len(saves) + 1)]
                    )
                    save_id = saves[int(choice_idx) - 1].save_id
                    state = self.save_system.load_game(save_id)
                    if state:
                        self.initialize_game()
                        self._apply_game_state(state)
                        self.game_loop()
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
