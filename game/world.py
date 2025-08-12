"""
World class for LOGDTW2002
Handles locations, navigation, and space travel
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from game.player import Item
from game.sos_system import SOSSystem
from .sector_db import SectorRepository

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
    sector: int = 1  # Sector number (TW2002 style)
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.items is None:
            self.items = []
        if self.npcs is None:
            self.npcs = []
        if self.services is None:
            self.services = []

@dataclass
class SectorConnection:
    """Represents a connection between sectors with TW2002-style types"""
    destination_sector: int
    connection_type: str  # "neutral", "federation", "enemy", "hop", "skip", "warp"
    fuel_cost: int
    travel_time: int
    danger_level: int = 0

class PlanetSurface:
    """Represents a planetary surface for ground movement"""
    def __init__(self, name, width=5, height=5):
        self.name = name
        self.width = width
        self.height = height
        terrain_types = ['plains', 'forest', 'mountain', 'desert']
        sample_items = [
            Item("Herb Bundle", "Medicinal herbs", 5, "resource"),
            Item("Ancient Relic", "A mysterious artifact", 100, "quest")
        ]
        sample_npcs = ["Trader", "Explorer", "Scientist"]
        self.grid = []
        for y in range(height):
            row = []
            for x in range(width):
                tile = {
                    'desc': f'Area ({x},{y})',
                    'terrain': random.choice(terrain_types),
                    'items': [random.choice(sample_items)] if random.random() < 0.1 else [],
                    'npcs': [random.choice(sample_npcs)] if random.random() < 0.1 else [],
                    'resource': random.choice([None, 'ore', 'crystals', 'herbs', None]),
                    'encounter': random.choice([None, 'alien_raider', None, 'space_pirate', None]),
                    'explored': False
                }
                row.append(tile)
            self.grid.append(row)
        self.player_pos = (width // 2, height // 2)  # Start in the center
        self.grid[self.player_pos[1]][self.player_pos[0]]['explored'] = True

    def move(self, direction):
        x, y = self.player_pos
        if direction == 'north' and y > 0:
            y -= 1
        elif direction == 'south' and y < self.height - 1:
            y += 1
        elif direction == 'west' and x > 0:
            x -= 1
        elif direction == 'east' and x < self.width - 1:
            x += 1
        else:
            return {'moved': False, 'events': []}  # Can't move

        self.player_pos = (x, y)
        tile = self.grid[y][x]
        tile['explored'] = True

        events = []
        if tile.get('encounter'):
            events.append({'type': 'combat', 'enemy_type': tile['encounter']})
            tile['encounter'] = None
        if tile.get('items'):
            events.append({'type': 'item', 'items': tile['items']})
        if tile.get('npcs'):
            events.append({'type': 'npc', 'npcs': tile['npcs']})
        if tile.get('resource'):
            events.append({'type': 'resource', 'resource': tile['resource']})

        return {'moved': True, 'events': events}

    def get_adjacent(self):
        x, y = self.player_pos
        adj = {}
        if y > 0:
            adj['north'] = (x, y-1)
        if y < self.height - 1:
            adj['south'] = (x, y+1)
        if x > 0:
            adj['west'] = (x-1, y)
        if x < self.width - 1:
            adj['east'] = (x+1, y)
        return adj

    def get_current_area(self):
        x, y = self.player_pos
        return self.grid[y][x]

    def get_map(self):
        map_str = "\n[bold cyan]Planetary Surface Map[/bold cyan]\n"
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                if (x, y) == self.player_pos:
                    row += '[bold red]X[/bold red]'
                else:
                    tile = self.grid[y][x]
                    row += '.' if tile.get('explored') else '?'
            map_str += row + '\n'
        map_str += "Legend: [bold red]X[/bold red]=Player, .=Explored, ?=Unexplored\n"
        return map_str

class World:
    """Game world with locations and navigation - TW2002 style"""

    def __init__(self, event_engine=None, max_sectors: int = 10_000, db_path: str = None):
        """Create a new world.

        Parameters
        ----------
        event_engine : Optional[EventEngine]
            If provided, travel actions will notify the event engine so it can
            generate encounters or other dynamic events.  The parameter is
            optional to maintain backwards compatibility with existing tests
            and demos that instantiate ``World`` without an event system.
        """

        # Event engine hook
        self.event_engine = event_engine

        self.locations = {}
        self.current_location = "Earth Station"
        self.player_coordinates = (0, 0, 0)
        self.current_sector = 1  # Current sector number
        self.sector_names = {1: "Alpha", 2: "Beta", 3: "Gamma", 4: "Delta", 5: "Epsilon"}
        self.discovered_sectors = {"Alpha"}  # Track discovered sectors by name
        self.sector_connections = {}  # Sector connections with types
        self.sector_factions = {}  # Faction control of sectors
        self.traveling = False
        self.travel_destination = None
        self.travel_progress = 0
        self.travel_start_time = 0
        self.on_planet_surface = False
        self.planet_surface = None
        
        # Sector persistence
        self.max_sectors = max_sectors
        default_db = os.path.join(os.path.expanduser('~'), '.logdtw2002', 'sectors.db')
        self.sector_repo = SectorRepository(db_path or default_db)

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

        # Events
        self.event_templates = self._create_event_templates()
        self.market_conditions = {}
        self.sos_system = SOSSystem()

        self.on_planet_surface = False
        self.planet_surface = None

        # Ensure first 10 sectors exist as Federation space; others generated on demand
        self._ensure_initial_sectors()

    # ------------------------------------------------------------------
    # Sector generation and persistence
    # ------------------------------------------------------------------
    def _ensure_initial_sectors(self) -> None:
        import random
        # Pre-create sectors 1..10 as Federation
        for sid in range(1, 11):
            if not self.sector_repo.get_sector(sid):
                rec = {
                    'id': sid,
                    'name': self.sector_names.get(sid, f'Sector {sid}') if hasattr(self, 'sector_names') else f'Sector {sid}',
                    'faction': 'Federation',
                    'region': 'Federation',
                    'danger_level': random.randint(1, 3),
                    'has_market': 1,
                    'has_outpost': 1 if sid in (1, 2, 3) else 0,
                    'has_station': 1,
                    'has_research': 1 if sid in (3, 6) else 0,
                    'has_mining': 1 if sid in (2, 4) else 0,
                    'connections': [],
                    'explored': 1 if sid == 1 else 0,
                    'charted': 1 if sid == 1 else 0,
                }
                self.sector_repo.upsert_sector(rec)
        # Simple spine connections 1-2-3-...-10
        for sid in range(1, 10):
            self.sector_repo.add_bidirectional_connection(sid, sid + 1)

    def _generate_sector_record(self, sector_id: int) -> Dict:
        import random
        region = 'Nebula'
        name = f'Nebula {sector_id}'
        faction = random.choice(['Neutral', 'Scientists', 'Traders', 'Pirates'])
        danger = random.randint(2, 9)
        rec = {
            'id': sector_id,
            'name': name,
            'faction': faction,
            'region': region,
            'danger_level': danger,
            'has_market': 1 if random.random() < 0.35 else 0,
            'has_outpost': 1 if random.random() < 0.25 else 0,
            'has_station': 1 if random.random() < 0.2 else 0,
            'has_research': 1 if random.random() < 0.15 else 0,
            'has_mining': 1 if random.random() < 0.3 else 0,
            'connections': [],
            'explored': 0,
            'charted': 0,
        }
        return rec

    def get_or_create_sector(self, sector_id: int) -> Dict:
        if sector_id < 1 or sector_id > self.max_sectors:
            raise ValueError('Sector out of bounds')
        rec = self.sector_repo.get_sector(sector_id)
        if rec:
            return rec
        # Create
        rec = self._generate_sector_record(sector_id)
        self.sector_repo.upsert_sector(rec)
        # Connect interestingly: random 2-4 links to near ids
        import random
        num_links = random.randint(2, 4)
        candidates = [i for i in range(max(1, sector_id - 7), min(self.max_sectors, sector_id + 7)) if i != sector_id]
        random.shuffle(candidates)
        for target in candidates[:num_links]:
            self.sector_repo.add_bidirectional_connection(sector_id, target)
        return self.sector_repo.get_sector(sector_id) or rec

    def mark_sector_explored(self, sector_id: int) -> None:
        self.sector_repo.mark_explored(sector_id)

    def mark_sector_charted(self, sector_id: int) -> None:
        self.sector_repo.mark_charted(sector_id)
        
    def _create_world(self):
        """Create the game world with TW2002-style numbered sectors"""
        
        # Create locations with numbered sectors
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
                'travel_time': 0,
                'sector': 1
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
                'travel_time': 30,
                'sector': 2
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
                'travel_time': 20,
                'sector': 3
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
                'travel_time': 45,
                'sector': 4
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
                'travel_time': 60,
                'sector': 5
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
                'travel_time': 40,
                'sector': 6
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
                'travel_time': 90,
                'sector': 7
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
                'travel_time': 75,
                'sector': 8
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
                travel_time=loc_data['travel_time'],
                sector=loc_data['sector']
            )
            self.locations[loc_data['name']] = location
        
        # Set up sector factions
        self.sector_factions = {
            1: "Federation",    # Earth Station
            2: "Federation",    # Mars Colony
            3: "Scientists",    # Luna Base
            4: "Neutral",       # Asteroid Belt
            5: "Pirates",       # Pirate Haven
            6: "Scientists",    # Deep Space Lab
            7: "Neutral",       # Outer Rim
            8: "Neutral"        # Nebula Zone
        }
        
        # Create TW2002-style sector connections
        self._create_sector_connections()
        
        # Add some items to locations
        self._add_items_to_locations()
    
    def _create_sector_connections(self):
        """Create TW2002-style sector connections with different types"""
        # Initialize sector connections dictionary
        self.sector_connections = {}
        
        # Define connections between sectors with types
        connections_data = [
            # From Sector 1 (Earth Station)
            (1, 2, "federation", 5, 30),   # Earth to Mars - Federation space
            (1, 3, "federation", 3, 20),   # Earth to Luna - Federation space
            
            # From Sector 2 (Mars Colony)
            (2, 1, "federation", 5, 30),   # Mars to Earth - Federation space
            (2, 4, "neutral", 8, 45),      # Mars to Asteroid Belt - Neutral space
            
            # From Sector 3 (Luna Base)
            (3, 1, "federation", 3, 20),   # Luna to Earth - Federation space
            (3, 6, "hop", 6, 40),          # Luna to Deep Space Lab - Hop connection
            
            # From Sector 4 (Asteroid Belt)
            (4, 2, "neutral", 8, 45),      # Asteroid Belt to Mars - Neutral space
            (4, 5, "enemy", 10, 60),       # Asteroid Belt to Pirate Haven - Enemy space
            
            # From Sector 5 (Pirate Haven)
            (5, 4, "enemy", 10, 60),       # Pirate Haven to Asteroid Belt - Enemy space
            (5, 7, "skip", 15, 90),        # Pirate Haven to Outer Rim - Skip connection
            
            # From Sector 6 (Deep Space Lab)
            (6, 3, "hop", 6, 40),          # Deep Space Lab to Luna - Hop connection
            (6, 8, "warp", 12, 75),        # Deep Space Lab to Nebula Zone - Warp connection
            
            # From Sector 7 (Outer Rim)
            (7, 5, "skip", 15, 90),        # Outer Rim to Pirate Haven - Skip connection
            
            # From Sector 8 (Nebula Zone)
            (8, 6, "warp", 12, 75),        # Nebula Zone to Deep Space Lab - Warp connection
        ]
        
        # Create sector connections
        for source_sector, dest_sector, conn_type, fuel_cost, travel_time in connections_data:
            if source_sector not in self.sector_connections:
                self.sector_connections[source_sector] = []
            
            connection = SectorConnection(
                destination_sector=dest_sector,
                connection_type=conn_type,
                fuel_cost=fuel_cost,
                travel_time=travel_time,
                danger_level=self._get_connection_danger(conn_type)
            )
            self.sector_connections[source_sector].append(connection)
    
    def _get_connection_danger(self, connection_type: str) -> int:
        """Get danger level based on connection type"""
        danger_levels = {
            "federation": 1,
            "neutral": 3,
            "enemy": 8,
            "hop": 2,
            "skip": 6,
            "warp": 4
        }
        return danger_levels.get(connection_type, 5)
        
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

    def _create_event_templates(self) -> List[Dict]:
        """Create templates for random sector events"""
        return [
            {
                'name': 'Pirate Ambush',
                'type': 'pirate',
                'description': 'A band of pirates emerges from the shadows.',
                'danger_min': 5,
                'danger_max': 10
            },
            {
                'name': 'Distress Call',
                'type': 'distress',
                'description': 'A faint distress signal is picked up by your sensors.',
                'danger_min': 2,
                'danger_max': 10
            },
            {
                'name': 'Trading Opportunity',
                'type': 'trade',
                'description': 'Roaming merchants offer goods at competitive prices.',
                'danger_min': 0,
                'danger_max': 6
            }
        ]
        
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

    def _sector_name(self, number: int) -> str:
        names = {1: "Alpha", 2: "Beta", 3: "Gamma", 4: "Delta"}
        return names.get(number, f"Sector {number}")

    def can_jump_to(self, destination: str) -> bool:
        """Check if player can jump to a destination by name"""
        if destination not in self.locations:
            return False
        sector = self.locations[destination].sector
        return self.can_jump_to_sector(sector)

    def get_available_jumps(self) -> List[Dict]:
        """Get available sector jumps from current sector (TW2002 style)"""
        if self.current_sector not in self.sector_connections:
            return []
        
        available_jumps = []
        for connection in self.sector_connections[self.current_sector]:
            # Check if destination sector has any locations
            sector_locations = [loc for loc in self.locations.values() if loc.sector == connection.destination_sector]
            if sector_locations:
                available_jumps.append({
                    'sector': connection.destination_sector,
                    'type': connection.connection_type,
                    'fuel_cost': connection.fuel_cost,
                    'travel_time': connection.travel_time,
                    'danger_level': connection.danger_level,
                    'faction': self.sector_factions.get(connection.destination_sector, "Unknown")
                })
        
        return available_jumps

    def can_jump_to_sector(self, sector_number: int) -> bool:
        """Check if player can jump to sector number"""
        if self.current_sector not in self.sector_connections:
            return False

        for connection in self.sector_connections[self.current_sector]:
            if connection.destination_sector == sector_number:
                return True
        return False

    def can_jump_to(self, destination: str) -> bool:
        """Check if a location name is valid for instant jumps"""
        return destination in self.locations

    def jump_to_sector(self, sector_number: int, player) -> Dict:
        """Jump to a connected sector (TW2002 style)"""
        if not self.can_jump_to_sector(sector_number):
            return {'success': False, 'message': f'Cannot jump to sector {sector_number} from here'}
        
        # Find the connection details
        connection = None
        for conn in self.sector_connections[self.current_sector]:
            if conn.destination_sector == sector_number:
                connection = conn
                break
        
        if not connection:
            return {'success': False, 'message': f'No connection to sector {sector_number}'}
        
        # Check fuel requirements
        if player.fuel < connection.fuel_cost:
            return {'success': False, 'message': f'Not enough fuel. Need {connection.fuel_cost}, have {player.fuel}'}
        
        # Find a location in the destination sector
        sector_locations = [loc for loc in self.locations.values() if loc.sector == sector_number]
        if not sector_locations:
            return {'success': False, 'message': f'No locations found in sector {sector_number}'}
        
        dest_location = sector_locations[0]  # Use first location in sector
        
        # Start jump
        self.is_traveling = True
        self.travel_destination = dest_location.name
        self.travel_progress = 0
        self.travel_time = connection.travel_time
        self.travel_start_time = time.time()
        
        # Discover and persist the sector
        self.discovered_sectors.add(self.sector_names.get(sector_number, str(sector_number)))
        try:
            self.get_or_create_sector(sector_number)
            self.mark_sector_explored(sector_number)
        except Exception:
            pass
        
        return {
            'success': True,
            'message': f'Jumping to sector {sector_number} ({connection.connection_type} space). Estimated time: {connection.travel_time} minutes',
            'travel_time': connection.travel_time,
            'fuel_cost': connection.fuel_cost,
            'sector': sector_number,
            'connection_type': connection.connection_type
        }

    def start_travel(self, destination: str, player) -> Dict:
        """Begin travel using a destination name"""
        if destination not in self.locations:
            return {'success': False, 'message': f'Unknown destination {destination}'}
        dest_sector = self.locations[destination].sector
        return self.jump_to_sector(dest_sector, player)

    def update_jump(self, player) -> Dict:
        """Update jump progress"""
        if not self.is_traveling:
            return {'traveling': False}
        
        elapsed_time = (time.time() - self.travel_start_time) / 60  # Convert to minutes
        progress = min(100, (elapsed_time / self.travel_time) * 100)
        
        if progress >= 100:
            # Arrived at destination
            self._complete_jump(player)
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

    def update_travel(self, player) -> Dict:
        """Update travel and trigger events on arrival"""
        status = self.update_jump(player)
        if status.get('arrived'):
            event = self.trigger_event(player)
            if event:
                status['event'] = event
        return status

    def _complete_jump(self, player):
        """Complete jump to destination"""
        dest_location = self.locations[self.travel_destination]
        
        # Find the connection used for this jump
        connection = None
        for conn in self.sector_connections.get(self.current_sector, []):
            if conn.destination_sector == dest_location.sector:
                connection = conn
                break
        
        # Consume fuel
        if connection:
            player.use_fuel(connection.fuel_cost)
        else:
            player.use_fuel(dest_location.fuel_cost)
        
        # Update location and sector
        self.current_location = self.travel_destination
        self.player_coordinates = dest_location.coordinates
        self.current_sector = dest_location.sector
        # Mark charted in DB on arrival
        try:
            self.mark_sector_charted(self.current_sector)
        except Exception:
            pass
        
        # Reset travel state
        self.is_traveling = False
        self.travel_destination = None
        self.travel_progress = 0
        self.travel_time = 0

    def trigger_event(self, player) -> Optional[Dict]:
        """Trigger a random event based on sector danger level"""
        location = self.get_current_location()
        if not location:
            return None

        danger = location.danger_level
        possible = [e for e in self.event_templates if e['danger_min'] <= danger <= e['danger_max']]

        # 30% chance an event occurs
        if not possible or random.random() > 0.3:
            return None

        event = random.choice(possible)
        outcome = ""

        if event['type'] == 'pirate':
            damage = random.randint(5, 15)
            player.health = max(0, player.health - damage)
            location.danger_level = min(10, location.danger_level + 1)
            outcome = f'Pirates attack your ship, dealing {damage} damage.'
        elif event['type'] == 'distress':
            signal = self.sos_system.generate_distress_signal(self.player_coordinates)
            if signal:
                outcome = f'Received distress call from {signal.ship_name} at {signal.coordinates}.'
            else:
                outcome = 'A distress call was detected but quickly faded.'
        elif event['type'] == 'trade':
            credits = random.randint(50, 150)
            player.credits += credits
            self.market_conditions[location.sector] = 'boom'
            outcome = f'Profitable trade nets {credits} credits.'

        result = {
            'name': event['name'],
            'description': event['description'],
            'outcome': outcome
        }

        try:
            from utils.display import DisplayManager
            DisplayManager().show_event_result(result)
        except Exception:
            pass

        return result

    def instant_jump(self, destination: str) -> bool:
        """Instant jump to a destination (for warp command)"""
        if not self.can_jump_to(destination):
            return False
        
        dest_location = self.locations[destination]
        
        # Update location and sector
        self.current_location = destination
        self.player_coordinates = dest_location.coordinates
        self.space_sector = dest_location.sector

        # Discover the sector
        self.discovered_sectors.add(self.sector_names.get(dest_location.sector, str(dest_location.sector)))
        
        return True

    def get_current_sector_display(self) -> Dict:
        """Get current sector information for TW2002-style display"""
        current_loc = self.get_current_location()
        if not current_loc:
            return {'error': 'No current location'}
        
        sector_number = self.current_sector
        faction = self.sector_factions.get(sector_number, "Unknown")
        
        # Get available connections
        available_connections = self.get_available_jumps()
        
        return {
            'sector': sector_number,
            'location': current_loc.name,
            'faction': faction,
            'connections': available_connections,
            'discovered': sector_number in self.discovered_sectors
        }
    
    def get_sector_info(self, sector_number: int = None) -> Dict:
        """Get information about a sector"""
        if sector_number is None:
            # Return current sector info
            sector_number = self.current_sector
        
        sector_locations = [loc for loc in self.locations.values() if loc.sector == sector_number]
        
        if not sector_locations:
            return {'discovered': False, 'sector': sector_number}
        
        return {
            'discovered': sector_number in self.discovered_sectors,
            'sector': sector_number,
            'locations': [loc.name for loc in sector_locations],
            'danger_level': max(loc.danger_level for loc in sector_locations),
            'faction': self.sector_factions.get(sector_number, "Unknown")
        }

    def get_all_sectors(self) -> List[str]:
        """Get all sectors in the game"""
        return list(set(loc.sector for loc in self.locations.values()))

    def get_discovered_sectors(self) -> List[str]:
        """Get discovered sectors"""
        return list(self.discovered_sectors)

    def get_location_description(self) -> str:
        """Get detailed description of current location"""
        location = self.get_current_location()
        if not location:
            return "Unknown location"
        
        desc = f"\n[bold cyan]{location.name}[/bold cyan] - Sector {location.sector}[/bold cyan]\n"
        desc += f"[italic]{location.description}[/italic]\n\n"
        
        desc += f"Type: {location.location_type.title()}\n"
        desc += f"Sector: {location.sector}\n"
        desc += f"Danger Level: {location.danger_level}/10\n"
        desc += f"Faction: {location.faction}\n"
        
        if location.services:
            desc += f"Services: {', '.join(location.services)}\n"
        
        if location.connections:
            desc += f"Connected Sectors: {', '.join(location.connections)}\n"
        
        if location.items:
            desc += f"Items here: {', '.join([item.name for item in location.items])}\n"
        
        return desc

    def get_map_display(self) -> str:
        """Get a visual map of the game world with sectors"""
        map_str = "\n[bold cyan]Galactic Map - Sector Navigation[/bold cyan]\n"
        map_str += "=" * 60 + "\n\n"
        
        # Show current sector
        current_loc = self.get_current_location()
        if current_loc:
            map_str += f"[bold yellow]Current Sector: {current_loc.sector}[/bold yellow]\n"
            map_str += f"[bold yellow]Current Location: {current_loc.name}[/bold yellow]\n\n"
        
        # Show all sectors
        all_sectors = self.get_all_sectors()
        discovered_sectors = self.get_discovered_sectors()
        
        map_str += "[bold cyan]Sectors:[/bold cyan]\n"
        for sector in all_sectors:
            if sector in discovered_sectors:
                sector_info = self.get_sector_info(sector)
                map_str += f"  [green]✓ {sector}[/green] - {', '.join(sector_info['locations'])}\n"
            else:
                map_str += f"  [dim]? Unknown Sector[/dim]\n"
        
        map_str += "\n[bold cyan]Sector Connections:[/bold cyan]\n"
        
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
        map_str += "[green]✓ Discovered Sectors[/green]\n"
        map_str += "[dim]? Undiscovered Sectors[/dim]\n"
        
        return map_str

    def get_jump_info(self, destination: str) -> Dict:
        """Get jump information for a destination"""
        if not self.can_jump_to(destination):
            return {'available': False}
        
        dest_location = self.locations[destination]
        current_loc = self.get_current_location()
        
        return {
            'available': True,
            'destination': destination,
            'sector': dest_location.sector,
            'fuel_cost': dest_location.fuel_cost,
            'travel_time': dest_location.travel_time,
            'danger_level': dest_location.danger_level,
            'faction': dest_location.faction,
            'services': dest_location.services
        }

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def can_jump_to(self, destination: str) -> bool:
        """Determine whether a jump to the given destination is possible."""
        if destination not in self.locations:
            return False
        current_loc = self.get_current_location()
        if not current_loc:
            return False
        return destination in current_loc.connections

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
        current_loc = self.get_current_location()
        return {
            'name': current_loc.sector if current_loc else "Unknown",
            'coordinates': self.player_coordinates,
            'weather': self.get_weather_conditions(),
            'danger_level': current_loc.danger_level if current_loc else 0
        }

    def land_on_planet(self):
        """Land on a planet and enter surface mode if possible"""
        location = self.get_current_location()
        if location and location.location_type == 'planet':
            self.on_planet_surface = True
            self.planet_surface = PlanetSurface(location.name)
            return {'success': True, 'message': f'You have landed on {location.name}. Use n/s/e/w to move.'}
        return {'success': False, 'message': 'You can only land on planets.'}

    def leave_planet_surface(self):
        """Leave the planetary surface and return to orbit"""
        if self.on_planet_surface:
            self.on_planet_surface = False
            self.planet_surface = None
            return {'success': True, 'message': 'You have returned to orbit.'}
        return {'success': False, 'message': 'You are not on a planetary surface.'}

    def move_on_surface(self, direction):
        if self.on_planet_surface and self.planet_surface:
            return self.planet_surface.move(direction)
        return {'moved': False, 'events': []}

    def get_surface_adjacent(self):
        if self.on_planet_surface and self.planet_surface:
            return self.planet_surface.get_adjacent()
        return {}

    def get_surface_area(self):
        if self.on_planet_surface and self.planet_surface:
            return self.planet_surface.get_current_area()
        return None

    def get_surface_map(self):
        if self.on_planet_surface and self.planet_surface:
            return self.planet_surface.get_map()
        return ''

    def collect_surface_item(self, player, item_name):
        if self.on_planet_surface and self.planet_surface:
            tile = self.planet_surface.get_current_area()
            for item in list(tile.get('items', [])):
                if item.name.lower() == item_name.lower():
                    if player.add_item(item):
                        tile['items'].remove(item)
                        return {'success': True, 'message': f'Collected {item.name}.'}
                    else:
                        return {'success': False, 'message': 'Inventory full.'}
            return {'success': False, 'message': 'Item not found here.'}
        return {'success': False, 'message': 'You are not on a planetary surface.'}

    def talk_to_surface_npc(self, npc_name):
        if self.on_planet_surface and self.planet_surface:
            tile = self.planet_surface.get_current_area()
            for npc in tile.get('npcs', []):
                if npc.lower() == npc_name.lower():
                    return {'success': True, 'message': f'You talk to {npc}.'}
            return {'success': False, 'message': 'No such NPC here.'}
        return {'success': False, 'message': 'You are not on a planetary surface.'}

    def collect_surface_resource(self, player):
        if self.on_planet_surface and self.planet_surface:
            tile = self.planet_surface.get_current_area()
            resource = tile.get('resource')
            if resource:
                item = Item(name=resource.title(), description=f'{resource} gathered from surface', value=10, item_type='resource')
                if player.add_item(item):
                    tile['resource'] = None
                    return {'success': True, 'message': f'Gathered {resource}.'}
                else:
                    return {'success': False, 'message': 'Inventory full.'}
            return {'success': False, 'message': 'No resource node here.'}
        return {'success': False, 'message': 'You are not on a planetary surface.'}

    def is_on_planet_surface(self):
        return self.on_planet_surface

    def fire_genesis_torpedo(self, player):
        """Create a new planet in the current sector using the Genesis Torpedo"""
        # Check if player has the torpedo
        if not player.has_item('Genesis Torpedo'):
            return {'success': False, 'message': 'You do not have a Genesis Torpedo.'}
        
        # Get current sector
        current_loc = self.get_current_location()
        if not current_loc:
            return {'success': False, 'message': 'Unknown location.'}
        sector = current_loc.sector
        
        # Generate a unique planet name
        base_names = ['Eden', 'Genesis', 'Nova', 'Gaia', 'Aurora', 'Haven', 'Prometheus', 'Arcadia']
        suffix = random.randint(100, 999)
        planet_name = f"{random.choice(base_names)}-{suffix}"
        
        # Create the new planet location
        new_planet = Location(
            name=planet_name,
            description="A lush, newly-formed world teeming with potential.",
            location_type='planet',
            coordinates=(random.randint(0, 200), random.randint(0, 200), 0),
            connections=[current_loc.name],
            services=['trading', 'exploration', 'research'],
            danger_level=random.randint(1, 4),
            faction='Neutral',
            fuel_cost=7,
            travel_time=35,
            sector=sector
        )
        self.locations[planet_name] = new_planet
        # Connect current location to new planet
        if planet_name not in current_loc.connections:
            current_loc.connections.append(planet_name)
        if current_loc.name not in new_planet.connections:
            new_planet.connections.append(current_loc.name)
        
        # Remove the torpedo from inventory
        player.remove_item('Genesis Torpedo')
        
        return {
            'success': True,
            'message': f'Genesis Torpedo fired! A new planet, {planet_name}, has formed in sector {sector}.',
            'planet': planet_name
        }