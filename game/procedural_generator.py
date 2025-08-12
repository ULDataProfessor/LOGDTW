#!/usr/bin/env python3
"""
Procedural Generation System for LOGDTW2002
Creates infinite, dynamic content including sectors, planets, events, and NPCs
"""

import random
import math
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class BiomeType(Enum):
    TEMPERATE = "temperate"
    DESERT = "desert"
    ICE = "ice"
    VOLCANIC = "volcanic"
    TOXIC = "toxic"
    OCEAN = "ocean"
    JUNGLE = "jungle"
    CRYSTAL = "crystal"
    ENERGY = "energy"


class EventType(Enum):
    NONE = "none"
    PIRATE_ATTACK = "pirate_attack"
    MERCHANT_CONVOY = "merchant_convoy"
    DISTRESS_SIGNAL = "distress_signal"
    STELLAR_PHENOMENON = "stellar_phenomenon"
    ANCIENT_ARTIFACT = "ancient_artifact"
    FACTION_PATROL = "faction_patrol"
    ASTEROID_FIELD = "asteroid_field"
    NEBULA = "nebula"
    WORMHOLE = "wormhole"
    DERELICT_SHIP = "derelict_ship"


@dataclass
class ProceduralPlanet:
    name: str
    biome: BiomeType
    size: str  # small, medium, large, massive
    population: int
    tech_level: int
    resources: Dict[str, int]
    atmosphere: str
    gravity: float
    temperature: int
    special_features: List[str]
    trade_goods: List[str]
    faction_control: str


@dataclass
class ProceduralSector:
    id: int
    name: str
    coordinates: Tuple[int, int]
    faction_control: str
    danger_level: int
    planets: List[ProceduralPlanet]
    stations: List[Dict]
    events: List[Dict]
    trade_routes: List[str]
    stellar_objects: List[str]
    warp_gates: List[int]
    resources: Dict[str, int]
    discovery_date: Optional[str]
    # New narrative fields
    narrative_summary: Optional[str] = None
    narrative_hooks: Optional[List[str]] = None


@dataclass
class ProceduralEvent:
    id: str
    type: EventType
    title: str
    description: str
    sector_id: int
    duration: int
    effects: Dict[str, Any]
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    completion_status: str


