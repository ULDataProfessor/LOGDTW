"""
SOS and Distress System for LOGDTW2002
Handles ships in distress and rescue missions
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from game.player import Player, Item

@dataclass
class DistressSignal:
    """Represents a distress signal from a ship"""
    ship_name: str
    ship_type: str
    coordinates: Tuple[int, int, int]
    distress_type: str  # engine_failure, pirate_attack, medical_emergency, etc.
    severity: int  # 1-10 scale
    reward: int
    time_limit: int  # minutes
    start_time: float
    rescued: bool = False
    description: str = ""

class SOSSystem:
    """Handles distress signals and rescue missions"""
    
    def __init__(self):
        self.active_signals = {}
        self.completed_rescues = []
        self.signal_counter = 0
        
    def generate_distress_signal(self, player_coordinates: Tuple[int, int, int]) -> Optional[DistressSignal]:
        """Generate a random distress signal"""
        # 10% chance of distress signal appearing
        if random.random() > 0.1:
            return None
        
        ship_types = [
            "Cargo Freighter", "Passenger Liner", "Mining Vessel", 
            "Research Ship", "Military Patrol", "Trading Vessel",
            "Exploration Craft", "Medical Transport", "Diplomatic Envoy"
        ]
        
        distress_types = [
            "engine_failure", "pirate_attack", "medical_emergency",
            "life_support_failure", "navigational_error", "fuel_shortage",
            "structural_damage", "communication_failure", "weapon_system_malfunction"
        ]
        
        ship_name = f"{random.choice(['USS', 'FSS', 'CSS', 'MSS'])} {random.choice(['Enterprise', 'Discovery', 'Voyager', 'Endeavor', 'Pioneer', 'Explorer'])}"
        ship_type = random.choice(ship_types)
        distress_type = random.choice(distress_types)
        severity = random.randint(3, 8)
        
        # Calculate reward based on severity and ship type
        base_reward = severity * 50
        if "Military" in ship_type or "Diplomatic" in ship_type:
            base_reward *= 2
        reward = base_reward + random.randint(0, 100)
        
        # Generate coordinates near player
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        offset_z = random.randint(-20, 20)
        coordinates = (
            player_coordinates[0] + offset_x,
            player_coordinates[1] + offset_y,
            player_coordinates[2] + offset_z
        )
        
        # Generate description
        description = self._generate_distress_description(ship_name, ship_type, distress_type, severity)
        
        signal = DistressSignal(
            ship_name=ship_name,
            ship_type=ship_type,
            coordinates=coordinates,
            distress_type=distress_type,
            severity=severity,
            reward=reward,
            time_limit=random.randint(15, 45),  # 15-45 minutes
            start_time=time.time(),
            description=description
        )
        
        self.signal_counter += 1
        signal_id = f"SOS-{self.signal_counter:04d}"
        self.active_signals[signal_id] = signal
        
        return signal
    
    def _generate_distress_description(self, ship_name: str, ship_type: str, distress_type: str, severity: int) -> str:
        """Generate a description for the distress signal"""
        descriptions = {
            "engine_failure": [
                f"{ship_name} reports complete engine failure. Crew attempting emergency repairs.",
                f"Critical engine malfunction detected on {ship_name}. Systems shutting down.",
                f"{ship_name} experiencing catastrophic engine failure. Immediate assistance required."
            ],
            "pirate_attack": [
                f"{ship_name} under attack by unknown vessels. Weapons systems compromised.",
                f"Pirate vessels engaging {ship_name}. Shields failing, crew taking cover.",
                f"Multiple hostile ships attacking {ship_name}. Emergency evacuation in progress."
            ],
            "medical_emergency": [
                f"{ship_name} reports medical emergency. Several crew members injured.",
                f"Critical medical situation on {ship_name}. Life support systems failing.",
                f"{ship_name} experiencing outbreak of unknown illness. Medical supplies exhausted."
            ],
            "life_support_failure": [
                f"{ship_name} life support systems failing. Oxygen levels critical.",
                f"Atmospheric systems malfunction on {ship_name}. Crew experiencing breathing difficulties.",
                f"{ship_name} reports life support failure. Emergency protocols activated."
            ],
            "navigational_error": [
                f"{ship_name} lost in uncharted space. Navigation systems offline.",
                f"Critical navigational error on {ship_name}. Ship drifting into dangerous territory.",
                f"{ship_name} navigation systems malfunctioning. Ship unable to determine location."
            ],
            "fuel_shortage": [
                f"{ship_name} running critically low on fuel. Engines may shut down soon.",
                f"Fuel reserves depleted on {ship_name}. Ship unable to maintain course.",
                f"{ship_name} reports fuel emergency. Engines operating at minimal power."
            ],
            "structural_damage": [
                f"{ship_name} hull integrity compromised. Structural damage throughout ship.",
                f"Critical structural failure on {ship_name}. Hull breaches detected.",
                f"{ship_name} experiencing severe structural damage. Ship may break apart."
            ],
            "communication_failure": [
                f"{ship_name} communication systems offline. Unable to contact base.",
                f"Critical communication failure on {ship_name}. Ship isolated from support.",
                f"{ship_name} experiencing total communication blackout. Crew unable to send messages."
            ],
            "weapon_system_malfunction": [
                f"{ship_name} weapon systems malfunctioning. Unable to defend against threats.",
                f"Critical weapon system failure on {ship_name}. Defensive capabilities compromised.",
                f"{ship_name} reports weapon system overload. Systems may detonate."
            ]
        }
        
        base_description = random.choice(descriptions.get(distress_type, ["Unknown emergency situation."]))
        
        if severity >= 8:
            base_description += " CRITICAL SITUATION - IMMEDIATE RESPONSE REQUIRED!"
        elif severity >= 6:
            base_description += " URGENT - Time is of the essence."
        elif severity >= 4:
            base_description += " Moderate assistance needed."
        else:
            base_description += " Minor assistance requested."
        
        return base_description
    
    def get_active_signals(self) -> Dict[str, DistressSignal]:
        """Get all active distress signals"""
        return self.active_signals.copy()
    
    def get_signal_info(self, signal_id: str) -> Optional[DistressSignal]:
        """Get information about a specific distress signal"""
        return self.active_signals.get(signal_id)
    
    def calculate_distance(self, coords1: Tuple[int, int, int], coords2: Tuple[int, int, int]) -> float:
        """Calculate distance between two coordinate sets"""
        return ((coords1[0] - coords2[0])**2 + 
                (coords1[1] - coords2[1])**2 + 
                (coords1[2] - coords2[2])**2)**0.5
    
    def can_rescue(self, player_coordinates: Tuple[int, int, int], signal_id: str) -> bool:
        """Check if player can rescue this ship"""
        if signal_id not in self.active_signals:
            return False
        
        signal = self.active_signals[signal_id]
        distance = self.calculate_distance(player_coordinates, signal.coordinates)
        
        # Must be within 30 units to rescue
        return distance <= 30
    
    def attempt_rescue(self, player: Player, signal_id: str) -> Dict:
        """Attempt to rescue a ship in distress"""
        if signal_id not in self.active_signals:
            return {'success': False, 'message': 'Distress signal not found'}
        
        signal = self.active_signals[signal_id]
        
        # Check if signal is still active
        elapsed_time = (time.time() - signal.start_time) / 60
        if elapsed_time > signal.time_limit:
            return {'success': False, 'message': 'Too late! The ship has been lost.'}
        
        # Check if player is close enough
        if not self.can_rescue(player.coordinates, signal_id):
            return {'success': False, 'message': 'You are too far away to rescue this ship.'}
        
        # Check if player has required resources
        required_fuel = signal.severity * 2
        required_energy = signal.severity * 5
        
        if player.fuel < required_fuel:
            return {'success': False, 'message': f'Not enough fuel. Need {required_fuel}, have {player.fuel}'}
        
        if player.energy < required_energy:
            return {'success': False, 'message': f'Not enough energy. Need {required_energy}, have {player.energy}'}
        
        # Consume resources
        player.use_fuel(required_fuel)
        player.use_energy(required_energy)
        
        # Calculate success chance based on severity
        success_chance = max(0.1, 1.0 - (signal.severity * 0.1))
        
        if random.random() < success_chance:
            # Successful rescue
            reward = signal.reward
            bonus = int(reward * 0.2)  # 20% bonus for successful rescue
            total_reward = reward + bonus
            
            player.add_credits(total_reward)
            player.gain_experience(signal.severity * 5)
            
            # Add to completed rescues
            self.completed_rescues.append({
                'signal_id': signal_id,
                'ship_name': signal.ship_name,
                'reward': total_reward,
                'timestamp': time.time()
            })
            
            # Remove from active signals
            del self.active_signals[signal_id]
            
            return {
                'success': True,
                'message': f'Rescue successful! {signal.ship_name} thanks you for your help.',
                'reward': total_reward,
                'bonus': bonus,
                'experience': signal.severity * 5
            }
        else:
            # Failed rescue
            return {
                'success': False,
                'message': f'Rescue attempt failed. {signal.ship_name} was lost.',
                'resources_lost': True
            }
    
    def update_signals(self):
        """Update distress signals and remove expired ones"""
        current_time = time.time()
        expired_signals = []
        
        for signal_id, signal in self.active_signals.items():
            elapsed_time = (current_time - signal.start_time) / 60
            
            if elapsed_time > signal.time_limit:
                expired_signals.append(signal_id)
        
        # Remove expired signals
        for signal_id in expired_signals:
            del self.active_signals[signal_id]
    
    def get_rescue_statistics(self) -> Dict:
        """Get statistics about completed rescues"""
        if not self.completed_rescues:
            return {
                'total_rescues': 0,
                'total_rewards': 0,
                'average_reward': 0
            }
        
        total_rescues = len(self.completed_rescues)
        total_rewards = sum(rescue['reward'] for rescue in self.completed_rescues)
        average_reward = total_rewards / total_rescues
        
        return {
            'total_rescues': total_rescues,
            'total_rewards': total_rewards,
            'average_reward': average_reward
        }
    
    def get_nearby_signals(self, player_coordinates: Tuple[int, int, int], max_distance: int = 50) -> List[Tuple[str, DistressSignal, float]]:
        """Get distress signals within a certain distance"""
        nearby = []
        
        for signal_id, signal in self.active_signals.items():
            distance = self.calculate_distance(player_coordinates, signal.coordinates)
            if distance <= max_distance:
                nearby.append((signal_id, signal, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[2])
        return nearby 