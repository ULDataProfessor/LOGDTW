#!/usr/bin/env python3
"""
Random Events & Encounters System for LOGDTW2002
Manages dynamic events, encounters, and their consequences
"""

import random
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Union
from enum import Enum
from pathlib import Path

class EventType(Enum):
    """Types of random events"""
    MALFUNCTION = "malfunction"
    PIRATE_ATTACK = "pirate_attack"
    MARKET_CRASH = "market_crash"
    MARKET_BOOM = "market_boom"
    DISTRESS_CALL = "distress_call"
    STORM = "storm"
    DISCOVERY = "discovery"
    NPC_ENCOUNTER = "npc_encounter"
    SYSTEM_FAILURE = "system_failure"
    FUEL_LEAK = "fuel_leak"
    CARGO_THEFT = "cargo_theft"
    FRIENDLY_TRADER = "friendly_trader"
    MYSTERIOUS_SIGNAL = "mysterious_signal"

class EventContext(Enum):
    """When events can occur"""
    IN_SPACE = "in_space"
    AT_STATION = "at_station"
    DURING_TRAVEL = "during_travel"
    AFTER_TRADE = "after_trade"
    AFTER_COMBAT = "after_combat"
    ON_PLANET = "on_planet"

@dataclass
class EventOutcome:
    """Result of an event"""
    success: bool
    message: str
    effects: Dict[str, Any] = field(default_factory=dict)
    choices: List[str] = field(default_factory=list)
    rewards: Dict[str, int] = field(default_factory=dict)
    penalties: Dict[str, int] = field(default_factory=dict)

@dataclass
class RandomEvent:
    """Definition of a random event"""
    event_id: str
    name: str
    description: str
    event_type: EventType
    context: EventContext
    base_probability: float  # 0.0 to 1.0
    cooldown_seconds: int = 300  # 5 minutes default
    min_level: int = 1
    max_level: int = 100
    faction_requirements: List[str] = field(default_factory=list)
    item_requirements: List[str] = field(default_factory=list)
    last_triggered: float = 0.0
    
    def can_trigger(self, game_state: Dict[str, Any]) -> bool:
        """Check if this event can trigger given current game state"""
        # Check cooldown
        current_time = time.time()
        if (current_time - self.last_triggered) < self.cooldown_seconds:
            return False
        
        # Check level requirements
        player_level = game_state.get('player_level', 1)
        if not (self.min_level <= player_level <= self.max_level):
            return False
        
        # Check faction requirements
        if self.faction_requirements:
            player_reputation = game_state.get('reputation', {})
            for faction in self.faction_requirements:
                if player_reputation.get(faction, 0) < 0:
                    return False
        
        # Check item requirements
        if self.item_requirements:
            inventory = game_state.get('inventory', [])
            inventory_names = [item.get('name', '') for item in inventory]
            for required_item in self.item_requirements:
                if required_item not in inventory_names:
                    return False
        
        return True
    
    def get_weighted_probability(self, game_state: Dict[str, Any]) -> float:
        """Get probability adjusted for current game state"""
        if not self.can_trigger(game_state):
            return 0.0
        
        probability = self.base_probability
        
        # Adjust based on current sector danger
        sector_danger = game_state.get('sector_danger', 1)
        if self.event_type in [EventType.PIRATE_ATTACK, EventType.MALFUNCTION, EventType.STORM]:
            probability *= (1.0 + sector_danger * 0.2)
        
        # Adjust based on player health/condition
        player_health = game_state.get('player_health', 100)
        if player_health < 50 and self.event_type == EventType.MALFUNCTION:
            probability *= 2.0
        
        # Adjust based on reputation
        reputation = game_state.get('reputation', {})
        pirate_rep = reputation.get('Pirates', 0)
        if self.event_type == EventType.PIRATE_ATTACK and pirate_rep > 50:
            probability *= 0.5  # Reduce pirate attacks if good with pirates
        
        return min(probability, 1.0)

