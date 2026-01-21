#!/usr/bin/env python3
"""
AI Player System for StellarOdyssey2080
Intelligent computer-controlled players that compete with the human player
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from game.player import Player
from game.world import World


@dataclass
class AIPlayer:
    """An AI-controlled player with intelligent decision-making"""

    name: str
    personality: str  # aggressive, defensive, trader, explorer, balanced
    current_sector: int = 1
    credits: int = 1000
    level: int = 1
    experience: int = 0
    
    # AI-specific attributes
    goals: List[str] = field(default_factory=list)
    memory: Dict[str, any] = field(default_factory=dict)
    decision_history: List[Dict] = field(default_factory=list)
    
    # Trading intelligence
    market_knowledge: Dict[int, Dict[str, float]] = field(default_factory=dict)  # sector -> item -> price
    trade_history: List[Dict] = field(default_factory=list)
    
    # Exploration intelligence
    explored_sectors: List[int] = field(default_factory=list)
    sector_valuations: Dict[int, float] = field(default_factory=dict)  # sector -> value score
    
    # Combat intelligence
    combat_style: str = "balanced"  # aggressive, defensive, tactical
    threat_assessment: Dict[str, float] = field(default_factory=dict)
    
    # Empire building
    owned_planets: List[str] = field(default_factory=list)
    empire_strategy: str = "expansion"  # expansion, consolidation, trade
    
    # Decision weights based on personality
    decision_weights: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize AI player based on personality"""
        self._initialize_personality()
        self._initialize_goals()
    
    def _initialize_personality(self):
        """Set up decision weights and behavior based on personality"""
        if self.personality == "aggressive":
            self.decision_weights = {
                "combat": 0.4,
                "exploration": 0.2,
                "trading": 0.1,
                "empire": 0.3,
            }
            self.combat_style = "aggressive"
            self.empire_strategy = "expansion"
        elif self.personality == "trader":
            self.decision_weights = {
                "combat": 0.1,
                "exploration": 0.2,
                "trading": 0.5,
                "empire": 0.2,
            }
            self.combat_style = "defensive"
            self.empire_strategy = "trade"
        elif self.personality == "explorer":
            self.decision_weights = {
                "combat": 0.15,
                "exploration": 0.5,
                "trading": 0.15,
                "empire": 0.2,
            }
            self.combat_style = "tactical"
            self.empire_strategy = "expansion"
        elif self.personality == "defensive":
            self.decision_weights = {
                "combat": 0.2,
                "exploration": 0.2,
                "trading": 0.2,
                "empire": 0.4,
            }
            self.combat_style = "defensive"
            self.empire_strategy = "consolidation"
        else:  # balanced
            self.decision_weights = {
                "combat": 0.25,
                "exploration": 0.25,
                "trading": 0.25,
                "empire": 0.25,
            }
            self.combat_style = "balanced"
            self.empire_strategy = "expansion"
    
    def _initialize_goals(self):
        """Set initial goals based on personality"""
        if self.personality == "aggressive":
            self.goals = ["conquer_sectors", "build_army", "dominate_trade_routes"]
        elif self.personality == "trader":
            self.goals = ["maximize_profits", "establish_trade_routes", "control_markets"]
        elif self.personality == "explorer":
            self.goals = ["discover_all_sectors", "find_ancient_artifacts", "map_galaxy"]
        elif self.personality == "defensive":
            self.goals = ["fortify_positions", "build_alliances", "secure_resources"]
        else:
            self.goals = ["balanced_growth", "explore_and_trade", "build_empire"]
    
    def make_decision(self, world: World, trading_system, player: Optional[Player] = None) -> Dict:
        """Make an intelligent decision based on current state"""
        decision_type = self._choose_decision_type()
        
        if decision_type == "trade":
            return self._make_trading_decision(world, trading_system)
        elif decision_type == "explore":
            return self._make_exploration_decision(world)
        elif decision_type == "combat":
            return self._make_combat_decision(world, player)
        elif decision_type == "empire":
            return self._make_empire_decision(world)
        else:
            return {"action": "wait", "reason": "analyzing situation"}
    
    def _choose_decision_type(self) -> str:
        """Choose what type of decision to make based on weights and current state"""
        # Adjust weights based on current situation
        adjusted_weights = self.decision_weights.copy()
        
        # If low on credits, prioritize trading
        if self.credits < 500:
            adjusted_weights["trading"] *= 1.5
        else:
            adjusted_weights["trading"] *= 0.8
        
        # If haven't explored much, prioritize exploration
        if len(self.explored_sectors) < 5:
            adjusted_weights["exploration"] *= 1.5
        else:
            adjusted_weights["exploration"] *= 0.9
        
        # If have planets, prioritize empire management
        if len(self.owned_planets) > 0:
            adjusted_weights["empire"] *= 1.3
        
        # Normalize weights
        total = sum(adjusted_weights.values())
        if total > 0:
            for key in adjusted_weights:
                adjusted_weights[key] /= total
        
        # Choose based on weighted random
        rand = random.random()
        cumulative = 0.0
        
        for decision_type, weight in adjusted_weights.items():
            cumulative += weight
            if rand <= cumulative:
                return decision_type
        
        return "exploration"  # Default fallback
    
    def _make_trading_decision(self, world: World, trading_system) -> Dict:
        """Make an intelligent trading decision"""
        current_sector = self.current_sector
        
        # Learn market prices
        if current_sector not in self.market_knowledge:
            self.market_knowledge[current_sector] = {}
        
        # Get current market prices
        try:
            prices = trading_system.get_sector_prices(current_sector)
            for item, price in prices.items():
                self.market_knowledge[current_sector][item] = price
        except Exception:
            pass
        
        # Find best trade opportunity
        best_opportunity = self._find_best_trade_opportunity(world, trading_system)
        
        if best_opportunity:
            return {
                "action": "trade",
                "type": best_opportunity["action"],  # buy or sell
                "item": best_opportunity["item"],
                "quantity": best_opportunity["quantity"],
                "sector": best_opportunity["sector"],
                "expected_profit": best_opportunity["profit"],
                "reason": f"Identified profitable trade opportunity"
            }
        
        # Move to better trading location
        best_trade_sector = self._find_best_trade_sector(world, trading_system)
        if best_trade_sector and best_trade_sector != current_sector:
            return {
                "action": "travel",
                "destination": best_trade_sector,
                "reason": "Moving to better trading location"
            }
        
        return {"action": "wait", "reason": "No profitable trades available"}
    
    def _find_best_trade_opportunity(self, world: World, trading_system) -> Optional[Dict]:
        """Find the best trade opportunity across known sectors"""
        opportunities = []
        
        # Check known sectors for arbitrage
        for sector_id, prices in self.market_knowledge.items():
            if not prices:
                continue
            
            # Find items to buy (low price)
            for item, price in prices.items():
                # Check if we can sell elsewhere for profit
                for other_sector, other_prices in self.market_knowledge.items():
                    if other_sector == sector_id:
                        continue
                    if item in other_prices:
                        sell_price = other_prices[item]
                        if sell_price > price * 1.2:  # 20% profit margin
                            profit = (sell_price - price) * min(10, self.credits // price)
                            opportunities.append({
                                "action": "buy",
                                "item": item,
                                "quantity": min(10, self.credits // price),
                                "sector": sector_id,
                                "profit": profit,
                            })
        
        if opportunities:
            # Return best opportunity
            return max(opportunities, key=lambda x: x["profit"])
        
        return None
    
    def _find_best_trade_sector(self, world: World, trading_system) -> Optional[int]:
        """Find the sector with best trading opportunities"""
        if not self.market_knowledge:
            # Explore random sector
            return random.randint(1, 10)
        
        # Score sectors based on trade potential
        sector_scores = {}
        for sector_id, prices in self.market_knowledge.items():
            if not prices:
                continue
            # Score based on price volatility and opportunities
            score = len(prices) * 10  # More items = better
            sector_scores[sector_id] = score
        
        if sector_scores:
            return max(sector_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _make_exploration_decision(self, world: World) -> Dict:
        """Make an intelligent exploration decision"""
        # Find unexplored sectors
        current_location = world.get_current_location()
        if not current_location:
            return {"action": "wait", "reason": "No location data"}
        
        # Get connected sectors
        connected_sectors = []
        try:
            connections = world.sector_connections.get(self.current_sector, [])
            for conn in connections:
                connected_sectors.append(conn.destination_sector)
        except Exception:
            pass
        
        # Prioritize unexplored connected sectors
        unexplored = [s for s in connected_sectors if s not in self.explored_sectors]
        
        if unexplored:
            target = random.choice(unexplored)
            return {
                "action": "travel",
                "destination": target,
                "reason": f"Exploring new sector {target}"
            }
        
        # If all connected explored, explore further
        if connected_sectors:
            target = random.choice(connected_sectors)
            return {
                "action": "travel",
                "destination": target,
                "reason": f"Re-exploring sector {target} for opportunities"
            }
        
        return {"action": "wait", "reason": "No sectors to explore"}
    
    def _make_combat_decision(self, world: World, player: Optional[Player]) -> Dict:
        """Make an intelligent combat decision"""
        if not player:
            return {"action": "wait", "reason": "No combat targets"}
        
        # Assess threat level
        threat = self._assess_threat(player)
        
        if self.combat_style == "aggressive":
            if threat < 0.7:  # If we think we can win
                return {
                    "action": "combat",
                    "target": "player",
                    "reason": "Aggressive AI engaging player"
                }
        elif self.combat_style == "defensive":
            if threat > 0.5:  # If threatened
                return {
                    "action": "flee",
                    "reason": "Defensive AI avoiding combat"
                }
        else:  # tactical
            if threat < 0.6 and self.level >= player.level:
                return {
                    "action": "combat",
                    "target": "player",
                    "reason": "Tactical advantage identified"
                }
        
        return {"action": "wait", "reason": "No combat action needed"}
    
    def _assess_threat(self, player: Player) -> float:
        """Assess threat level of player (0.0 = no threat, 1.0 = extreme threat)"""
        # Simple threat assessment based on level and credits
        level_diff = player.level - self.level
        credit_diff = player.credits - self.credits
        
        threat = 0.5  # Base threat
        
        # Level difference
        threat += level_diff * 0.1
        
        # Credit difference (wealth = power)
        threat += min(credit_diff / 10000, 0.3)
        
        return max(0.0, min(1.0, threat))
    
    def _make_empire_decision(self, world: World) -> Dict:
        """Make an intelligent empire building decision"""
        current_location = world.get_current_location()
        if not current_location:
            return {"action": "wait", "reason": "No location data"}
        
        # If at a planet and don't own it, consider capturing
        if current_location.location_type == "planet":
            planet_key = f"{current_location.name}|{self.current_sector}"
            if planet_key not in self.owned_planets:
                # Check if we have enough resources
                if self.credits >= 500 and self.level >= 3:
                    if self.empire_strategy in ["expansion", "balanced"]:
                        return {
                            "action": "capture_planet",
                            "planet": current_location.name,
                            "sector": self.current_sector,
                            "reason": "Expanding empire"
                        }
        
        # Manage existing planets
        if self.owned_planets:
            return {
                "action": "manage_empire",
                "reason": "Optimizing empire policies"
            }
        
        return {"action": "wait", "reason": "No empire actions available"}
    
    def learn_from_experience(self, decision: Dict, outcome: Dict):
        """Learn from decision outcomes to improve future decisions"""
        # Store decision and outcome
        self.decision_history.append({
            "decision": decision,
            "outcome": outcome,
            "timestamp": time.time()
        })
        
        # Update market knowledge
        if decision.get("action") == "trade" and outcome.get("success"):
            sector = decision.get("sector", self.current_sector)
            if sector not in self.market_knowledge:
                self.market_knowledge[sector] = {}
            
            item = decision.get("item")
            if item:
                # Update price knowledge
                profit = outcome.get("profit", 0)
                if profit > 0:
                    # Good trade, remember this
                    self.memory[f"good_trade_{item}_{sector}"] = True
                else:
                    # Bad trade, avoid similar
                    self.memory[f"bad_trade_{item}_{sector}"] = True
        
        # Update threat assessment
        if decision.get("action") == "combat":
            if outcome.get("victory"):
                # Won combat, might be more aggressive
                self.decision_weights["combat"] *= 1.05
            else:
                # Lost combat, be more cautious
                self.decision_weights["combat"] *= 0.95
        
        # Keep only recent history (last 100 decisions)
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
    
    def update_state(self, world: World):
        """Update AI player state based on world changes"""
        # Update current sector
        current_location = world.get_current_location()
        if current_location:
            self.current_sector = current_location.sector
            
            # Mark sector as explored
            if self.current_sector not in self.explored_sectors:
                self.explored_sectors.append(self.current_sector)
    
    def get_status(self) -> Dict:
        """Get current status of AI player"""
        return {
            "name": self.name,
            "personality": self.personality,
            "level": self.level,
            "credits": self.credits,
            "current_sector": self.current_sector,
            "explored_sectors": len(self.explored_sectors),
            "owned_planets": len(self.owned_planets),
            "goals": self.goals,
        }


class AIPlayerManager:
    """Manages multiple AI players in the game"""
    
    def __init__(self):
        self.ai_players: List[AIPlayer] = []
        self.update_interval = 60  # Update AI players every 60 seconds
        self.last_update = 0
    
    def create_ai_player(self, name: str, personality: str = "balanced") -> AIPlayer:
        """Create a new AI player"""
        ai_player = AIPlayer(name=name, personality=personality)
        self.ai_players.append(ai_player)
        return ai_player
    
    def update_ai_players(self, world: World, trading_system, player: Optional[Player] = None):
        """Update all AI players"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        for ai_player in self.ai_players:
            # Update state
            ai_player.update_state(world)
            
            # Make decision
            decision = ai_player.make_decision(world, trading_system, player)
            
            # Execute decision (simplified - in real game would have more complex execution)
            if decision.get("action") == "travel":
                ai_player.current_sector = decision.get("destination", ai_player.current_sector)
            elif decision.get("action") == "trade":
                # Simulate trade (would interact with trading system)
                pass
            elif decision.get("action") == "capture_planet":
                # Simulate planet capture
                planet_key = f"{decision.get('planet')}|{decision.get('sector')}"
                if planet_key not in ai_player.owned_planets:
                    ai_player.owned_planets.append(planet_key)
    
    def get_ai_players_status(self) -> List[Dict]:
        """Get status of all AI players"""
        return [ai_player.get_status() for ai_player in self.ai_players]
    
    def get_ai_player(self, name: str) -> Optional[AIPlayer]:
        """Get AI player by name"""
        for ai_player in self.ai_players:
            if ai_player.name == name:
                return ai_player
        return None

