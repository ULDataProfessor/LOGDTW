#!/usr/bin/env python3
"""
Negotiation Module for Multi-Step Chats and Negotiations
Handles complex negotiation scenarios with NPCs
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from game.personality import PersonalityProfile


class NegotiationState(Enum):
    """States of a negotiation"""
    INITIAL = "initial"
    COUNTER_OFFER = "counter_offer"
    HARD_BALL = "hard_ball"
    FINAL_OFFER = "final_offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WALKED_AWAY = "walked_away"


@dataclass
class NegotiationOffer:
    """Represents an offer in a negotiation"""
    offer_type: str  # "price", "trade", "service", "information", "favor"
    initial_value: float
    current_value: float
    minimum_acceptable: float
    maximum_possible: float
    terms: Dict[str, any] = field(default_factory=dict)
    
    def is_acceptable(self, value: float) -> bool:
        """Check if a value is acceptable"""
        return self.minimum_acceptable <= value <= self.maximum_possible


@dataclass
class NegotiationSession:
    """Represents an active negotiation session"""
    npc_name: str
    npc_personality: PersonalityProfile
    offer: NegotiationOffer
    state: NegotiationState = NegotiationState.INITIAL
    round: int = 0
    max_rounds: int = 5
    player_offers: List[float] = field(default_factory=list)
    npc_offers: List[float] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    relationship_impact: int = 0
    success_chance: float = 0.5  # Base chance of success
    
    def add_conversation(self, speaker: str, message: str, offer_value: Optional[float] = None):
        """Add a conversation entry"""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "round": self.round,
            "offer_value": offer_value
        })
    
    def calculate_success_chance(self, player_offer: float) -> float:
        """Calculate chance of NPC accepting offer"""
        base_chance = self.success_chance
        
        # Personality affects acceptance
        personality = self.npc_personality
        
        # Greedy NPCs are more likely to accept higher offers
        if personality.greed >= 7:
            if player_offer >= self.offer.current_value * 1.1:
                base_chance += 0.3
            elif player_offer >= self.offer.current_value:
                base_chance += 0.1
        
        # Patient NPCs are less likely to accept quickly
        if personality.patience >= 7 and self.round < 3:
            base_chance -= 0.2
        
        # Honest NPCs are more likely to accept fair offers
        if personality.honesty >= 7:
            fair_range = (self.offer.minimum_acceptable + self.offer.maximum_possible) / 2
            if abs(player_offer - fair_range) < fair_range * 0.1:
                base_chance += 0.2
        
        # Aggressive NPCs are less likely to accept low offers
        if personality.aggression >= 5:
            if player_offer < self.offer.current_value * 0.9:
                base_chance -= 0.3
        
        # Round-based adjustments
        if self.round >= self.max_rounds - 1:
            base_chance += 0.2  # More likely to accept on final round
        
        return max(0.0, min(1.0, base_chance))


class NegotiationSystem:
    """System for handling negotiations with NPCs"""
    
    def __init__(self):
        self.active_negotiations: Dict[str, NegotiationSession] = {}
    
    def start_negotiation(
        self,
        npc_name: str,
        npc_personality: PersonalityProfile,
        offer_type: str,
        initial_value: float,
        minimum_acceptable: float,
        maximum_possible: float,
        terms: Optional[Dict] = None
    ) -> NegotiationSession:
        """Start a new negotiation session"""
        offer = NegotiationOffer(
            offer_type=offer_type,
            initial_value=initial_value,
            current_value=initial_value,
            minimum_acceptable=minimum_acceptable,
            maximum_possible=maximum_possible,
            terms=terms or {}
        )
        
        session = NegotiationSession(
            npc_name=npc_name,
            npc_personality=npc_personality,
            offer=offer,
            state=NegotiationState.INITIAL
        )
        
        # Calculate initial success chance based on personality
        if npc_personality.greed >= 7:
            session.success_chance = 0.7  # Greedy NPCs are easier to negotiate with
        elif npc_personality.patience >= 7:
            session.success_chance = 0.4  # Patient NPCs are harder
        elif npc_personality.honesty >= 7:
            session.success_chance = 0.6  # Honest NPCs are reasonable
        else:
            session.success_chance = 0.5
        
        self.active_negotiations[npc_name] = session
        
        # Generate opening statement
        opening = self._generate_opening_statement(session)
        session.add_conversation(npc_name, opening)
        
        return session
    
    def _generate_opening_statement(self, session: NegotiationSession) -> str:
        """Generate opening statement based on personality"""
        personality = session.npc_personality
        offer = session.offer
        
        if personality.greed >= 7:
            return random.choice([
                f"I'm interested in {offer.offer_type}, but I need to see what you're offering.",
                f"Let's talk business. What's your best offer for {offer.offer_type}?",
                f"I'm always open to a good deal. What do you have in mind?",
            ])
        elif personality.patience >= 7:
            return random.choice([
                f"I'm in no rush. We can discuss {offer.offer_type} at length.",
                f"Take your time. I'm willing to negotiate {offer.offer_type} properly.",
                f"I believe in thorough negotiations. Let's talk about {offer.offer_type}.",
            ])
        elif personality.honesty >= 7:
            return random.choice([
                f"I'll be straight with you about {offer.offer_type}.",
                f"Let's be fair and honest about {offer.offer_type}.",
                f"I believe in fair deals. What's your offer for {offer.offer_type}?",
            ])
        elif personality.aggression >= 5:
            return random.choice([
                f"Don't waste my time. What's your offer for {offer.offer_type}?",
                f"I'm not here to chat. Make your offer for {offer.offer_type}.",
                f"Let's cut to the chase. {offer.offer_type} - what's it worth to you?",
            ])
        elif personality.cautiousness >= 7:
            return random.choice([
                f"I need to be careful about {offer.offer_type}. What are your terms?",
                f"Before we proceed with {offer.offer_type}, I need guarantees.",
                f"I'm cautious about {offer.offer_type}. Let's discuss the details.",
            ])
        else:
            return random.choice([
                f"Let's discuss {offer.offer_type}.",
                f"I'm open to negotiating {offer.offer_type}.",
                f"What's your interest in {offer.offer_type}?",
            ])
    
    def make_offer(
        self,
        npc_name: str,
        player_offer: float,
        player_message: Optional[str] = None
    ) -> Dict:
        """Player makes an offer in the negotiation"""
        if npc_name not in self.active_negotiations:
            return {
                "success": False,
                "message": "No active negotiation with this NPC."
            }
        
        session = self.active_negotiations[npc_name]
        session.round += 1
        
        # Add player's offer
        session.player_offers.append(player_offer)
        if player_message:
            session.add_conversation("Player", player_message, player_offer)
        
        # Check if offer is acceptable
        if session.offer.is_acceptable(player_offer):
            success_chance = session.calculate_success_chance(player_offer)
            
            if random.random() < success_chance:
                # NPC accepts
                session.state = NegotiationState.ACCEPTED
                session.offer.current_value = player_offer
                response = self._generate_acceptance_response(session)
                session.add_conversation(session.npc_name, response)
                
                # Relationship impact
                if player_offer >= session.offer.current_value:
                    session.relationship_impact = 5
                else:
                    session.relationship_impact = 2
                
                return {
                    "success": True,
                    "accepted": True,
                    "message": response,
                    "final_value": player_offer,
                    "relationship_change": session.relationship_impact,
                    "conversation_history": session.conversation_history
                }
            else:
                # NPC counters
                return self._generate_counter_offer(session, player_offer)
        else:
            # Offer is outside acceptable range
            if player_offer < session.offer.minimum_acceptable:
                session.state = NegotiationState.REJECTED
                response = self._generate_rejection_response(session, "too_low")
                session.add_conversation(session.npc_name, response)
                
                if session.round >= session.max_rounds:
                    return {
                        "success": False,
                        "rejected": True,
                        "message": response,
                        "conversation_history": session.conversation_history
                    }
                else:
                    return {
                        "success": False,
                        "rejected": False,
                        "message": response,
                        "conversation_history": session.conversation_history,
                        "hint": f"Try offering at least {session.offer.minimum_acceptable:.2f}"
                    }
            else:  # player_offer > maximum_possible
                session.state = NegotiationState.ACCEPTED
                response = self._generate_acceptance_response(session, "generous")
                session.add_conversation(session.npc_name, response)
                session.relationship_impact = 10
                
                return {
                    "success": True,
                    "accepted": True,
                    "message": response,
                    "final_value": player_offer,
                    "relationship_change": session.relationship_impact,
                    "conversation_history": session.conversation_history
                }
    
    def _generate_counter_offer(self, session: NegotiationSession, player_offer: float) -> Dict:
        """Generate a counter-offer from the NPC"""
        personality = session.npc_personality
        offer = session.offer
        
        # Calculate counter-offer based on personality
        if personality.greed >= 7:
            # Greedy NPCs push for more
            counter = player_offer * 1.15
        elif personality.honesty >= 7:
            # Honest NPCs make fair counters
            fair_value = (offer.minimum_acceptable + offer.maximum_possible) / 2
            counter = max(player_offer * 1.05, fair_value)
        elif personality.patience >= 7:
            # Patient NPCs don't move much
            counter = player_offer * 1.1
        elif personality.aggression >= 5:
            # Aggressive NPCs push hard
            counter = player_offer * 1.2
        else:
            counter = player_offer * 1.1
        
        # Ensure counter is within bounds
        counter = min(counter, offer.maximum_possible)
        counter = max(counter, offer.minimum_acceptable)
        
        session.npc_offers.append(counter)
        session.state = NegotiationState.COUNTER_OFFER
        session.offer.current_value = counter
        
        # Generate response
        response = self._generate_counter_response(session, counter)
        session.add_conversation(session.npc_name, response, counter)
        
        if session.round >= session.max_rounds:
            session.state = NegotiationState.FINAL_OFFER
            response += " This is my final offer."
        
        return {
            "success": False,
            "counter_offer": True,
            "message": response,
            "counter_value": counter,
            "round": session.round,
            "max_rounds": session.max_rounds,
            "conversation_history": session.conversation_history
        }
    
    def _generate_counter_response(self, session: NegotiationSession, counter_value: float) -> str:
        """Generate counter-offer response"""
        personality = session.npc_personality
        
        if personality.greed >= 7:
            return random.choice([
                f"I need {counter_value:.2f} for this. That's my bottom line.",
                f"Come on, you can do better than that. How about {counter_value:.2f}?",
                f"I'm worth more than that. {counter_value:.2f} is what I need.",
            ])
        elif personality.honesty >= 7:
            return random.choice([
                f"I think {counter_value:.2f} is a fair price for both of us.",
                f"Let's meet in the middle. How about {counter_value:.2f}?",
                f"I believe {counter_value:.2f} is reasonable. What do you think?",
            ])
        elif personality.patience >= 7:
            return random.choice([
                f"I can wait for the right offer. {counter_value:.2f} would work.",
                f"Take your time to consider. I'm asking {counter_value:.2f}.",
                f"I'm not in a hurry. {counter_value:.2f} is my offer.",
            ])
        elif personality.aggression >= 5:
            return random.choice([
                f"That's not enough! I want {counter_value:.2f}!",
                f"Don't insult me with that offer. {counter_value:.2f} or nothing!",
                f"You're wasting my time. {counter_value:.2f} - take it or leave it!",
            ])
        else:
            return random.choice([
                f"How about {counter_value:.2f}?",
                f"I could do {counter_value:.2f}.",
                f"Let's say {counter_value:.2f}.",
            ])
    
    def _generate_acceptance_response(self, session: NegotiationSession, reason: str = "normal") -> str:
        """Generate acceptance response"""
        personality = session.npc_personality
        
        if reason == "generous":
            if personality.greed >= 7:
                return random.choice([
                    "Excellent! You drive a hard bargain, but I accept!",
                    "Now that's what I'm talking about! Deal!",
                    "You've got yourself a deal!",
                ])
            else:
                return random.choice([
                    "That's very generous of you. I accept.",
                    "Thank you for the fair offer. Deal.",
                    "I appreciate your generosity. Accepted.",
                ])
        else:
            if personality.friendliness >= 7:
                return random.choice([
                    "Perfect! I'm happy with that deal.",
                    "Sounds good to me! Let's shake on it.",
                    "I'm satisfied with that. Deal!",
                ])
            elif personality.honesty >= 7:
                return random.choice([
                    "That's a fair deal. I accept.",
                    "I can work with that. Accepted.",
                    "Fair enough. Deal.",
                ])
            else:
                return random.choice([
                    "Alright, I'll take it.",
                    "Deal.",
                    "Accepted.",
                ])
    
    def _generate_rejection_response(self, session: NegotiationSession, reason: str) -> str:
        """Generate rejection response"""
        personality = session.npc_personality
        
        if reason == "too_low":
            if personality.aggression >= 5:
                return random.choice([
                    "That's insulting! Get out of here!",
                    "Are you trying to cheat me? No deal!",
                    "That's way too low! I'm done talking!",
                ])
            elif personality.greed >= 7:
                return random.choice([
                    "I need more than that. Much more.",
                    "That won't work. I need a better offer.",
                    "Come on, you can do better than that.",
                ])
            else:
                return random.choice([
                    "I'm afraid that's too low for me.",
                    "I can't accept that offer.",
                    "That doesn't work for me.",
                ])
        else:
            return "I can't accept that offer."
    
    def end_negotiation(self, npc_name: str, reason: str = "walked_away") -> Dict:
        """End a negotiation session"""
        if npc_name not in self.active_negotiations:
            return {"success": False, "message": "No active negotiation."}
        
        session = self.active_negotiations[npc_name]
        
        if reason == "walked_away":
            session.state = NegotiationState.WALKED_AWAY
            response = self._generate_walk_away_response(session)
            session.relationship_impact = -2
        else:
            response = "Negotiation ended."
        
        result = {
            "success": True,
            "message": response,
            "relationship_change": session.relationship_impact,
            "conversation_history": session.conversation_history
        }
        
        del self.active_negotiations[npc_name]
        return result
    
    def _generate_walk_away_response(self, session: NegotiationSession) -> str:
        """Generate response when player walks away"""
        personality = session.npc_personality
        
        if personality.aggression >= 5:
            return random.choice([
                "Fine! Walk away! You'll regret this!",
                "Your loss! Don't come back!",
                "I didn't want to deal with you anyway!",
            ])
        elif personality.patience >= 7:
            return random.choice([
                "Take your time. Come back when you're ready.",
                "I'll be here if you change your mind.",
                "No rush. Think it over.",
            ])
        else:
            return random.choice([
                "Alright, maybe another time.",
                "Let me know if you change your mind.",
                "Fair enough. Good luck.",
            ])
    
    def get_negotiation_status(self, npc_name: str) -> Optional[Dict]:
        """Get current negotiation status"""
        if npc_name not in self.active_negotiations:
            return None
        
        session = self.active_negotiations[npc_name]
        return {
            "npc_name": session.npc_name,
            "state": session.state.value,
            "round": session.round,
            "max_rounds": session.max_rounds,
            "current_offer": session.offer.current_value,
            "offer_range": {
                "min": session.offer.minimum_acceptable,
                "max": session.offer.maximum_possible
            },
            "conversation_history": session.conversation_history
        }