class RandomEventSystem:
    """
    Manages random events and encounters in the game
    
    Features:
    - Weighted probability system
    - Cooldown management
    - Context-based triggering
    - Player choice handling
    - Persistent event history
    """
    
    def __init__(self):
        self.events: Dict[str, RandomEvent] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.global_event_cooldown = 60  # Minimum seconds between any events
        self.last_global_event = 0.0
        self.rng = random.Random()
        
        # Initialize default events
        self._create_default_events()
    
    def _create_default_events(self):
        """Create the default set of random events"""
        
        # Ship malfunction
        self.add_event(RandomEvent(
            event_id="ship_malfunction",
            name="Ship Malfunction",
            description="Your ship's systems are experiencing technical difficulties.",
            event_type=EventType.MALFUNCTION,
            context=EventContext.IN_SPACE,
            base_probability=0.05,
            cooldown_seconds=600
        ))
        
        # Pirate attack
        self.add_event(RandomEvent(
            event_id="pirate_ambush",
            name="Pirate Ambush",
            description="Pirates have targeted your ship for attack!",
            event_type=EventType.PIRATE_ATTACK,
            context=EventContext.IN_SPACE,
            base_probability=0.08,
            cooldown_seconds=900,
            min_level=2
        ))
        
        # Market crash
        self.add_event(RandomEvent(
            event_id="market_crash",
            name="Market Crash",
            description="Economic instability causes market prices to plummet.",
            event_type=EventType.MARKET_CRASH,
            context=EventContext.AT_STATION,
            base_probability=0.03,
            cooldown_seconds=1800
        ))
        
        # Market boom
        self.add_event(RandomEvent(
            event_id="market_boom",
            name="Market Boom",
            description="Economic prosperity drives commodity prices up!",
            event_type=EventType.MARKET_BOOM,
            context=EventContext.AT_STATION,
            base_probability=0.04,
            cooldown_seconds=1800
        ))
        
        # Distress call
        self.add_event(RandomEvent(
            event_id="distress_signal",
            name="Distress Signal",
            description="You receive a distress signal from a nearby ship.",
            event_type=EventType.DISTRESS_CALL,
            context=EventContext.IN_SPACE,
            base_probability=0.06,
            cooldown_seconds=1200
        ))
        
        # Space storm
        self.add_event(RandomEvent(
            event_id="space_storm",
            name="Space Storm",
            description="A dangerous space storm threatens your ship's systems.",
            event_type=EventType.STORM,
            context=EventContext.DURING_TRAVEL,
            base_probability=0.04,
            cooldown_seconds=800
        ))
        
        # Discovery
        self.add_event(RandomEvent(
            event_id="rare_discovery",
            name="Rare Discovery",
            description="You've discovered something unusual in this sector.",
            event_type=EventType.DISCOVERY,
            context=EventContext.IN_SPACE,
            base_probability=0.02,
            cooldown_seconds=2400
        ))
        
        # Fuel leak
        self.add_event(RandomEvent(
            event_id="fuel_leak",
            name="Fuel Leak",
            description="A fuel leak is detected in your ship's systems.",
            event_type=EventType.FUEL_LEAK,
            context=EventContext.IN_SPACE,
            base_probability=0.03,
            cooldown_seconds=600
        ))
        
        # Friendly trader
        self.add_event(RandomEvent(
            event_id="friendly_trader",
            name="Friendly Trader",
            description="A friendly trader offers you a special deal.",
            event_type=EventType.FRIENDLY_TRADER,
            context=EventContext.IN_SPACE,
            base_probability=0.05,
            cooldown_seconds=1200
        ))
        
        # Mysterious signal
        self.add_event(RandomEvent(
            event_id="mysterious_signal",
            name="Mysterious Signal",
            description="Your sensors detect an unknown signal.",
            event_type=EventType.MYSTERIOUS_SIGNAL,
            context=EventContext.IN_SPACE,
            base_probability=0.01,
            cooldown_seconds=3600,
            min_level=5
        ))
    
    def add_event(self, event: RandomEvent):
        """Add an event to the system"""
        self.events[event.event_id] = event
    
    def remove_event(self, event_id: str):
        """Remove an event from the system"""
        if event_id in self.events:
            del self.events[event_id]
    
    def seed_random(self, seed: int):
        """Seed the random number generator for reproducible events"""
        self.rng.seed(seed)
    
    def check_for_events(self, context: EventContext, game_state: Dict[str, Any]) -> Optional[RandomEvent]:
        """
        Check if any events should trigger in the given context
        Returns the triggered event or None
        """
        current_time = time.time()
        
        # Check global cooldown
        if (current_time - self.last_global_event) < self.global_event_cooldown:
            return None
        
        # Get eligible events for this context
        eligible_events = [
            event for event in self.events.values()
            if event.context == context and event.can_trigger(game_state)
        ]
        
        if not eligible_events:
            return None
        
        # Calculate weighted probabilities
        weights = [event.get_weighted_probability(game_state) for event in eligible_events]
        total_weight = sum(weights)
        
        if total_weight <= 0:
            return None
        
        # Check if any event should trigger
        roll = self.rng.random()
        cumulative_probability = 0.0
        
        for event, weight in zip(eligible_events, weights):
            cumulative_probability += weight / total_weight * 0.3  # 30% max chance per check
            if roll <= cumulative_probability:
                event.last_triggered = current_time
                self.last_global_event = current_time
                return event
        
        return None
    
    def handle_event(self, event: RandomEvent, game_state: Dict[str, Any], 
                    choice: str = None) -> EventOutcome:
        """Handle the execution of an event and return the outcome"""
        
        # Record event in history
        self.event_history.append({
            'event_id': event.event_id,
            'timestamp': time.time(),
            'game_state_snapshot': {
                'player_level': game_state.get('player_level', 1),
                'current_sector': game_state.get('current_sector', 1),
                'credits': game_state.get('credits', 0)
            }
        })
        
        # Handle different event types
        if event.event_type == EventType.MALFUNCTION:
            return self._handle_malfunction(event, game_state, choice)
        elif event.event_type == EventType.PIRATE_ATTACK:
            return self._handle_pirate_attack(event, game_state, choice)
        elif event.event_type == EventType.MARKET_CRASH:
            return self._handle_market_crash(event, game_state, choice)
        elif event.event_type == EventType.MARKET_BOOM:
            return self._handle_market_boom(event, game_state, choice)
        elif event.event_type == EventType.DISTRESS_CALL:
            return self._handle_distress_call(event, game_state, choice)
        elif event.event_type == EventType.STORM:
            return self._handle_storm(event, game_state, choice)
        elif event.event_type == EventType.DISCOVERY:
            return self._handle_discovery(event, game_state, choice)
        elif event.event_type == EventType.FUEL_LEAK:
            return self._handle_fuel_leak(event, game_state, choice)
        elif event.event_type == EventType.FRIENDLY_TRADER:
            return self._handle_friendly_trader(event, game_state, choice)
        elif event.event_type == EventType.MYSTERIOUS_SIGNAL:
            return self._handle_mysterious_signal(event, game_state, choice)
        else:
            return EventOutcome(
                success=False,
                message=f"Unknown event type: {event.event_type}",
                effects={}
            )
    
    def _handle_malfunction(self, event: RandomEvent, game_state: Dict[str, Any], 
                          choice: str = None) -> EventOutcome:
        """Handle ship malfunction events"""
        damage = self.rng.randint(10, 30)
        fuel_loss = self.rng.randint(5, 15)
        
        if choice is None:
            return EventOutcome(
                success=True,
                message=f"{event.description} Your ship takes {damage} damage and loses {fuel_loss} fuel.",
                effects={
                    'health_damage': damage,
                    'fuel_loss': fuel_loss
                },
                choices=['repair_now', 'continue_damaged']
            )
        
        if choice == 'repair_now':
            repair_cost = damage * 10
            return EventOutcome(
                success=True,
                message=f"You perform emergency repairs for {repair_cost} credits.",
                effects={
                    'credit_cost': repair_cost,
                    'health_restore': damage
                }
            )
        elif choice == 'continue_damaged':
            return EventOutcome(
                success=True,
                message="You decide to continue with the damaged systems. Be careful!",
                effects={
                    'ongoing_malfunction': True
                }
            )
        
        return EventOutcome(success=False, message="Invalid choice for malfunction event.")
    
    def _handle_pirate_attack(self, event: RandomEvent, game_state: Dict[str, Any], 
                            choice: str = None) -> EventOutcome:
        """Handle pirate attack events"""
        player_combat = game_state.get('combat_power', 50)
        pirate_power = self.rng.randint(30, 80)
        
        if choice is None:
            escape_chance = min(90, game_state.get('piloting_skill', 50))
            bribe_amount = self.rng.randint(200, 500)
            
            return EventOutcome(
                success=True,
                message=f"{event.description} Pirate ship power: {pirate_power}. What do you do?",
                effects={
                    'pirate_power': pirate_power,
                    'escape_chance': escape_chance,
                    'bribe_amount': bribe_amount
                },
                choices=['fight', 'flee', 'bribe']
            )
        
        if choice == 'fight':
            if player_combat > pirate_power:
                loot = self.rng.randint(100, 300)
                return EventOutcome(
                    success=True,
                    message=f"You defeated the pirates and found {loot} credits in their wreckage!",
                    rewards={'credits': loot},
                    effects={'reputation_pirates': -10}
                )
            else:
                damage = self.rng.randint(20, 50)
                credit_loss = self.rng.randint(50, 200)
                return EventOutcome(
                    success=False,
                    message=f"The pirates overpowered you! You lose {damage} health and {credit_loss} credits.",
                    penalties={'health': damage, 'credits': credit_loss}
                )
        
        elif choice == 'flee':
            escape_chance = min(90, game_state.get('piloting_skill', 50))
            if self.rng.randint(1, 100) <= escape_chance:
                return EventOutcome(
                    success=True,
                    message="You successfully escaped from the pirates!",
                    effects={'fuel_loss': 10}
                )
            else:
                damage = self.rng.randint(10, 25)
                return EventOutcome(
                    success=False,
                    message=f"Escape failed! You take {damage} damage in the chase.",
                    penalties={'health': damage}
                )
        
        elif choice == 'bribe':
            bribe_amount = self.rng.randint(200, 500)
            if game_state.get('credits', 0) >= bribe_amount:
                return EventOutcome(
                    success=True,
                    message=f"You pay {bribe_amount} credits and the pirates let you pass.",
                    effects={'credit_cost': bribe_amount}
                )
            else:
                return EventOutcome(
                    success=False,
                    message="You don't have enough credits to bribe the pirates!",
                    choices=['fight', 'flee']
                )
        
        return EventOutcome(success=False, message="Invalid choice for pirate attack.")
    
    def _handle_market_crash(self, event: RandomEvent, game_state: Dict[str, Any], 
                           choice: str = None) -> EventOutcome:
        """Handle market crash events"""
        affected_goods = self.rng.choice(['Electronics', 'Weapons', 'Medicine', 'Food'])
        price_drop = self.rng.uniform(0.3, 0.6)  # 30-60% price drop
        
        return EventOutcome(
            success=True,
            message=f"{event.description} {affected_goods} prices have dropped by {int(price_drop*100)}%!",
            effects={
                'market_crash': True,
                'affected_good': affected_goods,
                'price_multiplier': 1.0 - price_drop
            }
        )
    
    def _handle_market_boom(self, event: RandomEvent, game_state: Dict[str, Any], 
                          choice: str = None) -> EventOutcome:
        """Handle market boom events"""
        affected_goods = self.rng.choice(['Tritium', 'Dilithium', 'Ammolite', 'Rare Metals'])
        price_increase = self.rng.uniform(0.5, 1.2)  # 50-120% price increase
        
        return EventOutcome(
            success=True,
            message=f"{event.description} {affected_goods} prices have increased by {int(price_increase*100)}%!",
            effects={
                'market_boom': True,
                'affected_good': affected_goods,
                'price_multiplier': 1.0 + price_increase
            }
        )
    
    def _handle_distress_call(self, event: RandomEvent, game_state: Dict[str, Any], 
                            choice: str = None) -> EventOutcome:
        """Handle distress call events"""
        if choice is None:
            return EventOutcome(
                success=True,
                message=f"{event.description} Do you want to respond?",
                choices=['respond', 'ignore']
            )
        
        if choice == 'respond':
            success_chance = game_state.get('engineering_skill', 50)
            if self.rng.randint(1, 100) <= success_chance:
                reward = self.rng.randint(300, 800)
                return EventOutcome(
                    success=True,
                    message=f"You successfully rescued the ship's crew! They reward you with {reward} credits.",
                    rewards={'credits': reward},
                    effects={'reputation_traders': 15}
                )
            else:
                fuel_cost = self.rng.randint(15, 25)
                return EventOutcome(
                    success=False,
                    message=f"The rescue attempt failed and cost you {fuel_cost} fuel.",
                    penalties={'fuel': fuel_cost}
                )
        elif choice == 'ignore':
            return EventOutcome(
                success=True,
                message="You decide to ignore the distress call and continue on your way.",
                effects={'reputation_traders': -5}
            )
        
        return EventOutcome(success=False, message="Invalid choice for distress call.")
    
    def _handle_storm(self, event: RandomEvent, game_state: Dict[str, Any], 
                    choice: str = None) -> EventOutcome:
        """Handle space storm events"""
        damage = self.rng.randint(5, 20)
        sensor_impairment_duration = self.rng.randint(2, 5)  # turns
        
        return EventOutcome(
            success=True,
            message=f"{event.description} The storm damages your ship for {damage} health and impairs sensors for {sensor_impairment_duration} turns.",
            effects={
                'health_damage': damage,
                'sensor_impairment': sensor_impairment_duration
            }
        )
    
    def _handle_discovery(self, event: RandomEvent, game_state: Dict[str, Any], 
                        choice: str = None) -> EventOutcome:
        """Handle discovery events"""
        discoveries = [
            ('Ancient Artifact', 'credits', self.rng.randint(500, 1500)),
            ('Rare Mineral Deposit', 'item', 'Rare Metals'),
            ('Abandoned Ship', 'fuel', self.rng.randint(20, 50)),
            ('Space Debris', 'scrap', self.rng.randint(10, 30)),
            ('Data Cache', 'experience', self.rng.randint(50, 150))
        ]
        
        discovery_name, reward_type, reward_value = self.rng.choice(discoveries)
        
        return EventOutcome(
            success=True,
            message=f"{event.description} You discovered: {discovery_name}!",
            rewards={reward_type: reward_value}
        )
    
    def _handle_fuel_leak(self, event: RandomEvent, game_state: Dict[str, Any], 
                        choice: str = None) -> EventOutcome:
        """Handle fuel leak events"""
        fuel_loss = self.rng.randint(15, 30)
        
        if choice is None:
            return EventOutcome(
                success=True,
                message=f"{event.description} You're losing {fuel_loss} fuel units!",
                effects={'fuel_loss': fuel_loss},
                choices=['emergency_patch', 'jettison_cargo']
            )
        
        if choice == 'emergency_patch':
            engineering_skill = game_state.get('engineering_skill', 50)
            if self.rng.randint(1, 100) <= engineering_skill:
                return EventOutcome(
                    success=True,
                    message="Emergency patch successful! Fuel leak sealed.",
                    effects={'fuel_loss_prevented': True}
                )
            else:
                return EventOutcome(
                    success=False,
                    message=f"Patch failed! You lose {fuel_loss} fuel.",
                    penalties={'fuel': fuel_loss}
                )
        elif choice == 'jettison_cargo':
            return EventOutcome(
                success=True,
                message="You jettison some cargo to reduce pressure and seal the leak.",
                effects={'cargo_loss': 1}
            )
        
        return EventOutcome(success=False, message="Invalid choice for fuel leak.")
    
    def _handle_friendly_trader(self, event: RandomEvent, game_state: Dict[str, Any], 
                              choice: str = None) -> EventOutcome:
        """Handle friendly trader events"""
        goods = ['Electronics', 'Medicine', 'Food', 'Iron']
        offered_good = self.rng.choice(goods)
        discount = self.rng.uniform(0.2, 0.4)  # 20-40% discount
        
        if choice is None:
            return EventOutcome(
                success=True,
                message=f"{event.description} They offer {offered_good} at {int(discount*100)}% off market price!",
                effects={
                    'trade_offer': True,
                    'offered_good': offered_good,
                    'discount': discount
                },
                choices=['accept', 'decline']
            )
        
        if choice == 'accept':
            return EventOutcome(
                success=True,
                message=f"You accept the trader's offer for discounted {offered_good}.",
                effects={
                    'special_trade': True,
                    'good': offered_good,
                    'discount': discount
                }
            )
        elif choice == 'decline':
            return EventOutcome(
                success=True,
                message="You politely decline the trader's offer.",
                effects={}
            )
        
        return EventOutcome(success=False, message="Invalid choice for trader encounter.")
    
    def _handle_mysterious_signal(self, event: RandomEvent, game_state: Dict[str, Any], 
                                choice: str = None) -> EventOutcome:
        """Handle mysterious signal events"""
        if choice is None:
            return EventOutcome(
                success=True,
                message=f"{event.description} The signal's origin is unknown. Investigate?",
                choices=['investigate', 'ignore']
            )
        
        if choice == 'investigate':
            outcomes = [
                ('alien_technology', 'You discover alien technology!', {'credits': 2000, 'experience': 200}),
                ('trap', 'It was a trap! Pirates ambush you!', {'health': -30}),
                ('derelict', 'You find a derelict ship with valuable cargo.', {'credits': 1000}),
                ('nothing', 'The signal leads to nothing but empty space.', {})
            ]
            
            outcome_type, message, effects = self.rng.choice(outcomes)
            
            return EventOutcome(
                success=outcome_type != 'trap',
                message=message,
                effects=effects
            )
        elif choice == 'ignore':
            return EventOutcome(
                success=True,
                message="You decide the risk isn't worth it and continue on your course.",
                effects={}
            )
        
        return EventOutcome(success=False, message="Invalid choice for mysterious signal.")
    
    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent event history"""
        return self.event_history[-limit:]
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about events"""
        total_events = len(self.event_history)
        event_types = {}
        
        for event_record in self.event_history:
            event_id = event_record['event_id']
            if event_id in event_types:
                event_types[event_id] += 1
            else:
                event_types[event_id] = 1
        
        return {
            'total_events': total_events,
            'event_types': event_types,
            'most_common': max(event_types.items(), key=lambda x: x[1]) if event_types else None,
            'global_cooldown': self.global_event_cooldown,
            'time_since_last_event': time.time() - self.last_global_event
        }
    
    def save_to_file(self, save_path: Path):
        """Save event system state to file"""
        data = {
            'event_history': self.event_history,
            'global_event_cooldown': self.global_event_cooldown,
            'last_global_event': self.last_global_event,
            'events': {}
        }
        
        # Save event states (cooldowns)
        for event_id, event in self.events.items():
            data['events'][event_id] = {
                'last_triggered': event.last_triggered
            }
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, save_path: Path) -> bool:
        """Load event system state from file"""
        try:
            if not save_path.exists():
                return False
            
            with open(save_path, 'r') as f:
                data = json.load(f)
            
            self.event_history = data.get('event_history', [])
            self.global_event_cooldown = data.get('global_event_cooldown', 60)
            self.last_global_event = data.get('last_global_event', 0.0)
            
            # Restore event cooldown states
            events_data = data.get('events', {})
            for event_id, event_data in events_data.items():
                if event_id in self.events:
                    self.events[event_id].last_triggered = event_data.get('last_triggered', 0.0)
            
            return True
            
        except Exception as e:
            print(f"Error loading event system data: {e}")
            return False
    
    def debug_info(self) -> Dict[str, Any]:
        """Get debug information about the event system"""
        stats = self.get_event_statistics()
        
        return {
            'system': 'RandomEventSystem',
            'total_events_registered': len(self.events),
            'statistics': stats,
            'recent_history': self.get_event_history(5)
        }

def create_random_event_system() -> RandomEventSystem:
    """Factory function to create a random event system"""
    return RandomEventSystem()
