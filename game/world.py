"""
World class for LOGDTW2002
Handles locations, navigation, and space travel
"""

import random
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
        
        # Events and encounters
        self.encounters = []
        self.weather_conditions = "Clear"
        
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
                'faction': 'Federation'
            },
            {
                'name': 'Mars Colony',
                'description': 'A red-dusted mining colony on the surface of Mars. Rich in minerals.',
                'location_type': 'planet',
                'coordinates': (50, 0, 0),
                'connections': ['Earth Station', 'Asteroid Belt'],
                'services': ['trading', 'mining', 'fuel'],
                'danger_level': 3,
                'faction': 'Federation'
            },
            {
                'name': 'Luna Base',
                'description': 'A research facility on Earth\'s moon. Home to scientists and explorers.',
                'location_type': 'moon_base',
                'coordinates': (0, 50, 0),
                'connections': ['Earth Station', 'Deep Space Lab'],
                'services': ['research', 'trading', 'fuel'],
                'danger_level': 2,
                'faction': 'Scientists'
            },
            {
                'name': 'Asteroid Belt',
                'description': 'A dangerous region filled with asteroids and space debris.',
                'location_type': 'asteroid_field',
                'coordinates': (100, 0, 0),
                'connections': ['Mars Colony', 'Pirate Haven'],
                'services': ['mining'],
                'danger_level': 7,
                'faction': 'Neutral'
            },
            {
                'name': 'Pirate Haven',
                'description': 'A lawless space station controlled by pirates and smugglers.',
                'location_type': 'space_station',
                'coordinates': (150, 0, 0),
                'connections': ['Asteroid Belt', 'Outer Rim'],
                'services': ['trading', 'repair', 'missions'],
                'danger_level': 9,
                'faction': 'Pirates'
            },
            {
                'name': 'Deep Space Lab',
                'description': 'A remote research station studying cosmic phenomena.',
                'location_type': 'research_station',
                'coordinates': (0, 100, 0),
                'connections': ['Luna Base', 'Nebula Zone'],
                'services': ['research', 'fuel'],
                'danger_level': 4,
                'faction': 'Scientists'
            },
            {
                'name': 'Outer Rim',
                'description': 'The edge of known space. Mysterious and dangerous.',
                'location_type': 'deep_space',
                'coordinates': (200, 0, 0),
                'connections': ['Pirate Haven'],
                'services': ['exploration'],
                'danger_level': 10,
                'faction': 'Neutral'
            },
            {
                'name': 'Nebula Zone',
                'description': 'A beautiful but treacherous region filled with colorful gas clouds.',
                'location_type': 'nebula',
                'coordinates': (0, 150, 0),
                'connections': ['Deep Space Lab'],
                'services': ['exploration', 'research'],
                'danger_level': 6,
                'faction': 'Neutral'
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
                faction=loc_data['faction']
            )
            self.locations[loc_data['name']] = location
        
        # Add some items to locations
        self._add_items_to_locations()
        
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

    def travel_to(self, destination: str) -> bool:
        """Travel to a destination"""
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