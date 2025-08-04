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
    
    def show_location(self, location: Location):
        """Display current location information"""
        if not location:
            return
        
        # Create location panel
        location_text = f"[bold cyan]{location.name}[/bold cyan]\n"
        location_text += f"[italic]{location.description}[/italic]\n\n"
        
        # Add location details
        details = []
        details.append(f"Type: {location.location_type.title()}")
        details.append(f"Danger Level: {location.danger_level}/10")
        details.append(f"Faction: {location.faction}")
        
        if location.services:
            details.append(f"Services: {', '.join(location.services)}")
        
        if location.connections:
            details.append(f"Connections: {', '.join(location.connections)}")
        
        location_text += "\n".join(details)
        
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
    
    def show_location_description(self, location: Location):
        """Show detailed location description"""
        if not location:
            return
        
        desc_text = f"[bold cyan]{location.name}[/bold cyan]\n"
        desc_text += f"[italic]{location.description}[/italic]\n\n"
        
        desc_text += f"Type: {location.location_type.title()}\n"
        desc_text += f"Danger Level: {location.danger_level}/10\n"
        desc_text += f"Faction: {location.faction}\n"
        
        if location.services:
            desc_text += f"\n[bold yellow]Services:[/bold yellow]\n"
            for service in location.services:
                desc_text += f"  • {service.title()}\n"
        
        if location.connections:
            desc_text += f"\n[bold yellow]Connections:[/bold yellow]\n"
            for connection in location.connections:
                desc_text += f"  • {connection}\n"
        
        if location.items:
            desc_text += f"\n[bold yellow]Items Here:[/bold yellow]\n"
            for item in location.items:
                desc_text += f"  • {item.name} ({item.value} credits)\n"
        
        self.console.print(Panel(desc_text, title="Location Details", border_style="blue"))
    
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
        market_text += f"Price Modifier: {market_data['price_modifier']:.1f}x\n\n"
        
        market_text += "[bold yellow]Available Goods:[/bold yellow]\n"
        for good in market_data['goods']:
            market_text += f"  • {good['name']}: {good['price']} credits\n"
            market_text += f"    {good['description']}\n"
        
        self.console.print(Panel(market_text, title="Market", border_style="green"))
    
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

[bold yellow]Trading:[/bold yellow]
• buy [item], sell [item]
• trade, market

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