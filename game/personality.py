#!/usr/bin/env python3
"""
Enhanced Personality System for NPCs
Provides rich personality traits that influence dialogue, behavior, and negotiations
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PersonalityTrait(Enum):
    """Core personality dimensions"""
    FRIENDLINESS = "friendliness"  # -10 to 10: How warm and welcoming
    AGGRESSION = "aggression"  # -10 to 10: How confrontational
    INTELLIGENCE = "intelligence"  # 1 to 10: How smart and analytical
    LOYALTY = "loyalty"  # -10 to 10: How trustworthy and reliable
    GREED = "greed"  # -10 to 10: How materialistic
    CURIOSITY = "curiosity"  # -10 to 10: How inquisitive
    HONESTY = "honesty"  # -10 to 10: How truthful
    PATIENCE = "patience"  # -10 to 10: How tolerant of delays
    CHARISMA = "charisma"  # -10 to 10: How persuasive and charming
    CAUTIOUSNESS = "cautiousness"  # -10 to 10: How risk-averse


@dataclass
class PersonalityProfile:
    """Complete personality profile for an NPC"""
    
    # Core traits
    friendliness: int = 0  # -10 to 10
    aggression: int = 0  # -10 to 10
    intelligence: int = 5  # 1 to 10
    loyalty: int = 0  # -10 to 10
    greed: int = 0  # -10 to 10
    curiosity: int = 0  # -10 to 10
    honesty: int = 0  # -10 to 10
    patience: int = 0  # -10 to 10
    charisma: int = 0  # -10 to 10
    cautiousness: int = 0  # -10 to 10
    
    # Derived characteristics
    personality_type: str = "neutral"  # friendly, hostile, neutral, mysterious, etc.
    speech_pattern: str = "normal"  # formal, casual, technical, poetic, gruff
    emotional_state: str = "calm"  # calm, excited, anxious, angry, happy, sad
    interests: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived characteristics from traits"""
        self._calculate_personality_type()
        self._calculate_speech_pattern()
        self._calculate_interests()
    
    def _calculate_personality_type(self):
        """Determine personality type from traits"""
        if self.friendliness >= 7:
            self.personality_type = "friendly"
        elif self.aggression >= 7:
            self.personality_type = "hostile"
        elif self.intelligence >= 8 and self.curiosity >= 5:
            self.personality_type = "mysterious"
        elif self.greed >= 7:
            self.personality_type = "greedy"
        elif self.honesty >= 7:
            self.personality_type = "honest"
        elif self.cautiousness >= 7:
            self.personality_type = "cautious"
        else:
            self.personality_type = "neutral"
    
    def _calculate_speech_pattern(self):
        """Determine speech pattern from traits"""
        if self.intelligence >= 8:
            self.speech_pattern = "technical"
        elif self.charisma >= 7:
            self.speech_pattern = "poetic"
        elif self.aggression >= 5:
            self.speech_pattern = "gruff"
        elif self.friendliness >= 7:
            self.speech_pattern = "casual"
        elif self.cautiousness >= 7:
            self.speech_pattern = "formal"
        else:
            self.speech_pattern = "normal"
    
    def _calculate_interests(self):
        """Generate interests based on traits"""
        interests = []
        if self.curiosity >= 5:
            interests.extend(["exploration", "discovery", "mysteries"])
        if self.greed >= 5:
            interests.extend(["trading", "profit", "wealth"])
        if self.intelligence >= 7:
            interests.extend(["research", "technology", "science"])
        if self.aggression >= 5:
            interests.extend(["combat", "weapons", "tactics"])
        if self.friendliness >= 5:
            interests.extend(["socializing", "stories", "gossip"])
        self.interests = interests if interests else ["general topics"]
    
    def get_greeting_modifier(self) -> str:
        """Get greeting style based on personality"""
        if self.friendliness >= 7:
            return random.choice([
                "A warm smile spreads across their face.",
                "Their eyes light up with genuine warmth.",
                "They greet you with open arms.",
            ])
        elif self.aggression >= 5:
            return random.choice([
                "They eye you suspiciously.",
                "Their hand drifts toward their weapon.",
                "They stand tense, ready for trouble.",
            ])
        elif self.cautiousness >= 7:
            return random.choice([
                "They observe you carefully before speaking.",
                "They maintain a safe distance.",
                "They speak in measured, careful tones.",
            ])
        elif self.charisma >= 7:
            return random.choice([
                "They flash a charming smile.",
                "Their presence is immediately captivating.",
                "They speak with smooth confidence.",
            ])
        else:
            return "They acknowledge your presence."
    
    def get_dialogue_tone(self) -> str:
        """Get dialogue tone based on personality"""
        if self.speech_pattern == "technical":
            return random.choice([
                "According to my analysis...",
                "The data suggests...",
                "Statistically speaking...",
            ])
        elif self.speech_pattern == "poetic":
            return random.choice([
                "Like stars in the void...",
                "As the ancient texts say...",
                "In the grand tapestry of space...",
            ])
        elif self.speech_pattern == "gruff":
            return random.choice([
                "Listen here, spacefarer...",
                "Cut the chatter and...",
                "I don't have time for...",
            ])
        elif self.speech_pattern == "casual":
            return random.choice([
                "Hey, you know what?",
                "So, I was thinking...",
                "Want to hear something cool?",
            ])
        elif self.speech_pattern == "formal":
            return random.choice([
                "If I may be so bold...",
                "With all due respect...",
                "Permit me to suggest...",
            ])
        else:
            return ""
    
    def get_negotiation_style(self) -> str:
        """Get negotiation approach based on personality"""
        if self.greed >= 7:
            return "aggressive"  # Push for maximum profit
        elif self.patience >= 7:
            return "patient"  # Willing to wait for better deal
        elif self.honesty >= 7:
            return "straightforward"  # Fair and direct
        elif self.charisma >= 7:
            return "persuasive"  # Try to charm
        elif self.aggression >= 5:
            return "intimidating"  # Use threats
        elif self.cautiousness >= 7:
            return "careful"  # Risk-averse, needs guarantees
        else:
            return "standard"  # Normal negotiation
    
    def get_reaction_to_player_action(self, action: str) -> Dict[str, any]:
        """Get NPC's reaction to player action based on personality"""
        reaction = {
            "message": "",
            "relationship_change": 0,
            "emotional_state_change": None
        }
        
        # Friendliness affects reactions
        if "insult" in action.lower() or "threaten" in action.lower():
            if self.aggression >= 5:
                reaction["message"] = random.choice([
                    "They bristle with anger.",
                    "Their eyes narrow dangerously.",
                    "They step forward aggressively.",
                ])
                reaction["relationship_change"] = -10 - self.aggression
                reaction["emotional_state_change"] = "angry"
            elif self.cautiousness >= 7:
                reaction["message"] = random.choice([
                    "They back away cautiously.",
                    "They look for an escape route.",
                    "They try to de-escalate the situation.",
                ])
                reaction["relationship_change"] = -5
                reaction["emotional_state_change"] = "anxious"
            else:
                reaction["message"] = "They seem hurt by your words."
                reaction["relationship_change"] = -5
        
        elif "compliment" in action.lower() or "praise" in action.lower():
            if self.friendliness >= 5:
                reaction["message"] = random.choice([
                    "They beam with happiness.",
                    "Their face lights up.",
                    "They seem genuinely pleased.",
                ])
                reaction["relationship_change"] = 5 + self.friendliness
                reaction["emotional_state_change"] = "happy"
            elif self.charisma >= 7:
                reaction["message"] = "They accept the compliment gracefully."
                reaction["relationship_change"] = 3
            else:
                reaction["message"] = "They seem slightly pleased."
                reaction["relationship_change"] = 2
        
        elif "offer_trade" in action.lower() or "deal" in action.lower():
            if self.greed >= 7:
                reaction["message"] = random.choice([
                    "Their eyes gleam with interest.",
                    "They lean forward eagerly.",
                    "They're clearly interested in profit.",
                ])
                reaction["relationship_change"] = 3
            elif self.honesty >= 7:
                reaction["message"] = "They consider the offer carefully and fairly."
                reaction["relationship_change"] = 2
            else:
                reaction["message"] = "They consider your offer."
                reaction["relationship_change"] = 1
        
        return reaction
    
    def to_dict(self) -> Dict:
        """Convert personality to dictionary"""
        return {
            "friendliness": self.friendliness,
            "aggression": self.aggression,
            "intelligence": self.intelligence,
            "loyalty": self.loyalty,
            "greed": self.greed,
            "curiosity": self.curiosity,
            "honesty": self.honesty,
            "patience": self.patience,
            "charisma": self.charisma,
            "cautiousness": self.cautiousness,
            "personality_type": self.personality_type,
            "speech_pattern": self.speech_pattern,
            "emotional_state": self.emotional_state,
            "interests": self.interests,
            "dislikes": self.dislikes,
        }
    
    @classmethod
    def from_base_personality(cls, base: str) -> "PersonalityProfile":
        """Create personality profile from base personality type"""
        profile = cls()
        
        if base == "friendly":
            profile.friendliness = random.randint(6, 10)
            profile.charisma = random.randint(4, 8)
            profile.aggression = random.randint(-5, 0)
            profile.honesty = random.randint(3, 8)
        elif base == "hostile":
            profile.aggression = random.randint(6, 10)
            profile.friendliness = random.randint(-10, -2)
            profile.cautiousness = random.randint(3, 8)
            profile.honesty = random.randint(-5, 2)
        elif base == "mysterious":
            profile.curiosity = random.randint(6, 10)
            profile.intelligence = random.randint(7, 10)
            profile.cautiousness = random.randint(5, 10)
            profile.honesty = random.randint(-3, 3)
        elif base == "greedy":
            profile.greed = random.randint(7, 10)
            profile.friendliness = random.randint(-2, 5)
            profile.honesty = random.randint(-5, 2)
            profile.patience = random.randint(-5, 2)
        elif base == "honest":
            profile.honesty = random.randint(7, 10)
            profile.friendliness = random.randint(3, 8)
            profile.loyalty = random.randint(5, 10)
            profile.greed = random.randint(-5, 2)
        elif base == "cautious":
            profile.cautiousness = random.randint(7, 10)
            profile.intelligence = random.randint(5, 9)
            profile.patience = random.randint(5, 10)
            profile.aggression = random.randint(-5, 2)
        else:  # neutral
            profile.friendliness = random.randint(-2, 5)
            profile.aggression = random.randint(-3, 3)
            profile.intelligence = random.randint(3, 7)
            profile.honesty = random.randint(-2, 5)
        
        # Add some randomness to all traits
        for trait_name in ["friendliness", "aggression", "intelligence", "loyalty", 
                          "greed", "curiosity", "honesty", "patience", "charisma", "cautiousness"]:
            current_value = getattr(profile, trait_name)
            variation = random.randint(-2, 2)
            new_value = max(-10, min(10, current_value + variation))
            if trait_name == "intelligence":
                new_value = max(1, min(10, new_value))
            setattr(profile, trait_name, new_value)
        
        profile.__post_init__()  # Recalculate derived characteristics
        return profile

