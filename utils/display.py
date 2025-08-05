"""
Display manager for LOGDTW2002
Handles game display and formatting
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, List, Optional
from game.player import Player
from game.world import Location

class DisplayManager:
    """Handles game display and formatting"""
    
    def __init__(self):
        self.console = Console()
    
    def show_title(self, title: str, subtitle: str = ""):
        """Display a title with optional subtitle"""
        title_text = Text(title, style="bold magenta")
        if subtitle:
            subtitle_text = Text(subtitle, style="cyan")
            self.console.print(title_text)
            self.console.print(subtitle_text)
        else:
            self.console.print(title_text)
    
    def show_location(self, location):
        """Display current location information"""
        if not location:
            self.console.print("[red]Unknown location[/red]")
            return
        
        location_text = f"[bold cyan]{location.name}[/bold cyan] - Sector {location.sector}\n"
        location_text += f"[italic]{location.description}[/italic]\n\n"
        location_text += f"Type: {location.location_type.title()}\n"
        location_text += f"Sector: {location.sector}\n"
        location_text += f"Danger Level: {location.danger_level}/10\n"
        location_text += f"Faction: {location.faction}\n"
        
        if location.services:
            location_text += f"Services: {', '.join(location.services)}\n"
        
        if location.connections:
            location_text += f"Connected Sectors: {', '.join(location.connections)}\n"
        
        self.console.print(Panel(location_text, title="Location", border_style="blue"))
    
    def show_status(self, player: Player):
        """Display player status"""
        if not player:
            return
        
        # Create status table
        status_table = Table(title="Player Status", show_header=False, box=None)
        status_table.add_column("Stat", style="yellow")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Name", player.name)
        status_table.add_row("Level", str(player.level))
        status_table.add_row("Health", f"{player.health}/{player.max_health}")
        status_table.add_row("Energy", f"{player.energy}/{player.max_energy}")
        status_table.add_row("Fuel", f"{player.fuel}/{player.max_fuel}")
        status_table.add_row("Credits", str(player.credits))
        status_table.add_row("Experience", f"{player.experience}/{player.experience_to_next}")
        
        self.console.print(status_table)
    
    def show_detailed_status(self, player: Player):
        """Display detailed player status"""
        if not player:
            return
        
        # Create detailed status panel
        status_text = f"[bold cyan]{player.name}[/bold cyan] - Level {player.level}\n\n"
        
        # Core stats
        stats_text = "[bold yellow]Core Stats:[/bold yellow]\n"
        for stat, value in player.stats.items():
            stats_text += f"  {stat.title()}: {value}\n"
        
        # Combat stats
        combat_text = "\n[bold yellow]Combat Stats:[/bold yellow]\n"
        combat_text += f"  Health: {player.health}/{player.max_health}\n"
        combat_text += f"  Energy: {player.energy}/{player.max_energy}\n"
        combat_text += f"  Damage: {player.get_total_damage()}\n"
        combat_text += f"  Defense: {player.get_total_defense()}\n"
        
        # Skills
        skills_text = "\n[bold yellow]Skills:[/bold yellow]\n"
        for skill_name, skill in player.skills.items():
            skills_text += f"  {skill.name}: {skill.level}\n"
        
        # Ship info
        ship_text = "\n[bold yellow]Ship:[/bold yellow]\n"
        ship_text += f"  Name: {player.ship['name']}\n"
        ship_text += f"  Class: {player.ship['class']}\n"
        ship_text += f"  Cargo Capacity: {player.ship['cargo_capacity']}\n"
        ship_text += f"  Fuel Efficiency: {player.ship['fuel_efficiency']}\n"
        
        # Reputation
        rep_text = "\n[bold yellow]Reputation:[/bold yellow]\n"
        for faction, rep in player.reputation.items():
            rep_text += f"  {faction}: {rep}\n"
        
        full_status = status_text + stats_text + combat_text + skills_text + ship_text + rep_text
        
        self.console.print(Panel(full_status, title="Detailed Status", border_style="green"))
    
    def show_inventory(self, player: Player):
        """Display player inventory"""
        if not player:
            return
        
        if not player.inventory:
            self.console.print("[dim]Inventory is empty[/dim]")
            return
        
        # Create inventory table
        inventory_table = Table(title="Inventory", show_header=True)
        inventory_table.add_column("Item", style="cyan")
        inventory_table.add_column("Type", style="yellow")
        inventory_table.add_column("Value", style="green")
        inventory_table.add_column("Description", style="white")
        
        for item in player.inventory:
            inventory_table.add_row(
                item.name,
                item.item_type.title(),
                str(item.value),
                item.description
            )
        
        self.console.print(inventory_table)
        
        # Show equipped items
        if any(player.equipped.values()):
            equipped_text = "\n[bold yellow]Equipped Items:[/bold yellow]\n"
            for slot, item in player.equipped.items():
                if item:
                    equipped_text += f"  {slot.title()}: {item.name}\n"
                else:
                    equipped_text += f"  {slot.title()}: None\n"
            
            self.console.print(equipped_text)
    
    def show_location_description(self, location):
        """Display detailed location description"""
        if not location:
            self.console.print("[red]Unknown location[/red]")
            return
        
        desc_text = f"[bold cyan]{location.name}[/bold cyan] - Sector {location.sector}\n\n"
        desc_text += f"[italic]{location.description}[/italic]\n\n"
        
        desc_text += f"Location Type: {location.location_type.title()}\n"
        desc_text += f"Sector: {location.sector}\n"
        desc_text += f"Danger Level: {location.danger_level}/10\n"
        desc_text += f"Faction: {location.faction}\n"
        
        if location.services:
            desc_text += f"\nAvailable Services:\n"
            for service in location.services:
                desc_text += f"  • {service.title()}\n"
        
        if location.connections:
            desc_text += f"\nConnected Sectors:\n"
            for connection in location.connections:
                desc_text += f"  • {connection}\n"
        
        if location.items:
            desc_text += f"\nItems Found Here:\n"
            for item in location.items:
                desc_text += f"  • {item.name} ({item.value} credits)\n"
        
        self.console.print(Panel(desc_text, title="Location Details", border_style="cyan"))
    
    def show_combat_status(self, combat_data: Dict):
        """Display combat status"""
        if not combat_data.get('in_combat'):
            return
        
        # Create combat panel
        combat_text = f"[bold red]COMBAT ROUND {combat_data['round']}[/bold red]\n\n"
        
        # Enemy info
        enemy = combat_data['enemy']
        combat_text += f"[bold yellow]Enemy: {enemy['name']}[/bold yellow]\n"
        combat_text += f"Health: {enemy['health']}/{enemy['max_health']}\n"
        combat_text += f"Description: {enemy['description']}\n\n"
        
        # Player info
        player = combat_data['player']
        combat_text += f"[bold green]Your Health: {player['health']}/{player['max_health']}[/bold green]\n"
        combat_text += f"Energy: {player['energy']}/{player['max_energy']}\n\n"
        
        # Combat log
        if combat_data.get('log'):
            combat_text += "[bold cyan]Recent Actions:[/bold cyan]\n"
            for action in combat_data['log']:
                combat_text += f"  {action}\n"
        
        self.console.print(Panel(combat_text, title="Combat", border_style="red"))
    
    def show_market_info(self, market_data: Dict):
        """Display market information"""
        if not market_data.get('available'):
            self.console.print("[dim]No market available here[/dim]")
            return
        
        market_text = f"[bold cyan]Market Information[/bold cyan]\n\n"
        market_text += f"Specialization: {market_data['specialization'].title()}\n"
        market_text += f"Price Modifier: {market_data['price_modifier']:.1f}x\n"
        market_text += f"Trade Volume: {market_data['trade_volume'].title()}\n"
        market_text += f"Security: {market_data['security'].title()}\n\n"
        
        market_text += "[bold yellow]Available Goods:[/bold yellow]\n"
        for good in market_data['goods']:
            market_text += f"  • {good['name']}: {good['price']} credits\n"
            market_text += f"    {good['description']}\n"
        
        self.console.print(Panel(market_text, title="Market", border_style="green"))
    
    def show_trade_opportunities(self, opportunities: List[Dict]):
        """Display trade opportunities"""
        if not opportunities:
            self.console.print("[dim]No trade opportunities available[/dim]")
            return
        
        self.console.print("\n[bold cyan]Trade Opportunities[/bold cyan]")
        self.console.print("=" * 50)
        
        for i, opp in enumerate(opportunities, 1):
            action = "Buy" if opp['type'] == 'buy' else "Sell"
            self.console.print(f"{i}. {action} {opp['item']} for {opp['price']} credits")
    
    def show_trade_history(self, history: List[Dict]):
        """Display trade history"""
        if not history:
            self.console.print("[dim]No trade history available[/dim]")
            return
        
        self.console.print("\n[bold cyan]Trade History[/bold cyan]")
        self.console.print("=" * 50)
        
        for trade in history:
            action = "Bought" if trade['type'] == 'buy' else "Sold"
            self.console.print(f"{action} {trade['quantity']} {trade['item']} at {trade['location']} for {trade['amount']} credits")
    
    def show_travel_info(self, travel_info):
        """Display travel information"""
        if not travel_info.get('available'):
            self.console.print("[red]Cannot travel to this destination[/red]")
            return
        
        travel_text = f"[bold cyan]Jump Information[/bold cyan]\n\n"
        travel_text += f"Destination: {travel_info['destination']}\n"
        travel_text += f"Sector: {travel_info['sector']}\n"
        travel_text += f"Fuel Cost: {travel_info['fuel_cost']}\n"
        travel_text += f"Jump Time: {travel_info['travel_time']} minutes\n"
        travel_text += f"Danger Level: {travel_info['danger_level']}/10\n"
        travel_text += f"Faction: {travel_info['faction']}\n"
        
        if travel_info.get('services'):
            travel_text += f"\nServices: {', '.join(travel_info['services'])}\n"
        
        self.console.print(Panel(travel_text, title="Jump Info", border_style="blue"))
    
    def show_travel_progress(self, progress: float, destination: str, remaining_time: float):
        """Display travel progress"""
        progress_text = f"[bold yellow]Jumping to {destination}[/bold yellow]\n\n"
        progress_text += f"Progress: {progress:.1f}%\n"
        progress_text += f"Remaining Time: {remaining_time:.1f} minutes\n"
        
        # Create a simple progress bar
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        progress_text += f"[{bar}] {progress:.1f}%"
        
        self.console.print(Panel(progress_text, title="Jump Progress", border_style="yellow"))
    
    def show_quests(self, quests: List):
        """Display available quests"""
        if not quests:
            self.console.print("[dim]No quests available[/dim]")
            return
        
        quest_text = "[bold cyan]Available Quests[/bold cyan]\n\n"
        
        for i, quest in enumerate(quests, 1):
            quest_text += f"[bold yellow]{i}. {quest.name}[/bold yellow]\n"
            quest_text += f"   Type: {quest.quest_type.title()}\n"
            quest_text += f"   Difficulty: {quest.difficulty}/10\n"
            quest_text += f"   Faction: {quest.faction}\n"
            quest_text += f"   Description: {quest.description}\n"
            
            if quest.rewards:
                quest_text += "   Rewards: "
                rewards = []
                if 'experience' in quest.rewards:
                    rewards.append(f"{quest.rewards['experience']} XP")
                if 'credits' in quest.rewards:
                    rewards.append(f"{quest.rewards['credits']} credits")
                quest_text += ", ".join(rewards) + "\n"
            
            quest_text += "\n"
        
        self.console.print(Panel(quest_text, title="Quests", border_style="yellow"))
    
    def show_help(self):
        """Display help information"""
        help_text = """
