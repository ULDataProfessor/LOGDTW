#!/usr/bin/env python3
"""
Dynamic Markets System for LOGDTW2002
More realistic trading economy with supply/demand, market fluctuations, and economic events
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

class MarketCondition(Enum):
    DEPRESSION = "depression"
    RECESSION = "recession"
    STABLE = "stable"
    GROWTH = "growth"
    BOOM = "boom"

class EconomicEvent(Enum):
    NONE = "none"
    WAR = "war"
    PEACE_TREATY = "peace_treaty"
    DISCOVERY = "discovery"
    DISASTER = "disaster"
    TRADE_EMBARGO = "trade_embargo"
    TECHNOLOGICAL_BREAKTHROUGH = "technological_breakthrough"
    RESOURCE_SHORTAGE = "resource_shortage"
    BUMPER_HARVEST = "bumper_harvest"
    PIRATE_RAIDS = "pirate_raids"
    FACTION_ALLIANCE = "faction_alliance"

class CommodityCategory(Enum):
    FOOD = "food"
    MINERALS = "minerals"
    TECHNOLOGY = "technology"
    WEAPONS = "weapons"
    MEDICINE = "medicine"
    LUXURY = "luxury"
    ENERGY = "energy"
    CHEMICALS = "chemicals"

@dataclass
class MarketData:
    base_price: float
    current_price: float
    supply: int
    demand: int
    volatility: float
    trend: float  # -1 to 1, negative = falling, positive = rising
    category: CommodityCategory
    production_cost: float
    seasonal_factor: float = 1.0
    event_modifier: float = 1.0

@dataclass
class EconomicEventData:
    event_type: EconomicEvent
    affected_commodities: List[str]
    price_modifiers: Dict[str, float]
    supply_modifiers: Dict[str, float]
    demand_modifiers: Dict[str, float]
    duration: int  # in game turns
    description: str
    start_turn: int
    sector_id: Optional[int] = None  # None = galaxy-wide

@dataclass
class SectorEconomy:
    sector_id: int
    wealth_level: float  # 0.1 to 2.0, affects all prices
    population: int
    industrial_capacity: float
    specializations: List[str]  # What this sector produces well
    imports: List[str]  # What this sector needs
    exports: List[str]  # What this sector sells
    trade_routes: List[int]  # Connected sectors
    market_condition: MarketCondition
    stability: float  # 0.0 to 1.0, affects price volatility
    corruption_level: float  # 0.0 to 1.0, affects trade efficiency

class DynamicMarketSystem:
    """Advanced market simulation with realistic economic behaviors"""
    
    def __init__(self):
        self.commodities = {}
        self.sector_economies = {}
        self.active_events = []
        self.historical_prices = {}
        self.trade_volumes = {}
        self.market_cycles = {}
        self.current_turn = 0
        
        # Economic parameters
        self.inflation_rate = 0.02  # 2% per year base inflation
        self.market_volatility = 0.1
        self.seasonal_amplitude = 0.15
        self.event_probability = 0.05  # 5% chance per turn
        
        # Initialize markets
        self._initialize_commodities()
        self._initialize_economic_events()
        
    def _initialize_commodities(self):
        """Initialize base commodity data"""
        commodity_data = {
            # Food
            "Food": {"base_price": 50, "volatility": 0.2, "category": CommodityCategory.FOOD, "cost": 30},
            "Grain": {"base_price": 30, "volatility": 0.25, "category": CommodityCategory.FOOD, "cost": 20},
            "Protein": {"base_price": 80, "volatility": 0.3, "category": CommodityCategory.FOOD, "cost": 50},
            "Spices": {"base_price": 200, "volatility": 0.4, "category": CommodityCategory.LUXURY, "cost": 120},
            
            # Minerals
            "Iron": {"base_price": 100, "volatility": 0.15, "category": CommodityCategory.MINERALS, "cost": 70},
            "Copper": {"base_price": 150, "volatility": 0.2, "category": CommodityCategory.MINERALS, "cost": 100},
            "Gold": {"base_price": 1000, "volatility": 0.3, "category": CommodityCategory.LUXURY, "cost": 800},
            "Tritium": {"base_price": 5000, "volatility": 0.5, "category": CommodityCategory.ENERGY, "cost": 3500},
            "Dilithium": {"base_price": 8000, "volatility": 0.6, "category": CommodityCategory.ENERGY, "cost": 6000},
            "Ammolite": {"base_price": 12000, "volatility": 0.7, "category": CommodityCategory.LUXURY, "cost": 9000},
            
            # Technology
            "Electronics": {"base_price": 300, "volatility": 0.25, "category": CommodityCategory.TECHNOLOGY, "cost": 200},
            "Software": {"base_price": 500, "volatility": 0.3, "category": CommodityCategory.TECHNOLOGY, "cost": 300},
            "AI Cores": {"base_price": 10000, "volatility": 0.8, "category": CommodityCategory.TECHNOLOGY, "cost": 7500},
            
            # Weapons
            "Weapons": {"base_price": 800, "volatility": 0.4, "category": CommodityCategory.WEAPONS, "cost": 600},
            "Military Hardware": {"base_price": 2000, "volatility": 0.5, "category": CommodityCategory.WEAPONS, "cost": 1500},
            
            # Medicine
            "Medicine": {"base_price": 400, "volatility": 0.3, "category": CommodityCategory.MEDICINE, "cost": 250},
            "Medical Equipment": {"base_price": 1500, "volatility": 0.35, "category": CommodityCategory.MEDICINE, "cost": 1000},
            
            # Energy
            "Energy Cells": {"base_price": 250, "volatility": 0.2, "category": CommodityCategory.ENERGY, "cost": 180},
            "Fuel": {"base_price": 75, "volatility": 0.3, "category": CommodityCategory.ENERGY, "cost": 50},
            
            # Chemicals
            "Chemicals": {"base_price": 180, "volatility": 0.25, "category": CommodityCategory.CHEMICALS, "cost": 120},
            "Rare Compounds": {"base_price": 3000, "volatility": 0.6, "category": CommodityCategory.CHEMICALS, "cost": 2200}
        }
        
        for name, data in commodity_data.items():
            self.commodities[name] = MarketData(
                base_price=data["base_price"],
                current_price=data["base_price"] * random.uniform(0.8, 1.2),
                supply=random.randint(100, 1000),
                demand=random.randint(100, 1000),
                volatility=data["volatility"],
                trend=random.uniform(-0.1, 0.1),
                category=data["category"],
                production_cost=data["cost"]
            )
            
            # Initialize price history
            self.historical_prices[name] = [self.commodities[name].current_price]
            self.trade_volumes[name] = []
    
    def _initialize_economic_events(self):
        """Initialize possible economic events"""
        self.economic_event_templates = {
            EconomicEvent.WAR: {
                "affected_commodities": ["Weapons", "Military Hardware", "Medicine", "Food"],
                "price_modifiers": {"Weapons": 1.8, "Military Hardware": 2.0, "Medicine": 1.5, "Food": 1.3},
                "supply_modifiers": {"Weapons": 0.7, "Medicine": 0.8, "Food": 0.9},
                "demand_modifiers": {"Weapons": 2.0, "Military Hardware": 2.5, "Medicine": 1.5},
                "duration": (10, 30),
                "description": "Galactic conflict disrupts trade routes and increases demand for military supplies"
            },
            
            EconomicEvent.TECHNOLOGICAL_BREAKTHROUGH: {
                "affected_commodities": ["AI Cores", "Electronics", "Software"],
                "price_modifiers": {"AI Cores": 0.6, "Electronics": 0.8, "Software": 0.7},
                "supply_modifiers": {"AI Cores": 1.5, "Electronics": 1.3, "Software": 1.4},
                "demand_modifiers": {"AI Cores": 1.2, "Electronics": 1.1, "Software": 1.2},
                "duration": (15, 25),
                "description": "Major technological breakthrough revolutionizes production methods"
            },
            
            EconomicEvent.RESOURCE_SHORTAGE: {
                "affected_commodities": ["Tritium", "Dilithium", "Rare Compounds"],
                "price_modifiers": {"Tritium": 2.5, "Dilithium": 3.0, "Rare Compounds": 2.2},
                "supply_modifiers": {"Tritium": 0.3, "Dilithium": 0.2, "Rare Compounds": 0.4},
                "demand_modifiers": {"Tritium": 1.5, "Dilithium": 1.8, "Rare Compounds": 1.3},
                "duration": (20, 40),
                "description": "Critical resource shortage affects multiple sectors"
            },
            
            EconomicEvent.BUMPER_HARVEST: {
                "affected_commodities": ["Food", "Grain", "Protein"],
                "price_modifiers": {"Food": 0.5, "Grain": 0.4, "Protein": 0.6},
                "supply_modifiers": {"Food": 2.0, "Grain": 2.5, "Protein": 1.8},
                "demand_modifiers": {"Food": 0.8, "Grain": 0.7, "Protein": 0.9},
                "duration": (8, 15),
                "description": "Exceptional harvests flood the market with agricultural products"
            },
            
            EconomicEvent.PIRATE_RAIDS: {
                "affected_commodities": ["Weapons", "Fuel", "Medicine"],
                "price_modifiers": {"Weapons": 1.4, "Fuel": 1.6, "Medicine": 1.3},
                "supply_modifiers": {"Weapons": 0.8, "Fuel": 0.7, "Medicine": 0.9},
                "demand_modifiers": {"Weapons": 1.3, "Fuel": 1.2, "Medicine": 1.1},
                "duration": (5, 15),
                "description": "Increased pirate activity disrupts shipping lanes"
            },
            
            EconomicEvent.DISCOVERY: {
                "affected_commodities": ["Gold", "Ammolite", "Rare Compounds"],
                "price_modifiers": {"Gold": 0.7, "Ammolite": 0.8, "Rare Compounds": 0.6},
                "supply_modifiers": {"Gold": 1.8, "Ammolite": 1.5, "Rare Compounds": 2.0},
                "demand_modifiers": {"Gold": 1.1, "Ammolite": 1.2, "Rare Compounds": 1.3},
                "duration": (12, 25),
                "description": "Major resource discovery floods the market with rare materials"
            }
        }
    
    def initialize_sector_economy(self, sector_id: int, **kwargs) -> SectorEconomy:
        """Initialize economy for a new sector"""
        
        # Generate or use provided economic parameters
        wealth_level = kwargs.get('wealth_level', random.uniform(0.5, 1.5))
        population = kwargs.get('population', random.randint(10000, 10000000))
        industrial_capacity = kwargs.get('industrial_capacity', random.uniform(0.1, 2.0))
        
        # Determine specializations based on sector characteristics
        all_specializations = [
            "Mining", "Agriculture", "Manufacturing", "Technology", "Trade",
            "Military", "Research", "Tourism", "Energy", "Pharmaceuticals"
        ]
        
        num_specializations = random.randint(1, 3)
        specializations = random.sample(all_specializations, num_specializations)
        
        # Determine imports/exports based on specializations
        imports, exports = self._determine_trade_goods(specializations)
        
        # Market condition based on wealth and stability
        conditions = list(MarketCondition)
        if wealth_level > 1.2:
            market_condition = random.choice([MarketCondition.GROWTH, MarketCondition.BOOM])
        elif wealth_level < 0.8:
            market_condition = random.choice([MarketCondition.RECESSION, MarketCondition.DEPRESSION])
        else:
            market_condition = MarketCondition.STABLE
        
        economy = SectorEconomy(
            sector_id=sector_id,
            wealth_level=wealth_level,
            population=population,
            industrial_capacity=industrial_capacity,
            specializations=specializations,
            imports=imports,
            exports=exports,
            trade_routes=kwargs.get('trade_routes', []),
            market_condition=market_condition,
            stability=kwargs.get('stability', random.uniform(0.3, 0.9)),
            corruption_level=kwargs.get('corruption_level', random.uniform(0.0, 0.3))
        )
        
        self.sector_economies[sector_id] = economy
        return economy
    
    def _determine_trade_goods(self, specializations: List[str]) -> Tuple[List[str], List[str]]:
        """Determine what a sector imports and exports based on specializations"""
        exports = []
        imports = []
        
        specialization_exports = {
            "Mining": ["Iron", "Copper", "Gold", "Tritium", "Dilithium", "Rare Compounds"],
            "Agriculture": ["Food", "Grain", "Protein", "Spices"],
            "Manufacturing": ["Electronics", "Weapons", "Medical Equipment"],
            "Technology": ["Software", "AI Cores", "Electronics"],
            "Military": ["Weapons", "Military Hardware"],
            "Energy": ["Energy Cells", "Fuel", "Tritium"],
            "Pharmaceuticals": ["Medicine", "Medical Equipment", "Chemicals"]
        }
        
        specialization_imports = {
            "Mining": ["Food", "Medicine", "Weapons"],
            "Agriculture": ["Electronics", "Weapons", "Medicine"],
            "Manufacturing": ["Iron", "Copper", "Energy Cells", "Chemicals"],
            "Technology": ["Rare Compounds", "Energy Cells", "Food"],
            "Military": ["Iron", "Electronics", "Energy Cells"],
            "Energy": ["Iron", "Electronics", "Chemicals"],
            "Pharmaceuticals": ["Chemicals", "Electronics", "Food"]
        }
        
        for spec in specializations:
            if spec in specialization_exports:
                exports.extend(specialization_exports[spec])
            if spec in specialization_imports:
                imports.extend(specialization_imports[spec])
        
        # Remove duplicates and conflicts (can't export and import the same thing)
        exports = list(set(exports))
        imports = list(set(imports))
        imports = [item for item in imports if item not in exports]
        
        return imports, exports
    
    def update_market(self, turn_number: int):
        """Update market conditions for a new turn"""
        self.current_turn = turn_number
        
        # Update each commodity
        for commodity_name, market_data in self.commodities.items():
            self._update_commodity_price(commodity_name, market_data)
        
        # Process active events
        self._process_economic_events()
        
        # Chance to trigger new events
        if random.random() < self.event_probability:
            self._trigger_random_event()
        
        # Update sector economies
        for economy in self.sector_economies.values():
            self._update_sector_economy(economy)
        
        # Record historical data
        self._record_historical_data()
    
    def _update_commodity_price(self, commodity_name: str, market_data: MarketData):
        """Update price for a single commodity"""
        
        # Base supply/demand ratio
        supply_demand_ratio = market_data.supply / max(market_data.demand, 1)
        
        # Calculate price pressure from supply/demand
        if supply_demand_ratio > 1.2:
            price_pressure = -0.1  # Oversupply, prices fall
        elif supply_demand_ratio < 0.8:
            price_pressure = 0.1   # Undersupply, prices rise
        else:
            price_pressure = 0.0   # Balanced
        
        # Add trend momentum
        trend_factor = market_data.trend * 0.5
        
        # Add random volatility
        random_factor = random.gauss(0, market_data.volatility) * 0.1
        
        # Seasonal effects (simplified)
        seasonal_factor = math.sin(self.current_turn * 0.1) * self.seasonal_amplitude
        market_data.seasonal_factor = 1.0 + seasonal_factor
        
        # Calculate total price change
        total_change = price_pressure + trend_factor + random_factor
        total_change *= market_data.seasonal_factor
        total_change *= market_data.event_modifier
        
        # Apply price change
        price_multiplier = 1.0 + total_change
        market_data.current_price *= price_multiplier
        
        # Ensure price doesn't go below production cost
        min_price = market_data.production_cost * 0.8
        market_data.current_price = max(market_data.current_price, min_price)
        
        # Update trend (prices tend to revert to mean over time)
        mean_reversion = (market_data.base_price - market_data.current_price) / market_data.base_price * 0.05
        market_data.trend = (market_data.trend * 0.9) + mean_reversion + random.gauss(0, 0.02)
        market_data.trend = max(-0.5, min(0.5, market_data.trend))  # Clamp trend
        
        # Update supply and demand based on price changes
        self._update_supply_demand(market_data, price_multiplier)
    
    def _update_supply_demand(self, market_data: MarketData, price_multiplier: float):
        """Update supply and demand based on price changes"""
        
        # Price elasticity of demand (higher prices reduce demand)
        demand_elasticity = -0.5  # -50% demand change for 100% price change
        demand_change = (price_multiplier - 1.0) * demand_elasticity
        market_data.demand = int(market_data.demand * (1.0 + demand_change))
        market_data.demand = max(10, market_data.demand)  # Minimum demand
        
        # Price elasticity of supply (higher prices increase supply)
        supply_elasticity = 0.3   # +30% supply change for 100% price change
        supply_change = (price_multiplier - 1.0) * supply_elasticity
        market_data.supply = int(market_data.supply * (1.0 + supply_change))
        market_data.supply = max(10, market_data.supply)  # Minimum supply
        
        # Add random fluctuations
        market_data.demand += random.randint(-10, 10)
        market_data.supply += random.randint(-10, 10)
        
        # Ensure positive values
        market_data.demand = max(1, market_data.demand)
        market_data.supply = max(1, market_data.supply)
    
    def _process_economic_events(self):
        """Process active economic events"""
        active_events = []
        
        for event in self.active_events:
            # Check if event has expired
            if self.current_turn - event.start_turn >= event.duration:
                # Remove event effects
                for commodity in event.affected_commodities:
                    if commodity in self.commodities:
                        self.commodities[commodity].event_modifier = 1.0
                # Don't add to active_events (effectively removing it)
            else:
                # Event is still active
                active_events.append(event)
        
        self.active_events = active_events
    
    def _trigger_random_event(self):
        """Trigger a random economic event"""
        event_type = random.choice(list(EconomicEvent))
        if event_type == EconomicEvent.NONE:
            return
        
        template = self.economic_event_templates.get(event_type)
        if not template:
            return
        
        # Create event
        duration = random.randint(*template["duration"])
        event = EconomicEventData(
            event_type=event_type,
            affected_commodities=template["affected_commodities"],
            price_modifiers=template["price_modifiers"],
            supply_modifiers=template.get("supply_modifiers", {}),
            demand_modifiers=template.get("demand_modifiers", {}),
            duration=duration,
            description=template["description"],
            start_turn=self.current_turn,
            sector_id=random.choice(list(self.sector_economies.keys())) if self.sector_economies else None
        )
        
        # Apply event effects
        for commodity in event.affected_commodities:
            if commodity in self.commodities:
                price_mod = event.price_modifiers.get(commodity, 1.0)
                self.commodities[commodity].event_modifier = price_mod
                
                supply_mod = event.supply_modifiers.get(commodity, 1.0)
                self.commodities[commodity].supply = int(self.commodities[commodity].supply * supply_mod)
                
                demand_mod = event.demand_modifiers.get(commodity, 1.0)
                self.commodities[commodity].demand = int(self.commodities[commodity].demand * demand_mod)
        
        self.active_events.append(event)
        print(f"🌟 Economic Event: {event.description}")

    def trigger_event(self, event_type: EconomicEvent):
        """Trigger a specific economic event.

        The dynamic market system already supports random events internally.
        This public method exposes the same functionality for external systems
        such as the :class:`EventEngine` so that other gameplay systems can
        cause market-wide disturbances.
        """
        if event_type == EconomicEvent.NONE:
            return None

        template = self.economic_event_templates.get(event_type)
        if not template:
            return None

        duration = random.randint(*template["duration"])
        event = EconomicEventData(
            event_type=event_type,
            affected_commodities=template["affected_commodities"],
            price_modifiers=template["price_modifiers"],
            supply_modifiers=template.get("supply_modifiers", {}),
            demand_modifiers=template.get("demand_modifiers", {}),
            duration=duration,
            description=template["description"],
            start_turn=self.current_turn,
            sector_id=None,
        )

        self.active_events.append(event)

        for commodity in event.affected_commodities:
            if commodity in self.commodities:
                price_mod = event.price_modifiers.get(commodity, 1.0)
                self.commodities[commodity].event_modifier = price_mod

                supply_mod = event.supply_modifiers.get(commodity, 1.0)
                self.commodities[commodity].supply = int(
                    self.commodities[commodity].supply * supply_mod
                )

                demand_mod = event.demand_modifiers.get(commodity, 1.0)
                self.commodities[commodity].demand = int(
                    self.commodities[commodity].demand * demand_mod
                )

        return event
    
    def _update_sector_economy(self, economy: SectorEconomy):
        """Update a sector's economic conditions"""
        
        # Wealth level changes based on market conditions
        wealth_change = {
            MarketCondition.DEPRESSION: -0.02,
            MarketCondition.RECESSION: -0.01,
            MarketCondition.STABLE: 0.0,
            MarketCondition.GROWTH: 0.01,
            MarketCondition.BOOM: 0.02
        }[economy.market_condition]
        
        # Add random fluctuation
        wealth_change += random.gauss(0, 0.005)
        
        # Apply change
        economy.wealth_level *= (1.0 + wealth_change)
        economy.wealth_level = max(0.1, min(3.0, economy.wealth_level))  # Clamp values
        
        # Market condition can change based on wealth trends
        if random.random() < 0.1:  # 10% chance to change
            if economy.wealth_level > 1.5:
                economy.market_condition = random.choice([MarketCondition.GROWTH, MarketCondition.BOOM])
            elif economy.wealth_level < 0.7:
                economy.market_condition = random.choice([MarketCondition.RECESSION, MarketCondition.DEPRESSION])
            else:
                economy.market_condition = MarketCondition.STABLE
    
    def _record_historical_data(self):
        """Record current prices for historical analysis"""
        for commodity_name, market_data in self.commodities.items():
            self.historical_prices[commodity_name].append(market_data.current_price)
            
            # Keep only last 100 data points
            if len(self.historical_prices[commodity_name]) > 100:
                self.historical_prices[commodity_name].pop(0)
    
    def get_sector_prices(self, sector_id: int) -> Dict[str, float]:
        """Get commodity prices for a specific sector"""
        base_prices = {}
        
        for commodity_name, market_data in self.commodities.items():
            price = market_data.current_price
            
            # Apply sector-specific modifiers
            if sector_id in self.sector_economies:
                economy = self.sector_economies[sector_id]
                
                # Wealth level affects all prices
                price *= economy.wealth_level
                
                # Imports are more expensive, exports are cheaper
                if commodity_name in economy.imports:
                    price *= (1.1 + economy.corruption_level * 0.2)  # Import markup + corruption
                elif commodity_name in economy.exports:
                    price *= (0.9 - economy.corruption_level * 0.1)  # Export discount - corruption
                
                # Market condition affects prices
                condition_modifiers = {
                    MarketCondition.DEPRESSION: 0.8,
                    MarketCondition.RECESSION: 0.9,
                    MarketCondition.STABLE: 1.0,
                    MarketCondition.GROWTH: 1.1,
                    MarketCondition.BOOM: 1.2
                }
                price *= condition_modifiers[economy.market_condition]
                
                # Stability affects price variance
                variance = (1.0 - economy.stability) * 0.2
                price *= random.uniform(1.0 - variance, 1.0 + variance)
            
            base_prices[commodity_name] = max(1, int(price))
        
        return base_prices
    
    def execute_trade(self, commodity: str, quantity: int, sector_id: int, 
                     is_purchase: bool) -> Dict[str, Any]:
        """Execute a trade and update market conditions"""
        
        if commodity not in self.commodities:
            return {"success": False, "error": "Unknown commodity"}
        
        market_data = self.commodities[commodity]
        sector_prices = self.get_sector_prices(sector_id)
        price_per_unit = sector_prices[commodity]
        
        if is_purchase:
            # Buying increases demand, may increase price
            if quantity > market_data.supply:
                return {"success": False, "error": "Insufficient supply"}
            
            market_data.supply -= quantity
            market_data.demand += quantity // 4  # Buying creates future demand
            
        else:
            # Selling increases supply, may decrease price
            market_data.supply += quantity
            market_data.demand -= quantity // 4  # Selling reduces demand
        
        # Record trade volume
        if commodity not in self.trade_volumes:
            self.trade_volumes[commodity] = []
        
        self.trade_volumes[commodity].append({
            "turn": self.current_turn,
            "quantity": quantity,
            "price": price_per_unit,
            "sector": sector_id,
            "type": "buy" if is_purchase else "sell"
        })
        
        # Large trades affect prices more
        if quantity > market_data.supply // 10:  # More than 10% of supply
            price_impact = quantity / market_data.supply * 0.1
            if is_purchase:
                market_data.current_price *= (1.0 + price_impact)
            else:
                market_data.current_price *= (1.0 - price_impact)
        
        total_cost = price_per_unit * quantity
        
        return {
            "success": True,
            "commodity": commodity,
            "quantity": quantity,
            "price_per_unit": price_per_unit,
            "total_cost": total_cost,
            "remaining_supply": market_data.supply,
            "current_demand": market_data.demand
        }
    
    def get_market_analysis(self, commodity: str, sector_id: int = None) -> Dict[str, Any]:
        """Get detailed market analysis for a commodity"""
        
        if commodity not in self.commodities:
            return {"error": "Unknown commodity"}
        
        market_data = self.commodities[commodity]
        history = self.historical_prices.get(commodity, [])
        
        # Calculate trends
        if len(history) >= 2:
            recent_trend = (history[-1] - history[-5]) / history[-5] if len(history) >= 5 else 0
            long_term_trend = (history[-1] - history[0]) / history[0] if history else 0
        else:
            recent_trend = long_term_trend = 0
        
        # Get current price for sector
        if sector_id:
            current_price = self.get_sector_prices(sector_id).get(commodity, market_data.current_price)
        else:
            current_price = market_data.current_price
        
        # Supply/demand ratio
        supply_demand_ratio = market_data.supply / max(market_data.demand, 1)
        
        # Market outlook
        if supply_demand_ratio > 1.5:
            outlook = "Oversupplied - Prices likely to fall"
        elif supply_demand_ratio < 0.7:
            outlook = "High demand - Prices likely to rise"
        elif recent_trend > 0.1:
            outlook = "Rising trend - Bullish"
        elif recent_trend < -0.1:
            outlook = "Falling trend - Bearish"
        else:
            outlook = "Stable market conditions"
        
        # Investment recommendation
        if supply_demand_ratio < 0.8 and recent_trend > 0:
            recommendation = "BUY - Strong demand with upward trend"
        elif supply_demand_ratio > 1.3 and recent_trend < 0:
            recommendation = "SELL - Oversupply with downward trend"
        elif market_data.volatility > 0.4:
            recommendation = "HOLD - High volatility, wait for stability"
        else:
            recommendation = "NEUTRAL - No clear trend"
        
        # Active events affecting this commodity
        affecting_events = [
            event for event in self.active_events 
            if commodity in event.affected_commodities
        ]
        
        return {
            "commodity": commodity,
            "current_price": current_price,
            "base_price": market_data.base_price,
            "supply": market_data.supply,
            "demand": market_data.demand,
            "volatility": market_data.volatility,
            "trend": market_data.trend,
            "supply_demand_ratio": supply_demand_ratio,
            "recent_trend": recent_trend,
            "long_term_trend": long_term_trend,
            "outlook": outlook,
            "recommendation": recommendation,
            "price_history": history[-20:],  # Last 20 data points
            "active_events": [event.description for event in affecting_events],
            "category": market_data.category.value
        }
    
    def get_best_trade_opportunities(self, current_sector: int, 
                                   accessible_sectors: List[int]) -> List[Dict[str, Any]]:
        """Find the best trading opportunities between accessible sectors"""
        
        opportunities = []
        current_prices = self.get_sector_prices(current_sector)
        
        for target_sector in accessible_sectors:
            if target_sector == current_sector:
                continue
            
            target_prices = self.get_sector_prices(target_sector)
            
            for commodity in current_prices:
                buy_price = current_prices[commodity]
                sell_price = target_prices[commodity]
                
                if sell_price > buy_price:
                    profit_margin = (sell_price - buy_price) / buy_price
                    profit_per_unit = sell_price - buy_price
                    
                    opportunities.append({
                        "commodity": commodity,
                        "buy_sector": current_sector,
                        "sell_sector": target_sector,
                        "buy_price": buy_price,
                        "sell_price": sell_price,
                        "profit_per_unit": profit_per_unit,
                        "profit_margin": profit_margin,
                        "category": self.commodities[commodity].category.value
                    })
        
        # Sort by profit margin
        opportunities.sort(key=lambda x: x["profit_margin"], reverse=True)
        return opportunities[:10]  # Top 10 opportunities
    
    def get_economic_summary(self) -> Dict[str, Any]:
        """Get overall economic summary"""
        
        # Calculate average market conditions
        total_wealth = sum(eco.wealth_level for eco in self.sector_economies.values())
        avg_wealth = total_wealth / len(self.sector_economies) if self.sector_economies else 1.0
        
        # Count market conditions
        condition_counts = {}
        for eco in self.sector_economies.values():
            condition_counts[eco.market_condition.value] = condition_counts.get(eco.market_condition.value, 0) + 1
        
        # Calculate price volatility
        total_volatility = sum(market.volatility for market in self.commodities.values())
        avg_volatility = total_volatility / len(self.commodities)
        
        # Active events
        event_descriptions = [event.description for event in self.active_events]
        
        return {
            "turn": self.current_turn,
            "average_wealth_level": avg_wealth,
            "total_sectors": len(self.sector_economies),
            "market_conditions": condition_counts,
            "average_volatility": avg_volatility,
            "active_events": len(self.active_events),
            "event_descriptions": event_descriptions,
            "total_commodities": len(self.commodities),
            "inflation_rate": self.inflation_rate
        }
