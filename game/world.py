"""
World class for LOGDTW2002
Handles locations, navigation, and space travel
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from game.player import Item

@dataclass
class Location:
    """Represents a location in the game world"""
    name: str
    description: str
    location_type: str  # planet, space_station, asteroid, etc.
    coordinates: Tuple[int, int, int]
    connections: List[str] = None
    items: List[Item] = None
    npcs: List[str] = None
    services: List[str] = None  # trading, repair, fuel, etc.
    danger_level: int = 0  # 0-10 scale
    faction: str = "Neutral"
    fuel_cost: int = 0  # Fuel cost to travel here
    travel_time: int = 0  # Travel time in minutes
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.items is None:
            self.items = []
        if self.npcs is None:
            self.npcs = []
        if self.services is None:
            self.services = []

class World:
    """Game world with locations and navigation"""
    
    def __init__(self):
        self.locations = {}
        self.current_location = "Earth Station"
        self.player_coordinates = (0, 0, 0)
        self.space_sector = "Alpha"
        
        # Initialize the game world
        self._create_world()
        
        # Travel state
        self.is_traveling = False
        self.travel_destination = None
        self.travel_progress = 0
        self.travel_time = 0
        self.travel_start_time = 0
        
        # Events and encounters
        self.encounters = []
        self.weather_conditions = "Clear"
        
        # Map data
        self.map_data = self._create_map_data()
        
    def _create_world(self):
        """Create the game world with locations"""
        
        # Create locations
        locations_data = [
            {
                'name': 'Earth Station',
                'description': 'A bustling space station orbiting Earth. The main hub for human space travel.',
                'location_type': 'space_station',
                'coordinates': (0, 0, 0),
                'connections': ['Mars Colony', 'Luna Base'],
                'services': ['trading', 'repair', 'fuel', 'missions'],
                'danger_level': 1,
                'faction': 'Federation',
                'fuel_cost': 0,
                'travel_time': 0
            },
            {
                'name': 'Mars Colony',
                'description': 'A red-dusted mining colony on the surface of Mars. Rich in minerals.',
                'location_type': 'planet',
                'coordinates': (50, 0, 0),
                'connections': ['Earth Station', 'Asteroid Belt'],
                'services': ['trading', 'mining', 'fuel'],
                'danger_level': 3,
                'faction': 'Federation',
                'fuel_cost': 5,
                'travel_time': 30
            },
            {
                'name': 'Luna Base',
                'description': 'A research facility on Earth\'s moon. Home to scientists and explorers.',
                'location_type': 'moon_base',
                'coordinates': (0, 50, 0),
                'connections': ['Earth Station', 'Deep Space Lab'],
                'services': ['research', 'trading', 'fuel'],
                'danger_level': 2,
                'faction': 'Scientists',
                'fuel_cost': 3,
                'travel_time': 20
            },
            {
                'name': 'Asteroid Belt',
                'description': 'A dangerous region filled with asteroids and space debris.',
                'location_type': 'asteroid_field',
                'coordinates': (100, 0, 0),
                'connections': ['Mars Colony', 'Pirate Haven'],
                'services': ['mining'],
                'danger_level': 7,
                'faction': 'Neutral',
                'fuel_cost': 8,
                'travel_time': 45
            },
            {
                'name': 'Pirate Haven',
                'description': 'A lawless space station controlled by pirates and smugglers.',
                'location_type': 'space_station',
                'coordinates': (150, 0, 0),
                'connections': ['Asteroid Belt', 'Outer Rim'],
                'services': ['trading', 'repair', 'missions'],
                'danger_level': 9,
                'faction': 'Pirates',
                'fuel_cost': 10,
                'travel_time': 60
            },
            {
                'name': 'Deep Space Lab',
                'description': 'A remote research station studying cosmic phenomena.',
                'location_type': 'research_station',
                'coordinates': (0, 100, 0),
                'connections': ['Luna Base', 'Nebula Zone'],
                'services': ['research', 'fuel'],
                'danger_level': 4,
                'faction': 'Scientists',
                'fuel_cost': 6,
                'travel_time': 40
            },
            {
                'name': 'Outer Rim',
                'description': 'The edge of known space. Mysterious and dangerous.',
                'location_type': 'deep_space',
                'coordinates': (200, 0, 0),
                'connections': ['Pirate Haven'],
                'services': ['exploration'],
                'danger_level': 10,
                'faction': 'Neutral',
                'fuel_cost': 15,
                'travel_time': 90
            },
            {
                'name': 'Nebula Zone',
                'description': 'A beautiful but treacherous region filled with colorful gas clouds.',
                'location_type': 'nebula',
                'coordinates': (0, 150, 0),
                'connections': ['Deep Space Lab'],
                'services': ['exploration', 'research'],
                'danger_level': 6,
                'faction': 'Neutral',
                'fuel_cost': 12,
                'travel_time': 75
            }
        ]
        
        # Create location objects
        for loc_data in locations_data:
            location = Location(
                name=loc_data['name'],
                description=loc_data['description'],
                location_type=loc_data['location_type'],
                coordinates=loc_data['coordinates'],
                connections=loc_data['connections'],
                services=loc_data['services'],
                danger_level=loc_data['danger_level'],
                faction=loc_data['faction'],
                fuel_cost=loc_data['fuel_cost'],
                travel_time=loc_data['travel_time']
            )
            self.locations[loc_data['name']] = location
        
        # Add some items to locations
        self._add_items_to_locations()
        
    def _create_map_data(self) -> Dict:
        """Create map data for visual representation"""
        return {
            'width': 25,
            'height': 15,
            'locations': {
                'Earth Station': {'x': 12, 'y': 7, 'symbol': '🌍'},
                'Mars Colony': {'x': 18, 'y': 7, 'symbol': '🔴'},
                'Luna Base': {'x': 12, 'y': 3, 'symbol': '🌙'},
                'Asteroid Belt': {'x': 22, 'y': 7, 'symbol': '💎'},
                'Pirate Haven': {'x': 24, 'y': 7, 'symbol': '🏴‍☠️'},
                'Deep Space Lab': {'x': 12, 'y': 1, 'symbol': '🔬'},
                'Outer Rim': {'x': 24, 'y': 5, 'symbol': '⭐'},
                'Nebula Zone': {'x': 12, 'y': 0, 'symbol': '🌌'}
            },
            'connections': [
                ('Earth Station', 'Mars Colony'),
                ('Earth Station', 'Luna Base'),
                ('Mars Colony', 'Asteroid Belt'),
                ('Asteroid Belt', 'Pirate Haven'),
                ('Luna Base', 'Deep Space Lab'),
                ('Deep Space Lab', 'Nebula Zone'),
                ('Pirate Haven', 'Outer Rim')
            ]
        }
        
    def _add_items_to_locations(self):
        """Add items to various locations"""
        
        # Items for different locations
        items_data = {
            'Earth Station': [
                Item("Advanced Med Kit", "High-quality medical supplies", 100, "consumable"),
                Item("Energy Shield", "Personal protective field", 200, "shield", defense=10),
                Item("Federation Badge", "Official identification", 50, "equipment")
            ],
            'Mars Colony': [
                Item("Mining Laser", "Industrial cutting tool", 150, "weapon", damage=25),
                Item("Raw Minerals", "Unprocessed ore", 20, "trade_good"),
                Item("Dust Filter", "Protection from Martian dust", 30, "equipment")
            ],
            'Pirate Haven': [
                Item("Stolen Cargo", "Questionable goods", 300, "trade_good"),
                Item("Pirate Blade", "Deadly melee weapon", 120, "weapon", damage=30),
                Item("Smuggler's Map", "Shows secret routes", 80, "equipment")
            ],
            'Deep Space Lab': [
                Item("Research Data", "Valuable scientific information", 500, "trade_good"),
                Item("Quantum Scanner", "Advanced detection device", 400, "equipment"),
                Item("Experimental Weapon", "Prototype energy weapon", 600, "weapon", damage=40)
            ]
        }
        
        for location_name, items in items_data.items():
            if location_name in self.locations:
                self.locations[location_name].items.extend(items)

    def get_current_location(self) -> Location:
        """Get the current location object"""
        return self.locations.get(self.current_location)

    def get_available_destinations(self) -> List[str]:
        """Get list of available travel destinations"""
        current_loc = self.get_current_location()
        if current_loc:
            return current_loc.connections
        return []

    def can_travel_to(self, destination: str) -> bool:
        """Check if player can travel to destination"""
        current_loc = self.get_current_location()
        if not current_loc:
            return False
        
        return destination in current_loc.connections

    def start_travel(self, destination: str, player) -> Dict:
        """Start traveling to a destination"""
        if not self.can_travel_to(destination):
            return {'success': False, 'message': f'Cannot travel to {destination} from here'}
        
        dest_location = self.locations[destination]
        
        # Check fuel requirements
        if player.fuel < dest_location.fuel_cost:
            return {'success': False, 'message': f'Not enough fuel. Need {dest_location.fuel_cost}, have {player.fuel}'}
        
        # Start travel
        self.is_traveling = True
        self.travel_destination = destination
        self.travel_progress = 0
        self.travel_time = dest_location.travel_time
        self.travel_start_time = time.time()
        
        return {
            'success': True,
            'message': f'Traveling to {destination}. Estimated time: {dest_location.travel_time} minutes',
            'travel_time': dest_location.travel_time,
            'fuel_cost': dest_location.fuel_cost
        }

    def update_travel(self, player) -> Dict:
        """Update travel progress"""
        if not self.is_traveling:
            return {'traveling': False}
        
        elapsed_time = (time.time() - self.travel_start_time) / 60  # Convert to minutes
        progress = min(100, (elapsed_time / self.travel_time) * 100)
        
        if progress >= 100:
            # Arrived at destination
            self._complete_travel(player)
            return {
                'traveling': False,
                'arrived': True,
                'destination': self.travel_destination,
                'message': f'Arrived at {self.travel_destination}!'
            }
        
        return {
            'traveling': True,
            'progress': progress,
            'destination': self.travel_destination,
            'remaining_time': max(0, self.travel_time - elapsed_time)
        }

    def _complete_travel(self, player):
        """Complete travel to destination"""
        dest_location = self.locations[self.travel_destination]
        
        # Consume fuel
        player.use_fuel(dest_location.fuel_cost)
        
        # Update location
        self.current_location = self.travel_destination
        self.player_coordinates = dest_location.coordinates
        
        # Reset travel state
        self.is_traveling = False
        self.travel_destination = None
        self.travel_progress = 0
        self.travel_time = 0

    def travel_to(self, destination: str) -> bool:
        """Travel to a destination (instant travel for compatibility)"""
        if not self.can_travel_to(destination):
            return False
        
        # Calculate travel distance and fuel cost
        current_coords = self.get_current_location().coordinates
        dest_coords = self.locations[destination].coordinates
        
        distance = self._calculate_distance(current_coords, dest_coords)
        fuel_cost = distance // 10  # 1 fuel per 10 distance units
        
        # For now, just move instantly
        # In a full implementation, this would trigger travel mode
        self.current_location = destination
        self.player_coordinates = dest_coords
        
        return True

    def _calculate_distance(self, coords1: Tuple[int, int, int], coords2: Tuple[int, int, int]) -> int:
        """Calculate distance between two coordinate sets"""
        return int(((coords1[0] - coords2[0])**2 + 
                   (coords1[1] - coords2[1])**2 + 
                   (coords1[2] - coords2[2])**2)**0.5)

    def move_player(self, direction: str) -> bool:
        """Move player within current location (for ground-based movement)"""
        # This would be used for movement within a location
        # For now, just return True to indicate movement is possible
        return True

    def get_location_description(self) -> str:
        """Get detailed description of current location"""
        location = self.get_current_location()
        if not location:
            return "Unknown location"
        
        desc = f"\n[bold cyan]{location.name}[/bold cyan]\n"
        desc += f"[italic]{location.description}[/italic]\n\n"
        
        desc += f"Type: {location.location_type.title()}\n"
        desc += f"Danger Level: {location.danger_level}/10\n"
        desc += f"Faction: {location.faction}\n"
        
        if location.services:
            desc += f"Services: {', '.join(location.services)}\n"
        
        if location.connections:
            desc += f"Connections: {', '.join(location.connections)}\n"
        
        if location.items:
            desc += f"Items here: {', '.join([item.name for item in location.items])}\n"
        
        return desc

    def get_map_display(self) -> str:
        """Get a visual map of the game world"""
        map_str = "\n[bold cyan]Space Map[/bold cyan]\n"
        map_str += "=" * 50 + "\n\n"
        
        # Create a simple ASCII map
        map_width = self.map_data['width']
        map_height = self.map_data['height']
        
        # Initialize empty map
        map_grid = [[' ' for _ in range(map_width)] for _ in range(map_height)]
        
        # Add locations
        for loc_name, loc_data in self.map_data['locations'].items():
            x, y = loc_data['x'], loc_data['y']
            if 0 <= x < map_width and 0 <= y < map_height:
                map_grid[y][x] = loc_data['symbol']
        
        # Add connections (simple lines)
        for conn in self.map_data['connections']:
            loc1, loc2 = conn
            if loc1 in self.map_data['locations'] and loc2 in self.map_data['locations']:
                x1, y1 = self.map_data['locations'][loc1]['x'], self.map_data['locations'][loc1]['y']
                x2, y2 = self.map_data['locations'][loc2]['x'], self.map_data['locations'][loc2]['y']
                
                # Draw simple connection line
                if x1 == x2:  # Vertical line
                    for y in range(min(y1, y2) + 1, max(y1, y2)):
                        if 0 <= y < map_height and 0 <= x1 < map_width:
                            map_grid[y][x1] = '|'
                elif y1 == y2:  # Horizontal line
                    for x in range(min(x1, x2) + 1, max(x1, x2)):
                        if 0 <= x < map_width and 0 <= y1 < map_height:
                            map_grid[y1][x] = '-'
        
        # Highlight current location
        current_loc = self.get_current_location()
        if current_loc and current_loc.name in self.map_data['locations']:
            x, y = self.map_data['locations'][current_loc.name]['x'], self.map_data['locations'][current_loc.name]['y']
            if 0 <= x < map_width and 0 <= y < map_height:
                map_grid[y][x] = f"[bold red]{self.map_data['locations'][current_loc.name]['symbol']}[/bold red]"
        
        # Convert grid to string
        for row in map_grid:
            map_str += ''.join(row) + '\n'
        
        map_str += "\n[bold yellow]Legend:[/bold yellow]\n"
        map_str += "🌍 Earth Station    🔴 Mars Colony    🌙 Luna Base\n"
        map_str += "💎 Asteroid Belt    🏴‍☠️ Pirate Haven   🔬 Deep Space Lab\n"
        map_str += "⭐ Outer Rim        🌌 Nebula Zone\n"
        map_str += "[bold red]Current Location[/bold red]\n"
        
        return map_str

    def get_travel_info(self, destination: str) -> Dict:
        """Get travel information for a destination"""
        if not self.can_travel_to(destination):
            return {'available': False}
        
        dest_location = self.locations[destination]
        current_loc = self.get_current_location()
        
        return {
            'available': True,
            'destination': destination,
            'fuel_cost': dest_location.fuel_cost,
            'travel_time': dest_location.travel_time,
            'danger_level': dest_location.danger_level,
            'faction': dest_location.faction,
            'services': dest_location.services
        }

    def can_trade(self) -> bool:
        """Check if trading is available at current location"""
        location = self.get_current_location()
        return location and 'trading' in location.services

    def can_repair(self) -> bool:
        """Check if repair services are available"""
        location = self.get_current_location()
        return location and 'repair' in location.services

    def can_refuel(self) -> bool:
        """Check if fuel services are available"""
        location = self.get_current_location()
        return location and 'fuel' in location.services

    def is_in_combat(self) -> bool:
        """Check if player is currently in combat"""
        # This would be determined by current game state
        return False

    def get_random_encounter(self) -> Optional[str]:
        """Get a random encounter based on current location"""
        location = self.get_current_location()
        if not location:
            return None
        
        # Higher danger level = more likely to have encounters
        if random.random() < location.danger_level / 20:
            encounters = [
                "A group of space pirates approaches!",
                "You detect an unknown ship on your scanners.",
                "A meteor shower threatens your ship!",
                "You encounter a mysterious alien vessel.",
                "Space debris blocks your path.",
                "A distress signal reaches your ship."
            ]
            return random.choice(encounters)
        
        return None

    def get_weather_conditions(self) -> str:
        """Get current weather/space conditions"""
        conditions = [
            "Clear", "Solar Storm", "Asteroid Field", "Nebula Clouds",
            "Radiation Belt", "Magnetic Storm", "Cosmic Winds"
        ]
        return random.choice(conditions)

    def get_sector_info(self) -> Dict:
        """Get information about current space sector"""
        return {
            'name': self.space_sector,
            'coordinates': self.player_coordinates,
            'weather': self.get_weather_conditions(),
            'danger_level': self.get_current_location().danger_level if self.get_current_location() else 0
        }