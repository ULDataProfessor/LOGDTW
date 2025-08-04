"""
World Generator for LOGDTW2002
Creates new sectors and procedurally generated content
"""

import random
import string
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from game.player import Item

@dataclass
class Sector:
    """Represents a sector in the galaxy"""
    name: str
    coordinates: Tuple[int, int, int]
    sector_type: str  # core, frontier, dangerous, unexplored
    difficulty: int  # 1-10 scale
    discovered: bool = False
    colonized: bool = False
    warp_ports: List[str] = None
    trade_ports: List[str] = None
    space_stations: List[str] = None
    
    def __post_init__(self):
        if self.warp_ports is None:
            self.warp_ports = []
        if self.trade_ports is None:
            self.trade_ports = []
        if self.space_stations is None:
            self.space_stations = []

class WorldGenerator:
    """Generates new sectors and content"""
    
    def __init__(self):
        self.sectors = {}
        self.sector_names = self._load_sector_names()
        self.planet_types = self._load_planet_types()
        self.station_types = self._load_station_types()
        
    def _load_sector_names(self) -> List[str]:
        """Load sector name templates"""
        return [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
            "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
            "Nova", "Pulsar", "Quasar", "Nebula", "Void", "Rift", "Cluster",
            "Sector", "Zone", "Realm", "Domain", "Territory", "Province"
        ]
    
    def _load_planet_types(self) -> List[str]:
        """Load planet type templates"""
        return [
            "Desert", "Ice", "Jungle", "Ocean", "Volcanic", "Toxic", "Gas Giant",
            "Rocky", "Temperate", "Arctic", "Tropical", "Barren", "Fertile",
            "Mountainous", "Swamp", "Crystalline", "Metallic", "Organic"
        ]
    
    def _load_station_types(self) -> List[str]:
        """Load station type templates"""
        return [
            "Trading Post", "Military Base", "Research Station", "Mining Colony",
            "Refueling Station", "Repair Yard", "Shipyard", "Diplomatic Center",
            "Pirate Haven", "Smuggler's Den", "Tourist Resort", "Medical Center",
            "Educational Facility", "Entertainment Complex", "Industrial Hub"
        ]
    
    def generate_sector(self, coordinates: Tuple[int, int, int]) -> Sector:
        """Generate a new sector at given coordinates"""
        sector_name = self._generate_sector_name()
        sector_type = self._determine_sector_type(coordinates)
        difficulty = self._calculate_difficulty(coordinates, sector_type)
        
        sector = Sector(
            name=sector_name,
            coordinates=coordinates,
            sector_type=sector_type,
            difficulty=difficulty
        )
        
        # Generate content for the sector
        self._generate_sector_content(sector)
        
        return sector
    
    def _generate_sector_name(self) -> str:
        """Generate a unique sector name"""
        prefix = random.choice(self.sector_names)
        suffix = random.choice(self.sector_names)
        number = random.randint(1, 999)
        
        return f"{prefix}-{suffix} {number}"
    
    def _determine_sector_type(self, coordinates: Tuple[int, int, int]) -> str:
        """Determine sector type based on coordinates"""
        x, y, z = coordinates
        distance_from_center = (x**2 + y**2 + z**2)**0.5
        
        if distance_from_center < 50:
            return "core"
        elif distance_from_center < 150:
            return "frontier"
        elif distance_from_center < 300:
            return "dangerous"
        else:
            return "unexplored"
    
    def _calculate_difficulty(self, coordinates: Tuple[int, int, int], sector_type: str) -> int:
        """Calculate sector difficulty"""
        x, y, z = coordinates
        distance_from_center = (x**2 + y**2 + z**2)**0.5
        
        base_difficulty = min(10, max(1, int(distance_from_center / 30)))
        
        # Adjust based on sector type
        if sector_type == "core":
            base_difficulty = max(1, base_difficulty - 2)
        elif sector_type == "frontier":
            base_difficulty = base_difficulty
        elif sector_type == "dangerous":
            base_difficulty = min(10, base_difficulty + 2)
        elif sector_type == "unexplored":
            base_difficulty = min(10, base_difficulty + 3)
        
        return base_difficulty
    
    def _generate_sector_content(self, sector: Sector):
        """Generate content for a sector"""
        # Generate warp ports
        num_warp_ports = random.randint(1, 3)
        for i in range(num_warp_ports):
            port_name = f"Warp Port {chr(65 + i)}"
            sector.warp_ports.append(port_name)
        
        # Generate trade ports
        num_trade_ports = random.randint(0, 2)
        for i in range(num_trade_ports):
            port_name = f"Trade Port {chr(65 + i)}"
            sector.trade_ports.append(port_name)
        
        # Generate space stations
        num_stations = random.randint(1, 4)
        for i in range(num_stations):
            station_type = random.choice(self.station_types)
            station_name = f"{station_type} {chr(65 + i)}"
            sector.space_stations.append(station_name)
    
    def generate_planet(self, sector: Sector) -> Dict:
        """Generate a planet in a sector"""
        planet_type = random.choice(self.planet_types)
        planet_name = self._generate_planet_name()
        
        # Determine planet characteristics
        habitability = random.randint(1, 10)
        resources = random.randint(1, 10)
        population = random.randint(0, 1000000)
        
        # Determine colonization status
        colonized = random.random() < 0.3 and sector.sector_type in ["core", "frontier"]
        
        return {
            'name': planet_name,
            'type': planet_type,
            'habitability': habitability,
            'resources': resources,
            'population': population,
            'colonized': colonized,
            'sector': sector.name
        }
    
    def _generate_planet_name(self) -> str:
        """Generate a planet name"""
        prefixes = ["New", "Old", "Great", "Little", "Big", "Small", "Alpha", "Beta"]
        suffixes = ["World", "Earth", "Planet", "Prime", "Home", "Base", "Station"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(1, 999)
        
        return f"{prefix} {suffix} {number}"
    
    def generate_station(self, sector: Sector) -> Dict:
        """Generate a space station"""
        station_type = random.choice(self.station_types)
        station_name = self._generate_station_name()
        
        # Determine station characteristics
        size = random.choice(["Small", "Medium", "Large", "Massive"])
        services = self._generate_station_services(station_type)
        
        return {
            'name': station_name,
            'type': station_type,
            'size': size,
            'services': services,
            'sector': sector.name
        }
    
    def _generate_station_name(self) -> str:
        """Generate a station name"""
        prefixes = ["Deep", "High", "Low", "Central", "Outer", "Inner", "Alpha", "Beta"]
        suffixes = ["Station", "Base", "Hub", "Center", "Port", "Yard", "Complex"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(1, 999)
        
        return f"{prefix} {suffix} {number}"
    
    def _generate_station_services(self, station_type: str) -> List[str]:
        """Generate services based on station type"""
        base_services = ["fuel", "repair"]
        
        if "Trading" in station_type:
            base_services.append("trading")
        if "Military" in station_type:
            base_services.append("combat")
        if "Research" in station_type:
            base_services.append("research")
        if "Mining" in station_type:
            base_services.append("mining")
        if "Medical" in station_type:
            base_services.append("medical")
        if "Shipyard" in station_type:
            base_services.append("shipyard")
        if "Entertainment" in station_type:
            base_services.append("entertainment")
        
        return base_services
    
    def get_nearby_sectors(self, current_coords: Tuple[int, int, int], radius: int = 100) -> List[Sector]:
        """Get sectors within a certain radius"""
        nearby = []
        
        for x in range(current_coords[0] - radius, current_coords[0] + radius + 1, 50):
            for y in range(current_coords[1] - radius, current_coords[1] + radius + 1, 50):
                for z in range(current_coords[2] - radius, current_coords[2] + radius + 1, 50):
                    coords = (x, y, z)
                    if coords not in self.sectors:
                        sector = self.generate_sector(coords)
                        self.sectors[coords] = sector
                    nearby.append(self.sectors[coords])
        
        return nearby
    
    def discover_sector(self, coordinates: Tuple[int, int, int]) -> Sector:
        """Discover a new sector"""
        if coordinates not in self.sectors:
            sector = self.generate_sector(coordinates)
            self.sectors[coordinates] = sector
            sector.discovered = True
        else:
            sector = self.sectors[coordinates]
            sector.discovered = True
        
        return sector 