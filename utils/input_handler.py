"""
Input handler for LOGDTW2002
Handles player input and command processing
"""

import re
from typing import List, Dict, Optional, Tuple
from rich.prompt import Prompt
from rich.console import Console

class InputHandler:
    """Handles player input and command processing"""
    
    def __init__(self):
        self.console = Console()
        self.command_history = []
        self.max_history = 50
        
        # Define available commands
        self.commands = {
            # Movement commands
            'movement': ['north', 'south', 'east', 'west', 'n', 's', 'e', 'w', 'up', 'down', 'in', 'out'],
            
            # Action commands
            'actions': ['look', 'examine', 'search', 'take', 'drop', 'use', 'inventory', 'inv', 'i'],
            
            # Combat commands
            'combat': ['attack', 'defend', 'flee', 'use'],
            
            # Space travel commands
            'travel': ['travel', 'land', 'takeoff', 'scan', 'navigate'],
            
            # Trading commands
            'trading': ['buy', 'sell', 'trade', 'market'],
            
            # System commands
            'system': ['status', 'stats', 's', 'save', 'load', 'quit', 'exit', 'q', 'help', 'h'],
            
            # Special commands
            'special': ['quests', 'missions', 'skills', 'abilities', 'equipment', 'ship']
        }
        
        # Command aliases
        self.aliases = {
            'n': 'north',
            's': 'south',
            'e': 'east',
            'w': 'west',
            'inv': 'inventory',
            'i': 'inventory',
            'h': 'help',
            'q': 'quit',
            'exit': 'quit'
        }
    
    def get_input(self, prompt: str = "> ") -> str:
        """Get input from the player"""
        try:
            command = Prompt.ask(prompt).strip()
            
            # Add to history
            if command:
                self.command_history.append(command)
                if len(self.command_history) > self.max_history:
                    self.command_history.pop(0)
            
            return command
        except KeyboardInterrupt:
            return "quit"
        except EOFError:
            return "quit"
    
    def parse_command(self, command: str) -> Tuple[str, List[str]]:
        """Parse a command into action and arguments"""
        if not command:
            return "", []
        
        # Split command into parts
        parts = command.split()
        if not parts:
            return "", []
        
        action = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Resolve aliases
        if action in self.aliases:
            action = self.aliases[action]
        
        return action, args
    
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions based on partial input"""
        if not partial_command:
            return []
        
        suggestions = []
        partial_lower = partial_command.lower()
        
        # Check all command categories
        for category, commands in self.commands.items():
            for cmd in commands:
                if cmd.startswith(partial_lower):
                    suggestions.append(cmd)
        
        # Check aliases
        for alias, full_command in self.aliases.items():
            if alias.startswith(partial_lower):
                suggestions.append(f"{alias} ({full_command})")
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def validate_command(self, action: str, args: List[str]) -> Dict:
        """Validate a command and return validation result"""
        result = {
            'valid': True,
            'action': action,
            'args': args,
            'message': '',
            'suggestions': []
        }
        
        # Check if action is recognized
        all_commands = []
        for commands in self.commands.values():
            all_commands.extend(commands)
        
        if action not in all_commands:
            result['valid'] = False
            result['message'] = f"Unknown command: {action}"
            result['suggestions'] = self.get_command_suggestions(action)
            return result
        
        # Validate specific commands
        if action in ['buy', 'sell'] and not args:
            result['valid'] = False
            result['message'] = f"Usage: {action} [item_name] [quantity]"
            return result
        
        if action == 'travel' and not args:
            result['valid'] = False
            result['message'] = "Usage: travel [destination]"
            return result
        
        if action == 'use' and not args:
            result['valid'] = False
            result['message'] = "Usage: use [item_name]"
            return result
        
        return result
    
    def get_help_for_command(self, command: str) -> str:
        """Get help text for a specific command"""
        help_texts = {
            'north': 'Move north (also: n)',
            'south': 'Move south (also: s)',
            'east': 'Move east (also: e)',
            'west': 'Move west (also: w)',
            'look': 'Examine your surroundings',
            'inventory': 'Show your inventory (also: inv, i)',
            'status': 'Show your status (also: stats, s)',
            'attack': 'Attack an enemy',
            'defend': 'Take defensive stance',
            'flee': 'Attempt to flee from combat',
            'travel': 'Travel to another location',
            'buy': 'Buy an item from the market',
            'sell': 'Sell an item to the market',
            'quests': 'Show available quests',
            'help': 'Show this help (also: h)',
            'quit': 'Exit the game (also: q, exit)'
        }
        
        return help_texts.get(command, f"No help available for '{command}'")
    
    def show_command_help(self, category: str = None):
        """Show help for commands"""
        if category and category in self.commands:
            commands = self.commands[category]
            self.console.print(f"\n[bold yellow]{category.title()} Commands:[/bold yellow]")
            for cmd in commands:
                help_text = self.get_help_for_command(cmd)
                self.console.print(f"  {cmd}: {help_text}")
        else:
            self.console.print("\n[bold cyan]Available Commands:[/bold cyan]")
            for category, commands in self.commands.items():
                self.console.print(f"\n[bold yellow]{category.title()}:[/bold yellow]")
                for cmd in commands[:5]:  # Show first 5 commands per category
                    help_text = self.get_help_for_command(cmd)
                    self.console.print(f"  {cmd}: {help_text}")
                if len(commands) > 5:
                    self.console.print(f"  ... and {len(commands) - 5} more")
    
    def get_command_history(self, limit: int = 10) -> List[str]:
        """Get recent command history"""
        return self.command_history[-limit:] if self.command_history else []
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
    
    def suggest_command(self, context: str = None) -> List[str]:
        """Suggest commands based on context"""
        suggestions = []
        
        if context == 'combat':
            suggestions = self.commands['combat']
        elif context == 'trading':
            suggestions = self.commands['trading']
        elif context == 'movement':
            suggestions = self.commands['movement']
        elif context == 'exploration':
            suggestions = self.commands['actions'] + self.commands['travel']
        else:
            # General suggestions
            suggestions = []
            for commands in self.commands.values():
                suggestions.extend(commands[:3])  # Top 3 from each category
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def format_command(self, command: str) -> str:
        """Format a command for display"""
        # Add syntax highlighting for common patterns
        formatted = command
        
        # Highlight movement commands
        movement_pattern = r'\b(north|south|east|west|n|s|e|w)\b'
        formatted = re.sub(movement_pattern, r'[cyan]\1[/cyan]', formatted)
        
        # Highlight action commands
        action_pattern = r'\b(look|inventory|status|attack|travel|buy|sell)\b'
        formatted = re.sub(action_pattern, r'[yellow]\1[/yellow]', formatted)
        
        # Highlight system commands
        system_pattern = r'\b(help|quit|save|load)\b'
        formatted = re.sub(system_pattern, r'[red]\1[/red]', formatted)
        
        return formatted
    
    def get_autocomplete_options(self, partial: str) -> List[str]:
        """Get autocomplete options for partial input"""
        if not partial:
            return []
        
        options = []
        partial_lower = partial.lower()
        
        # Check all commands
        for category, commands in self.commands.items():
            for cmd in commands:
                if cmd.startswith(partial_lower):
                    options.append(cmd)
        
        # Check aliases
        for alias in self.aliases:
            if alias.startswith(partial_lower):
                options.append(alias)
        
        return sorted(list(set(options)))[:5]  # Remove duplicates and limit
    
    def process_input(self, raw_input: str) -> Dict:
        """Process raw input and return structured result"""
        action, args = self.parse_command(raw_input)
        validation = self.validate_command(action, args)
        
        return {
            'raw_input': raw_input,
            'action': action,
            'args': args,
            'valid': validation['valid'],
            'message': validation['message'],
            'suggestions': validation['suggestions']
        } 