class ProceduralGenerator:
    def __init__(self, seed: Optional[int] = None):
        """Initialize the procedural generator with optional seed for reproducible results"""
        self.seed = seed or random.randint(1, 1000000)
        random.seed(self.seed)

        # Name generation lists
        self.planet_prefixes = [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Nova",
            "Neo",
            "Prime",
            "Ultra",
            "Meta",
            "Proto",
            "Omega",
            "Sigma",
            "Kepler",
            "Vega",
            "Altair",
            "Rigel",
            "Sirius",
            "Proxima",
            "Centauri",
            "Aurora",
            "Stellar",
            "Cosmic",
            "Quantum",
            "Nexus",
            "Apex",
            "Zenith",
        ]

        self.planet_suffixes = [
            "Prime",
            "Major",
            "Minor",
            "Beta",
            "Station",
            "Outpost",
            "Colony",
            "Haven",
            "Reach",
            "Point",
            "Base",
            "Terminal",
            "Gateway",
            "Nexus",
            "Core",
            "Edge",
            "Frontier",
            "Deep",
            "Far",
            "New",
            "Old",
            "Lost",
        ]

        self.sector_names = [
            "Helix",
            "Vortex",
            "Spiral",
            "Corona",
            "Nebula",
            "Void",
            "Drift",
            "Expanse",
            "Region",
            "Zone",
            "Quadrant",
            "Cluster",
            "Array",
            "Complex",
            "Network",
            "Grid",
            "Matrix",
            "Field",
            "Domain",
            "Realm",
        ]

        # Resource lists
        self.common_resources = [
            "Iron",
            "Copper",
            "Silicon",
            "Carbon",
            "Water",
            "Oxygen",
            "Nitrogen",
        ]

        self.rare_resources = [
            "Tritium",
            "Dilithium",
            "Quantum Crystals",
            "Dark Matter",
            "Antimatter",
            "Neutronium",
            "Tachyons",
            "Zeridium",
            "Ammolite",
            "Unobtainium",
        ]

        self.trade_goods = [
            "Food",
            "Medicine",
            "Textiles",
            "Electronics",
            "Machinery",
            "Weapons",
            "Art",
            "Luxury Goods",
            "Raw Materials",
            "Processed Goods",
            "Energy",
            "Data",
            "Software",
            "Biologicals",
            "Chemicals",
            "Metals",
        ]

        # Faction lists
        self.factions = [
            "Federation",
            "Empire",
            "Republic",
            "Alliance",
            "Consortium",
            "Collective",
            "Syndicate",
            "Corporation",
            "Pirates",
            "Rebels",
            "Neutral",
            "Independent",
            "Mercenaries",
            "Traders",
            "Explorers",
        ]

    def generate_galaxy_sector(
        self, sector_id: int, force_regenerate: bool = False
    ) -> ProceduralSector:
        """Generate a complete sector with planets, stations, and events"""
        # Use sector ID to create consistent seed for this sector
        sector_seed = self.seed + sector_id * 1000
        random.seed(sector_seed)

        # Calculate coordinates based on sector ID
        coords = self._calculate_sector_coordinates(sector_id)

        # Generate sector name
        name = f"{random.choice(self.sector_names)} {sector_id}"

        # Determine faction control based on coordinates
        faction = self._determine_sector_faction(coords)

        # Calculate danger level (higher for outer sectors)
        danger_level = self._calculate_danger_level(coords)

        # Generate planets
        num_planets = random.randint(0, 5)
        planets = []
        for i in range(num_planets):
            planet = self._generate_planet(sector_id, i)
            planets.append(planet)

        # Generate stations
        stations = self._generate_stations(sector_id, faction, len(planets))

        # Generate events
        events = self._generate_sector_events(sector_id, danger_level)

        # Generate trade routes
        trade_routes = self._generate_trade_routes(sector_id, coords)

        # Generate stellar objects
        stellar_objects = self._generate_stellar_objects(coords)

        # Generate warp gates
        warp_gates = self._generate_warp_gates(sector_id, coords)

        # Generate sector resources
        resources = self._generate_sector_resources(coords, danger_level)

        # Reset random seed
        random.seed(self.seed)

        # Build narrative
        narrative_summary, narrative_hooks = self._generate_sector_narrative(
            name, faction, danger_level, planets, stations, events, stellar_objects
        )

        return ProceduralSector(
            id=sector_id,
            name=name,
            coordinates=coords,
            faction_control=faction,
            danger_level=danger_level,
            planets=planets,
            stations=stations,
            events=events,
            trade_routes=trade_routes,
            stellar_objects=stellar_objects,
            warp_gates=warp_gates,
            resources=resources,
            discovery_date=None,
            narrative_summary=narrative_summary,
            narrative_hooks=narrative_hooks,
        )

    def _generate_sector_narrative(
        self,
        name: str,
        faction: str,
        danger: int,
        planets: List["ProceduralPlanet"],
        stations: List[Dict],
        events: List[Dict],
        stellar: List[str],
    ) -> Tuple[str, List[str]]:
        """Create a short narrative and hooks for a sector based on its content."""
        hooks: List[str] = []
        descriptors = []
        if danger >= 4:
            descriptors.append("perilous")
        if "nebula" in [e.get("type") for e in events]:
            descriptors.append("shrouded by ionized mists")
        if any("Wormhole" in s for s in stellar):
            descriptors.append("warped by unstable wormholes")
        if planets:
            populous = sum(1 for p in planets if p.population > 1000000)
            if populous:
                descriptors.append("densely settled")
        if stations:
            descriptors.append("anchored by orbital stations")

        if not descriptors:
            descriptors.append("quiet")

        summary = f"{name} is a {', '.join(descriptors)} sector under {faction} influence."

        # Hooks derived from content
        if danger >= 4:
            hooks.append("Patrols report increasing pirate activity.")
        if any(e.get("type") == "ancient_artifact" for e in events):
            hooks.append("Scans hint at relics from a forgotten civilization.")
        if any("Wormhole" in s for s in stellar):
            hooks.append("Charts mark erratic gravitational lensing—navigation advised.")
        if planets and any(p.biome.name == "CRYSTAL" for p in planets):
            hooks.append("Crystal biomes emit harmonic frequencies—scientists are intrigued.")
        if stations and len(stations) > 1:
            hooks.append("Rival station syndicates vie for commercial dominance.")

        return summary, hooks

    def _calculate_sector_coordinates(self, sector_id: int) -> Tuple[int, int]:
        """Calculate sector coordinates in a spiral pattern"""
        if sector_id == 1:
            return (0, 0)

        # Spiral outward from center
        layer = int(math.ceil((math.sqrt(sector_id) - 1) / 2))
        arm = (sector_id - (2 * layer - 1) ** 2) // (2 * layer)
        position = (sector_id - (2 * layer - 1) ** 2) % (2 * layer)

        if arm == 0:  # Right
            return (layer, -layer + position)
        elif arm == 1:  # Top
            return (layer - position, layer)
        elif arm == 2:  # Left
            return (-layer, layer - position)
        else:  # Bottom
            return (-layer + position, -layer)

    def _determine_sector_faction(self, coords: Tuple[int, int]) -> str:
        """Determine faction control based on coordinates"""
        x, y = coords
        distance = math.sqrt(x * x + y * y)

        if distance <= 2:
            return "Federation"
        elif distance <= 4:
            return random.choice(["Federation", "Republic", "Alliance"])
        elif distance <= 8:
            return random.choice(["Empire", "Consortium", "Independent", "Neutral"])
        else:
            return random.choice(["Pirates", "Rebels", "Independent", "Unknown"])

    def _calculate_danger_level(self, coords: Tuple[int, int]) -> int:
        """Calculate danger level based on distance from center"""
        x, y = coords
        distance = math.sqrt(x * x + y * y)
        base_danger = min(int(distance), 10)
        return max(1, base_danger + random.randint(-2, 3))

    def _generate_planet(self, sector_id: int, planet_index: int) -> ProceduralPlanet:
        """Generate a single planet"""
        # Generate name
        name = f"{random.choice(self.planet_prefixes)} {random.choice(self.planet_suffixes)} {chr(65 + planet_index)}"

        # Select biome
        biome = random.choice(list(BiomeType))

        # Generate size
        size = random.choices(["small", "medium", "large", "massive"], weights=[40, 35, 20, 5])[0]

        # Generate population based on biome and size
        size_multiplier = {"small": 1, "medium": 3, "large": 8, "massive": 20}[size]
        biome_multiplier = {
            BiomeType.TEMPERATE: 5,
            BiomeType.OCEAN: 4,
            BiomeType.JUNGLE: 3,
            BiomeType.DESERT: 2,
            BiomeType.ICE: 1,
            BiomeType.VOLCANIC: 1,
            BiomeType.TOXIC: 0.5,
            BiomeType.CRYSTAL: 1,
            BiomeType.ENERGY: 0.2,
        }[biome]

        population = int(random.randint(1000, 50000) * size_multiplier * biome_multiplier)

        # Tech level (1-10)
        tech_level = max(1, min(10, random.randint(1, 8) + random.randint(-2, 3)))

        # Generate resources based on biome
        resources = self._generate_planet_resources(biome, size)

        # Atmosphere
        atmosphere = self._generate_atmosphere(biome)

        # Gravity (0.5x to 3.0x Earth)
        gravity = round(random.uniform(0.5, 3.0), 1)

        # Temperature (-200 to 500 Celsius)
        temp_ranges = {
            BiomeType.ICE: (-150, -20),
            BiomeType.TEMPERATE: (-10, 40),
            BiomeType.DESERT: (20, 80),
            BiomeType.VOLCANIC: (50, 200),
            BiomeType.TOXIC: (-50, 150),
            BiomeType.OCEAN: (0, 30),
            BiomeType.JUNGLE: (20, 45),
            BiomeType.CRYSTAL: (-100, 100),
            BiomeType.ENERGY: (100, 500),
        }
        temp_range = temp_ranges[biome]
        temperature = random.randint(temp_range[0], temp_range[1])

        # Special features
        special_features = self._generate_special_features(biome, tech_level)

        # Trade goods
        trade_goods = self._generate_planet_trade_goods(biome, tech_level, resources)

        # Faction control
        faction_control = random.choice(self.factions)

        return ProceduralPlanet(
            name=name,
            biome=biome,
            size=size,
            population=population,
            tech_level=tech_level,
            resources=resources,
            atmosphere=atmosphere,
            gravity=gravity,
            temperature=temperature,
            special_features=special_features,
            trade_goods=trade_goods,
            faction_control=faction_control,
        )

    def _generate_planet_resources(self, biome: BiomeType, size: str) -> Dict[str, int]:
        """Generate planet resources based on biome and size"""
        resources = {}
        size_multiplier = {"small": 1, "medium": 2, "large": 4, "massive": 8}[size]

        # Common resources
        for resource in random.sample(self.common_resources, random.randint(2, 5)):
            resources[resource] = random.randint(100, 1000) * size_multiplier

        # Rare resources based on biome
        biome_rares = {
            BiomeType.CRYSTAL: ["Quantum Crystals", "Dilithium"],
            BiomeType.VOLCANIC: ["Tritium", "Neutronium"],
            BiomeType.ENERGY: ["Antimatter", "Tachyons"],
            BiomeType.ICE: ["Dark Matter", "Zeridium"],
            BiomeType.TOXIC: ["Unobtainium", "Ammolite"],
        }

        if biome in biome_rares:
            for rare in biome_rares[biome]:
                if random.random() < 0.3:  # 30% chance
                    resources[rare] = random.randint(10, 100) * size_multiplier

        return resources

    def _generate_atmosphere(self, biome: BiomeType) -> str:
        """Generate planet atmosphere"""
        atmospheres = {
            BiomeType.TEMPERATE: ["Oxygen-Nitrogen", "Nitrogen-Oxygen", "Earth-like"],
            BiomeType.DESERT: ["Thin", "Carbon Dioxide", "Dry"],
            BiomeType.ICE: ["Frozen", "Methane", "Ammonia"],
            BiomeType.VOLCANIC: ["Sulfurous", "Toxic", "Volcanic"],
            BiomeType.TOXIC: ["Poisonous", "Corrosive", "Acidic"],
            BiomeType.OCEAN: ["Humid", "Water Vapor", "Oceanic"],
            BiomeType.JUNGLE: ["Dense", "Oxygen-Rich", "Humid"],
            BiomeType.CRYSTAL: ["Crystalline", "Mineral", "Stable"],
            BiomeType.ENERGY: ["Energized", "Plasma", "Unstable"],
        }
        return random.choice(atmospheres[biome])

    def _generate_special_features(self, biome: BiomeType, tech_level: int) -> List[str]:
        """Generate special planetary features"""
        features = []

        # Biome-specific features
        biome_features = {
            BiomeType.CRYSTAL: ["Crystal Caves", "Resonance Fields", "Living Crystals"],
            BiomeType.VOLCANIC: ["Active Volcanoes", "Lava Tubes", "Geothermal Vents"],
            BiomeType.ENERGY: ["Energy Storms", "Plasma Fields", "Temporal Anomalies"],
            BiomeType.ICE: ["Ice Caverns", "Frozen Seas", "Aurora Phenomena"],
            BiomeType.JUNGLE: ["Ancient Ruins", "Aggressive Flora", "Canopy Cities"],
        }

        if biome in biome_features:
            features.extend(random.sample(biome_features[biome], random.randint(1, 2)))

        # Tech-level features
        if tech_level >= 7:
            tech_features = ["Orbital Platforms", "Planetary Shield", "Space Elevator"]
            features.extend(random.sample(tech_features, random.randint(0, 2)))

        return features

    def _generate_planet_trade_goods(
        self, biome: BiomeType, tech_level: int, resources: Dict[str, int]
    ) -> List[str]:
        """Generate planet trade goods"""
        goods = []

        # Add goods based on resources
        for resource in resources:
            if resource in self.rare_resources:
                goods.append(resource)

        # Add biome-specific goods
        biome_goods = {
            BiomeType.TEMPERATE: ["Food", "Textiles", "Art"],
            BiomeType.DESERT: ["Minerals", "Solar Collectors"],
            BiomeType.ICE: ["Water", "Cryogenics"],
            BiomeType.JUNGLE: ["Biologicals", "Medicine", "Exotic Foods"],
            BiomeType.VOLCANIC: ["Metals", "Geothermal Energy"],
            BiomeType.OCEAN: ["Seafood", "Aquaculture", "Hydrocarbons"],
        }

        if biome in biome_goods:
            goods.extend(random.sample(biome_goods[biome], random.randint(1, 3)))

        # Add tech-based goods
        if tech_level >= 5:
            goods.extend(
                random.sample(["Electronics", "Software", "Machinery"], random.randint(1, 2))
            )
        if tech_level >= 8:
            goods.extend(random.sample(["Advanced Technology", "AI Systems"], random.randint(0, 1)))

        return list(set(goods))  # Remove duplicates

    def _generate_stations(self, sector_id: int, faction: str, num_planets: int) -> List[Dict]:
        """Generate space stations for the sector"""
        stations = []

        # At least one station per sector
        num_stations = max(1, random.randint(0, 3) + (num_planets // 2))

        station_types = [
            "Trade Station",
            "Military Outpost",
            "Research Facility",
            "Mining Platform",
            "Refinery",
            "Shipyard",
            "Observatory",
        ]

        for i in range(num_stations):
            station = {
                "name": f"{faction} {random.choice(station_types)} {sector_id}-{i+1}",
                "type": random.choice(station_types),
                "faction": faction,
                "size": random.choice(["Small", "Medium", "Large"]),
                "services": self._generate_station_services(),
                "population": random.randint(100, 5000),
                "docking_fee": random.randint(10, 100),
            }
            stations.append(station)

        return stations

    def _generate_station_services(self) -> List[str]:
        """Generate services available at a station"""
        all_services = [
            "Trading",
            "Repairs",
            "Fuel",
            "Medical",
            "Equipment",
            "Information",
            "Banking",
            "Entertainment",
            "Security",
        ]
        return random.sample(all_services, random.randint(3, 7))

    def _generate_sector_events(self, sector_id: int, danger_level: int) -> List[Dict]:
        """Generate random events for the sector"""
        events = []

        # Higher danger = more events
        num_events = random.randint(0, danger_level // 2)

        for i in range(num_events):
            event_type = random.choice(list(EventType))
            if event_type == EventType.NONE:
                continue

            event = {
                "id": f"event_{sector_id}_{i}",
                "type": event_type.value,
                "title": self._generate_event_title(event_type),
                "description": self._generate_event_description(event_type),
                "duration": random.randint(1, 10),
                "active": True,
                "discovered": False,
            }
            events.append(event)

        return events

    def _generate_event_title(self, event_type: EventType) -> str:
        """Generate event title"""
        titles = {
            EventType.PIRATE_ATTACK: ["Pirate Raid", "Buccaneer Assault", "Raider Strike"],
            EventType.MERCHANT_CONVOY: ["Trade Convoy", "Merchant Fleet", "Commercial Escort"],
            EventType.DISTRESS_SIGNAL: ["Ship in Distress", "Emergency Beacon", "Mayday Signal"],
            EventType.STELLAR_PHENOMENON: ["Solar Flare", "Cosmic Storm", "Stellar Anomaly"],
            EventType.ANCIENT_ARTIFACT: ["Ancient Relic", "Alien Artifact", "Lost Technology"],
            EventType.DERELICT_SHIP: ["Abandoned Vessel", "Ghost Ship", "Derelict Hulk"],
        }
        return random.choice(titles.get(event_type, ["Unknown Event"]))

    def _generate_event_description(self, event_type: EventType) -> str:
        """Generate event description"""
        descriptions = {
            EventType.PIRATE_ATTACK: "Pirates are actively raiding ships in this sector.",
            EventType.MERCHANT_CONVOY: "A merchant convoy is passing through, offering trade opportunities.",
            EventType.DISTRESS_SIGNAL: "A ship is broadcasting a distress signal.",
            EventType.STELLAR_PHENOMENON: "Unusual stellar activity is affecting the sector.",
            EventType.ANCIENT_ARTIFACT: "An ancient artifact has been detected.",
            EventType.DERELICT_SHIP: "A derelict ship has been found floating in space.",
        }
        return descriptions.get(event_type, "Something interesting is happening here.")

    def _generate_trade_routes(self, sector_id: int, coords: Tuple[int, int]) -> List[str]:
        """Generate trade routes connecting to other sectors"""
        routes = []
        x, y = coords

        # Generate routes to nearby sectors
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                if random.random() < 0.3:  # 30% chance of trade route
                    target_x, target_y = x + dx, y + dy
                    routes.append(f"Trade Route to ({target_x}, {target_y})")

        return routes

    def _generate_stellar_objects(self, coords: Tuple[int, int]) -> List[str]:
        """Generate stellar objects in the sector"""
        objects = []

        # Always has a star
        star_types = [
            "Red Dwarf",
            "Yellow Star",
            "Blue Giant",
            "Red Giant",
            "White Dwarf",
            "Binary System",
        ]
        objects.append(random.choice(star_types))

        # Additional objects
        possible_objects = [
            "Asteroid Belt",
            "Comet",
            "Gas Cloud",
            "Nebula Fragment",
            "Black Hole",
            "Neutron Star",
            "Pulsar",
            "Wormhole",
        ]

        num_objects = random.randint(0, 3)
        objects.extend(random.sample(possible_objects, min(num_objects, len(possible_objects))))

        return objects

    def _generate_warp_gates(self, sector_id: int, coords: Tuple[int, int]) -> List[int]:
        """Generate warp gate connections"""
        gates = []
        x, y = coords

        # Chance of warp gates based on distance from center
        distance = math.sqrt(x * x + y * y)
        gate_chance = max(0.1, 0.5 - (distance * 0.05))

        if random.random() < gate_chance:
            # Connect to 1-3 distant sectors
            num_gates = random.randint(1, 3)
            for _ in range(num_gates):
                # Random distant sector
                target_sector = random.randint(sector_id + 10, sector_id + 100)
                gates.append(target_sector)

        return gates

    def _generate_sector_resources(
        self, coords: Tuple[int, int], danger_level: int
    ) -> Dict[str, int]:
        """Generate sector-wide resources"""
        resources = {}

        # More dangerous sectors have rarer resources
        if danger_level >= 7:
            for rare in random.sample(self.rare_resources, random.randint(1, 3)):
                resources[rare] = random.randint(50, 500)

        # Common sector resources
        for common in random.sample(self.common_resources, random.randint(2, 4)):
            resources[common] = random.randint(100, 1000)

        return resources

    def generate_dynamic_event(
        self, sector_id: int, player_actions: Dict
    ) -> Optional[ProceduralEvent]:
        """Generate a dynamic event based on player actions and sector state"""
        event_chance = 0.1  # Base 10% chance

        # Increase chance based on player activity
        if player_actions.get("combat_victories", 0) > 5:
            event_chance += 0.05
        if player_actions.get("trade_volume", 0) > 10000:
            event_chance += 0.03
        if player_actions.get("exploration_count", 0) > 10:
            event_chance += 0.02

        if random.random() > event_chance:
            return None

        # Select event type based on player actions
        event_type = self._select_dynamic_event_type(player_actions)

        return ProceduralEvent(
            id=f"dynamic_{sector_id}_{random.randint(1000, 9999)}",
            type=event_type,
            title=self._generate_event_title(event_type),
            description=self._generate_event_description(event_type),
            sector_id=sector_id,
            duration=random.randint(5, 20),
            effects=self._generate_event_effects(event_type),
            requirements=self._generate_event_requirements(event_type),
            rewards=self._generate_event_rewards(event_type),
            completion_status="active",
        )

    def _select_dynamic_event_type(self, player_actions: Dict) -> EventType:
        """Select event type based on player behavior"""
        if player_actions.get("combat_victories", 0) > 10:
            return random.choice([EventType.PIRATE_ATTACK, EventType.FACTION_PATROL])
        elif player_actions.get("trade_volume", 0) > 20000:
            return random.choice([EventType.MERCHANT_CONVOY, EventType.ANCIENT_ARTIFACT])
        else:
            return random.choice(list(EventType))

    def _generate_event_effects(self, event_type: EventType) -> Dict[str, Any]:
        """Generate event effects"""
        effects = {}

        if event_type == EventType.PIRATE_ATTACK:
            effects = {"danger_increase": 2, "trade_disruption": True}
        elif event_type == EventType.MERCHANT_CONVOY:
            effects = {"trade_bonus": 1.5, "rare_goods": True}
        elif event_type == EventType.STELLAR_PHENOMENON:
            effects = {"navigation_hazard": True, "sensor_interference": True}

        return effects

    def _generate_event_requirements(self, event_type: EventType) -> Dict[str, Any]:
        """Generate event requirements"""
        requirements = {}

        if event_type == EventType.ANCIENT_ARTIFACT:
            requirements = {"science_skill": 5, "exploration_gear": True}
        elif event_type == EventType.PIRATE_ATTACK:
            requirements = {"combat_skill": 3, "weapons": True}

        return requirements

    def _generate_event_rewards(self, event_type: EventType) -> Dict[str, Any]:
        """Generate event rewards"""
        rewards = {}

        if event_type == EventType.ANCIENT_ARTIFACT:
            rewards = {"credits": random.randint(5000, 15000), "rare_item": True}
        elif event_type == EventType.MERCHANT_CONVOY:
            rewards = {"trade_discount": 0.2, "reputation": 100}
        elif event_type == EventType.DISTRESS_SIGNAL:
            rewards = {"credits": random.randint(1000, 5000), "reputation": 50}

        return rewards

    def get_sector_discovery_info(self, sector_id: int) -> Dict[str, Any]:
        """Get information about discovering a new sector"""
        sector = self.generate_galaxy_sector(sector_id)

        discovery_info = {
            "sector_id": sector_id,
            "name": sector.name,
            "faction": sector.faction_control,
            "danger_level": sector.danger_level,
            "planet_count": len(sector.planets),
            "station_count": len(sector.stations),
            "notable_features": [],
            "first_impression": "",
        }

        # Notable features
        if sector.warp_gates:
            discovery_info["notable_features"].append("Warp Gates Detected")
        if sector.danger_level >= 8:
            discovery_info["notable_features"].append("High Danger Zone")
        if len(sector.planets) >= 4:
            discovery_info["notable_features"].append("Rich Planetary System")

        # First impression
        impressions = [
            "A bustling sector filled with activity.",
            "A quiet, remote area of space.",
            "Warning signs of recent conflict detected.",
            "Rich with natural resources and opportunities.",
            "An unexplored frontier waiting to be discovered.",
        ]
        discovery_info["first_impression"] = random.choice(impressions)

        return discovery_info