[bold cyan]LOGDTW2002 - Game Controls[/bold cyan]

[bold yellow]Movement:[/bold yellow]
• north, south, east, west (or n, s, e, w)
• up, down, in, out

[bold yellow]Actions:[/bold yellow]
• look, examine, search
• take, drop, use, inventory
• talk, ask, say

[bold yellow]Combat:[/bold yellow]
• attack, defend, flee
• use [weapon/item]

[bold yellow]Space Travel:[/bold yellow]
• travel [destination]
• land, takeoff
• scan, navigate
• map (show space map)

[bold yellow]Trading:[/bold yellow]
• buy [item], sell [item]
• trade, market
• trade routes (show best routes)
• trade history

[bold yellow]System:[/bold yellow]
• status, stats
• save, load, quit
• help

[bold yellow]Special Commands:[/bold yellow]
• quests, missions
• skills, abilities
• equipment, ship
        """
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
    
    def show_ascii_art(self, art_type: str):
        """Display ASCII art"""
        art_pieces = {
            'ship': """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    ████████████████████████████████████████  ║
    ║                  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║                ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║              ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║            ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║      ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║  ████████████████████████████████████████████████████████████  ║
    ╚══════════════════════════════════════════════════════════════╝
            """,
            'planet': """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    ████████████████████████████████████████  ║
    ║                  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║                ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║              ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║            ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║      ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║  ████████████████████████████████████████████████████████████  ║
    ╚══════════════════════════════════════════════════════════════╝
            """,
            'space_station': """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    ████████████████████████████████████████  ║
    ║                  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║                ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║              ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║            ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║          ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║      ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██  ║
    ║  ████████████████████████████████████████████████████████████  ║
    ╚══════════════════════════════════════════════════════════════╝
            """
        }
        
        if art_type in art_pieces:
            self.console.print(art_pieces[art_type], style="cyan")
    
    def show_progress_bar(self, title: str, current: int, maximum: int):
        """Show a progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(title, total=maximum)
            progress.update(task, completed=current)
    
    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear() 

    def show_sector_info(self, sector_info):
        """Display sector information"""
        if not sector_info.get('discovered'):
            self.console.print("[dim]Sector not yet discovered[/dim]")
            return
        
        sector_text = f"[bold cyan]Sector: {sector_info['name']}[/bold cyan]\n\n"
        sector_text += f"Locations: {', '.join(sector_info['locations'])}\n"
        sector_text += f"Danger Level: {sector_info['danger_level']}/10\n"
        sector_text += f"Factions: {', '.join(sector_info['factions'])}\n"
        
        self.console.print(Panel(sector_text, title="Sector Information", border_style="green"))

    def show_sector_map(self, sectors, discovered_sectors):
        """Display a map of all sectors"""
        map_text = "[bold cyan]Galactic Sector Map[/bold cyan]\n\n"
        
        for sector in sectors:
            if sector in discovered_sectors:
                map_text += f"[green]✓ {sector}[/green]\n"
            else:
                map_text += f"[dim]? {sector} (Undiscovered)[/dim]\n"
        
        self.console.print(Panel(map_text, title="Sector Map", border_style="cyan")) 

    def show_adjacent_sectors(self, world):
        """Show adjacent sectors if in space, or adjacent tiles if on planet surface"""
        if world.is_on_planet_surface():
            adj = world.get_surface_adjacent()
            if adj:
                adj_text = "[bold cyan]Adjacent Areas:[/bold cyan] "
                adj_text += ', '.join([f"{dir.title()}" for dir in adj.keys()])
                self.console.print(adj_text)
        else:
            current_location = world.get_current_location()
            if current_location and current_location.connections:
                adj_text = "[bold cyan]Adjacent Sectors:[/bold cyan] "
                adj_text += ', '.join([f"[{sector}]" for sector in current_location.connections])
                self.console.print(adj_text)

    def show_space_instructions(self, world):
        """Show contextual instructions for space navigation"""
        location = world.get_current_location()
        if location and location.location_type == 'planet':
            self.console.print("[yellow]Type 'land' to land on the planet. Use 'jump [sector]' or 'warp [sector]' to travel. Type 'look' to examine, 'help' for more.[/yellow]")
        else:
            self.console.print("[yellow]Use 'jump [sector]' or 'warp [sector]' to travel. Type 'look' to examine, 'help' for more.[/yellow]")

    def show_planet_surface(self, world):
        """Show the planetary surface map and current area description"""
        self.console.print(world.get_surface_map())
        area = world.get_surface_area()
        if area:
            desc = area.get('desc', 'Unknown area')
            self.console.print(f"[bold cyan]Current Area:[/bold cyan] {desc}")

    def show_planet_surface_instructions(self, world):
        """Show contextual instructions for planetary surface movement"""
        adj = world.get_surface_adjacent()
        if adj:
            adj_text = "[bold cyan]You can move:[/bold cyan] " + ', '.join([dir.title() for dir in adj.keys()])
            self.console.print(adj_text)
        self.console.print("[yellow]Use n/s/e/w to move, 'leave' or 'orbit' to return to space. Type 'look' to examine area.[/yellow]")
    
    def show_tw2002_sector_display(self, world):
        """Display TW2002-style sector information"""
        sector_display = world.get_current_sector_display()
        
        if 'error' in sector_display:
            self.console.print(f"[red]{sector_display['error']}[/red]")
            return
        
        # Create the main sector display
        sector_text = f"\n[bold cyan]SECTOR {sector_display['sector']}[/bold cyan]\n"
        sector_text += f"[bold yellow]Location:[/bold yellow] {sector_display['location']}\n"
        sector_text += f"[bold yellow]Faction:[/bold yellow] {sector_display['faction']}\n"
        sector_text += f"[bold yellow]Status:[/bold yellow] {'Discovered' if sector_display['discovered'] else 'Unexplored'}\n\n"
        
        # Show connected sectors with types
        if sector_display['connections']:
            sector_text += "[bold yellow]Connected Sectors:[/bold yellow]\n"
            for conn in sector_display['connections']:
                # Color code based on connection type
                if conn['type'] == 'federation':
                    type_color = "green"
                    type_symbol = "🟢"
                elif conn['type'] == 'neutral':
                    type_color = "yellow"
                    type_symbol = "🟡"
                elif conn['type'] == 'enemy':
                    type_color = "red"
                    type_symbol = "🔴"
                elif conn['type'] == 'hop':
                    type_color = "cyan"
                    type_symbol = "🔵"
                elif conn['type'] == 'skip':
                    type_color = "magenta"
                    type_symbol = "🟣"
                elif conn['type'] == 'warp':
                    type_color = "blue"
                    type_symbol = "🔷"
                else:
                    type_color = "white"
                    type_symbol = "⚪"
                
                sector_text += f"  {type_symbol} Sector {conn['sector']} ({conn['type'].upper()}) - {conn['faction']}\n"
                sector_text += f"     Fuel: {conn['fuel_cost']}, Time: {conn['travel_time']}min, Danger: {conn['danger_level']}/10\n"
        else:
            sector_text += "[dim]No connected sectors[/dim]\n"
        
        self.console.print(Panel(sector_text, title="TW2002 Navigation", border_style="cyan")) 