"""
NPC system for LOGDTW2002
Handles NPCs, conversations, and interactive features with enhanced intelligence
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from game.player import Player
from game.quests import QuestSystem
from game.story_content import get_character_backstory
from game.personality import PersonalityProfile
from game.negotiation import NegotiationSystem, NegotiationState
from game.npc_stories import get_story_library, StoryType


@dataclass
class DialogueNode:
    """Represents a node within a dialogue tree."""

    text: str
    choices: Dict[str, str] = field(default_factory=dict)
    quest_id: Optional[str] = None
    faction_change: Optional[Dict[str, int]] = None


@dataclass
class NPC:
    """Represents an NPC in the game with enhanced intelligence"""

    name: str
    npc_type: str  # trader, pirate, scientist, official, etc.
    personality: str  # friendly, hostile, neutral, mysterious
    location: str
    dialogue: Dict[str, List[str]] = None
    quests: List[str] = None
    services: List[str] = None
    faction: str = "Neutral"
    reputation: int = 0  # -100 to 100
    personality_traits: Dict[str, int] = field(default_factory=dict)
    relationships: Dict[str, int] = field(default_factory=dict)
    dialogue_tree: Dict[str, DialogueNode] = field(default_factory=dict)
    personality_profile: Optional[PersonalityProfile] = None  # Enhanced personality
    
    # Enhanced: Memory and learning
    memory: Dict[str, any] = field(default_factory=dict)  # Remember interactions
    conversation_history: List[Dict] = field(default_factory=list)  # Track conversations
    player_interactions: int = 0  # Count interactions with player
    last_interaction_time: float = 0.0  # Timestamp of last interaction
    learned_preferences: Dict[str, any] = field(default_factory=dict)  # Learn player preferences

    def __post_init__(self):
        if self.dialogue is None:
            self.dialogue = {}
        if self.quests is None:
            self.quests = []
        if self.services is None:
            self.services = []

    def adjust_relationship(self, target: str, amount: int) -> None:
        """Modify relationship score with player or other NPC"""
        self.relationships[target] = self.relationships.get(target, 0) + amount
        # Enhanced: Remember significant relationship changes
        if abs(amount) >= 10:
            self.memory[f"relationship_change_{target}"] = {
                "amount": amount,
                "timestamp": time.time()
            }

    def get_relationship(self, target: str) -> int:
        """Get current relationship score"""
        return self.relationships.get(target, 0)
    
    def remember_interaction(self, player_name: str, interaction_type: str, details: Dict = None):
        """Remember an interaction with the player"""
        import time
        self.player_interactions += 1
        self.last_interaction_time = time.time()
        
        memory_key = f"interaction_{self.player_interactions}"
        self.memory[memory_key] = {
            "player": player_name,
            "type": interaction_type,
            "details": details or {},
            "timestamp": time.time()
        }
        
        # Enhanced: Learn from interactions
        if interaction_type == "trade":
            if details:
                item = details.get("item")
                if item:
                    self.learned_preferences[f"player_likes_{item}"] = True
        elif interaction_type == "quest_completed":
            self.learned_preferences["player_helpful"] = True
            self.adjust_relationship(player_name, 5)
    
    def get_personalized_greeting(self, player_name: str) -> str:
        """Generate a personalized greeting based on relationship and memory"""
        relationship = self.get_relationship(player_name)
        
        # Use personality profile if available
        greeting_modifier = ""
        if self.personality_profile:
            greeting_modifier = self.personality_profile.get_greeting_modifier()
        
        # Enhanced: Use memory to personalize
        if self.player_interactions > 0:
            if relationship > 50:
                return f"Ah, {player_name}! Always a pleasure to see you again, my friend."
            elif relationship > 20:
                return f"Hello {player_name}, good to see you back."
            elif relationship < -20:
                return f"{player_name}... I remember you. What do you want?"
            else:
                return f"Greetings, {player_name}."
        else:
            # First meeting
            if self.personality == "friendly":
                return f"Welcome, traveler! I'm {self.name}. How can I help you?"
            elif self.personality == "hostile":
                return f"What do you want, {player_name}?"
            else:
                return f"Hello. I'm {self.name}."


class NPCSystem:
    """NPC system with enhanced personality and negotiation support"""

    def __init__(self, quest_system=None, trading_system=None):
        self.npcs = {}
        self.conversations = {}
        self.npc_templates = self._create_npc_templates()
        self.quest_system = quest_system
        self.trading_system = trading_system
        self.negotiation_system = NegotiationSystem()  # Add negotiation system

    def set_systems(self, quest_system, trading_system):
        """Link external systems after initialization"""
        self.quest_system = quest_system
        self.trading_system = trading_system

    def _convert_choice_to_quest(self, player: Player, npc: NPC):
        """Convert dialogue choice into a quest offer if possible"""
        if not self.quest_system:
            return None
        quests = self.quest_system.get_available_quests(player, npc.location)
        if quests:
            return random.choice(quests)
        return None

    def _apply_market_modifier(self, npc: NPC, modifier: float = 0.9):
        """Apply a market price modifier via the trading system"""
        if not self.trading_system:
            return None
        self.trading_system.apply_price_modifier(npc.location, modifier)
        return modifier

    def _generate_personality_traits(self, base: str) -> Dict[str, int]:
        """Generate nuanced personality traits based on base personality"""
        # Use the new PersonalityProfile system
        profile = PersonalityProfile.from_base_personality(base)
        return profile.to_dict()

    def _create_dialogue_tree(self, dialogue: Dict[str, List[str]]) -> Dict[str, DialogueNode]:
        """Create a simple dialogue tree structure using ``DialogueNode`` objects."""

        start_text = random.choice(dialogue.get("greeting", ["Hello."]))
        tree: Dict[str, DialogueNode] = {
            "start": DialogueNode(
                text=start_text,
                choices={
                    "Ask about rumors": "rumors",
                    "Ask for secrets": "secrets",
                    "Say goodbye": "farewell",
                },
            )
        }

        tree["rumors"] = DialogueNode(
            text=random.choice(dialogue.get("rumors", ["Nothing to share."])),
            choices={"Back": "start"},
        )
        tree["secrets"] = DialogueNode(
            text=random.choice(dialogue.get("secrets", ["No secrets today."])),
            choices={"Back": "start"},
        )
        tree["farewell"] = DialogueNode(
            text=random.choice(dialogue.get("farewell", ["Farewell."])),
            choices={},
        )
        return tree

    def _create_npc_templates(self) -> Dict:
        """Create NPC templates with rich dialogue and hidden information"""
        return {
            "trader": {
                "personality": "friendly",
                "dialogue": {
                    "greeting": [
                        "Welcome, traveler! Looking for some good deals?",
                        "Ah, a customer! What can I interest you in today?",
                        "Greetings! My wares are the finest in the sector.",
                        "Well met, spacefarer! I've traveled these sectors for years.",
                    ],
                    "farewell": [
                        "Safe travels, friend!",
                        "Come back soon!",
                        "May your journey be profitable!",
                        "Watch out for those pirates in sector 7, they're getting bolder.",
                    ],
                    "trade": [
                        "I have some excellent merchandise.",
                        "This is top quality, I assure you.",
                        "You won't find better prices anywhere.",
                        "Heard the market in Alpha Centauri is paying double for Ammolite these days.",
                    ],
                    "rumors": [
                        "Rumor has it there's a hidden trading post in the asteroid belt.",
                        "The Federation is building something big in sector 12. Very hush-hush.",
                        "I heard a merchant found ancient alien artifacts in the outer rim.",
                        "There's talk of a new Genesis Torpedo being developed. Creates entire planets!",
                        "The stock market is rigged, I tell you. The big players know everything in advance.",
                        "Some say there's a secret holodeck program that can predict market movements.",
                    ],
                    "secrets": [
                        "Between you and me, the best deals are always on Tuesdays when the inspectors are off duty.",
                        "I've seen things in the deep sectors that would make your hair stand on end.",
                        "There's a reason why some sectors are marked 'unexplored' on the maps. They're not empty.",
                        "The Genesis Torpedo? That's not just a rumor. I've seen the blueprints.",
                        "Ever wonder why some planets just... appear? The Federation doesn't want you to know.",
                    ],
                },
                "services": ["trading", "information", "rumors"],
                "conversation": {
                    "start": DialogueNode(
                        text="Care to trade or looking for work?",
                        choices={"Ask about work": "offer", "Say goodbye": "farewell"},
                    ),
                    "offer": DialogueNode(
                        text="I need someone to deliver supplies to Luna Base. Interested?",
                        choices={"Yes": "accept", "No": "decline"},
                    ),
                    "accept": DialogueNode(
                        text="Great! I'll mark the coordinates for you.",
                        quest_id="delivery_001",
                        choices={"Goodbye": "farewell"},
                    ),
                    "decline": DialogueNode(
                        text="Maybe next time then.",
                        faction_change={"Traders": -5},
                        choices={"Goodbye": "farewell"},
                    ),
                    "farewell": DialogueNode(text="Safe travels, friend!", choices={}),
                },
            },
            "pirate": {
                "personality": "hostile",
                "dialogue": {
                    "greeting": [
                        "Well, well... what do we have here?",
                        "You're in my territory now, friend.",
                        "Hand over your cargo and no one gets hurt.",
                        "Look what the solar winds blew in.",
                    ],
                    "farewell": [
                        "You're lucky I'm in a good mood.",
                        "Don't let me catch you here again.",
                        "Next time won't be so pleasant.",
                        "Tell your friends about this encounter. If you survive.",
                    ],
                    "threat": [
                        "You're making a big mistake.",
                        "I don't think you understand the situation.",
                        "This can end badly for you.",
                        "I've seen better pilots in a kindergarten.",
                    ],
                    "rumors": [
                        "The Federation thinks they control everything. They don't know what's really out there.",
                        "There are things in the void that would make your nightmares look like bedtime stories.",
                        "Some sectors are forbidden for a reason. Not because of regulations - because of what lives there.",
                        "The Genesis Torpedo? We pirates have our own version. Creates chaos instead of order.",
                        "Ever heard of the Phantom Fleet? They say it's made of ships that never existed.",
                    ],
                    "secrets": [
                        "The real money isn't in cargo - it's in information. I know where the bodies are buried.",
                        "There's a reason why some distress signals are never answered. They're not from ships.",
                        "The Federation's 'exploration' missions? They're looking for something specific. Something old.",
                        "Some planets aren't planets at all. They're something else entirely.",
                        "The holodeck programs? Some of them are based on real events. Very real events.",
                    ],
                },
                "services": ["smuggling", "illegal_goods", "dangerous_information"],
            },
            "scientist": {
                "personality": "neutral",
                "dialogue": {
                    "greeting": [
                        "Fascinating! Another traveler from the void.",
                        "Greetings. I'm conducting important research.",
                        "Welcome to our research facility.",
                        "Ah, a test subject! I mean... welcome, citizen.",
                    ],
                    "farewell": [
                        "Safe journey through the stars.",
                        "May your discoveries be fruitful.",
                        "Return if you have interesting data.",
                        "Don't let the void drive you mad. It's already driven enough people mad.",
                    ],
                    "research": [
                        "The universe holds many mysteries.",
                        "My research could change everything.",
                        "There's so much we don't understand.",
                        "The Genesis Torpedo is just the beginning. We're working on something much bigger.",
                    ],
                    "rumors": [
                        "My colleagues have discovered something disturbing about the sector maps.",
                        "There are patterns in the void that suggest intelligent design. Or something worse.",
                        "The Federation's 'standard' measurements? They're not standard at all.",
                        "Some of the holodeck programs are based on real historical events. Very classified events.",
                        "The stock market fluctuations aren't random. There's a mathematical pattern that defies explanation.",
                    ],
                    "secrets": [
                        "The Genesis Torpedo technology? It's not human. We found it in an ancient alien ruin.",
                        "Some sectors are marked 'unexplored' because what we found there was too disturbing to report.",
                        "The Federation's 'exploration' is actually a cover for something else. Something they're afraid of.",
                        "There are beings in the void that don't follow our laws of physics. Or any laws at all.",
                        "The holodeck? It's not just for entertainment. It's a training ground for something bigger.",
                    ],
                },
                "services": ["research", "information", "classified_data"],
            },
            "official": {
                "personality": "neutral",
                "dialogue": {
                    "greeting": [
                        "Welcome to our station. Papers, please.",
                        "Greetings, citizen. How may I assist you?",
                        "Official business only, please.",
                        "Ah, another traveler. Let me check your credentials.",
                    ],
                    "farewell": [
                        "Keep your papers in order.",
                        "Safe travels, citizen.",
                        "Remember to follow regulations.",
                        "Stay within the approved sectors. For your own safety.",
                    ],
                    "official": [
                        "All procedures must be followed.",
                        "Regulations are for everyone's safety.",
                        "The law is clear on this matter.",
                        "Some information is classified for a reason.",
                    ],
                    "rumors": [
                        "The Federation is expanding into new sectors. For 'exploration' purposes.",
                        "There have been... incidents in the outer sectors. Best to stay in approved areas.",
                        "The Genesis Torpedo program is highly classified. For good reason.",
                        "Some distress signals are being ignored. Official policy, I'm afraid.",
                        "The stock market regulations are being tightened. Too many 'anomalies' lately.",
                    ],
                    "secrets": [
                        "Between you and me, some of those 'unexplored' sectors aren't unexplored at all.",
                        "The Federation has found things in the void that would make your blood run cold.",
                        "There's a reason why some holodeck programs are restricted. They're based on real events.",
                        "The Genesis Torpedo? That's just the beginning. We're working on something that can create entire galaxies.",
                        "Some of the 'NPCs' you meet aren't what they appear to be. The Federation is watching everything.",
                    ],
                },
                "services": ["bureaucracy", "permits", "classified_access"],
            },
            "entertainer": {
                "personality": "friendly",
                "dialogue": {
                    "greeting": [
                        "Welcome to the show!",
                        "Hey there, star traveler!",
                        "Ready for some entertainment?",
                        "Ah, a new face! Let me tell you a story.",
                    ],
                    "farewell": [
                        "Come back for more shows!",
                        "The stage is always open!",
                        "Keep the music playing!",
                        "Remember, the best stories are the ones that are true.",
                    ],
                    "performance": [
                        "The crowd loves this one!",
                        "Let me show you something special.",
                        "This is my best material.",
                        "This story is based on real events. Very real events.",
                    ],
                    "rumors": [
                        "I've performed in every sector. Seen things that would make your hair stand on end.",
                        "The best stories come from the outer rim. Where the Federation doesn't go.",
                        "Some of my material is based on real events. The Federation doesn't like that.",
                        "There are holodeck programs that are so realistic, you can't tell they're simulations.",
                        "The Genesis Torpedo? I wrote a song about it. The Federation banned it.",
                    ],
                    "secrets": [
                        "Between performances, I've seen things in the void that defy explanation.",
                        "Some of the 'entertainment' in the holodeck is based on classified Federation missions.",
                        "The real story of the Genesis Torpedo? It's not what the official records say.",
                        "There are beings in the void that communicate through music. Very disturbing music.",
                        "The Federation's 'exploration' missions? They're looking for something specific. Something that sings.",
                    ],
                },
                "services": ["entertainment", "holodeck", "stories"],
            },
            "mystic": {
                "personality": "mysterious",
                "dialogue": {
                    "greeting": [
                        "The void speaks to those who listen...",
                        "Ah, a seeker of truth in the darkness.",
                        "The stars have foretold your arrival.",
                        "You carry the weight of destiny, traveler.",
                    ],
                    "farewell": [
                        "May the void guide your path.",
                        "The stars will remember your name.",
                        "Seek truth in the darkness.",
                        "The Genesis Torpedo is not what it seems...",
                    ],
                    "prophecy": [
                        "I see patterns in the void that others cannot.",
                        "The Federation's maps are incomplete. There are places they dare not go.",
                        "Some sectors are not empty - they are waiting.",
                        "The holodeck programs are windows into other realities.",
                        "The Genesis Torpedo will awaken something ancient and terrible.",
                    ],
                    "secrets": [
                        "The void is not empty. It is full of voices that speak in silence.",
                        "The Federation fears what they cannot control. The void cannot be controlled.",
                        "Some of the 'NPCs' you meet are not what they appear to be.",
                        "The Genesis Torpedo technology is older than humanity itself.",
                        "There are beings in the void that have been waiting for the Genesis Torpedo to be used.",
                    ],
                },
                "services": ["prophecy", "mystical_guidance", "void_knowledge"],
            },
        }

    def create_npc(self, name: str, npc_type: str, location: str, faction: str = "Neutral") -> NPC:
        """Create a new NPC"""
        template = self.npc_templates.get(npc_type, self.npc_templates["trader"])

        dialogue_tree = template.get("conversation") or self._create_dialogue_tree(
            template["dialogue"]
        )

        npc = NPC(
            name=name,
            npc_type=npc_type,
            personality=template["personality"],
            location=location,
            dialogue=template["dialogue"],
            services=template["services"],
            faction=faction,
            personality_traits=self._generate_personality_traits(template["personality"]),
            dialogue_tree=dialogue_tree,
            personality_profile=PersonalityProfile.from_base_personality(template["personality"]),
        )

        self.npcs[name] = npc
        return npc

    def get_dialogue_options(self, npc: NPC, node: str = "start") -> Dict[str, str]:
        """Get available dialogue options for a given node"""
        node_data = npc.dialogue_tree.get(node, {})
        return {key: data["text"] for key, data in node_data.get("options", {}).items()}

    def update_behavior(self, world_events: List[str]) -> None:
        """Update NPC behavior based on global world events"""
        for event in world_events:
            for npc in self.npcs.values():
                if event == "market_crash" and npc.npc_type == "trader":
                    npc.dialogue.setdefault("rumors", []).append(
                        "The market crash has everyone on edge."
                    )
                if event == "pirate_activity" and npc.npc_type == "pirate":
                    npc.adjust_relationship("player", -5)

    def get_npcs_at_location(self, location: str) -> List[NPC]:
        """Get all NPCs at a specific location"""
        return [npc for npc in self.npcs.values() if npc.location == location]

    def get_npc_backstory(self, npc_name: str) -> Optional[str]:
        """Get backstory for an NPC if available"""
        backstory_data = get_character_backstory(npc_name)
        if backstory_data:
            return backstory_data.backstory
        return None

    def start_conversation(
        self,
        player: Player,
        npc_name: str,
        quest_system: Optional[QuestSystem] = None,
        choices: Optional[List[str]] = None,
    ) -> Dict:
        """Start a conversation with an NPC using a dialogue tree with enhanced intelligence.

        Parameters
        ----------
        player: Player
            The player engaging in conversation.
        npc_name: str
            Name of the NPC to talk to.
        quest_system: QuestSystem, optional
            Quest system to allow dialogue nodes to trigger quests.
        choices: list[str], optional
            Pre-determined choices for automated conversations (used in tests).

        Returns
        -------
        dict
            Contains conversation history and success state.
        """

        if npc_name not in self.npcs:
            return {"success": False, "message": "NPC not found"}

        npc = self.npcs[npc_name]

        # Enhanced: Check relationship and memory
        relationship = npc.get_relationship(player.name)
        if npc.personality == "hostile" and relationship < -50:
            return {"success": False, "message": f"{npc.name} refuses to talk to you."}
        
        # Enhanced: Use personalized greeting
        greeting = npc.get_personalized_greeting(player.name)
        
        # Enhanced: Remember this interaction
        npc.remember_interaction(player.name, "conversation", {
            "location": npc.location,
            "relationship": relationship
        })

        history: List[str] = []
        history.append(f"{npc.name}: {greeting}")
        current = "start"
        choice_iter = iter(choices) if choices else None

        while current:
            node = npc.dialogue_tree.get(current)
            if not node:
                break

            if current != "start":  # Don't repeat greeting
                history.append(f"{npc.name}: {node.text}")

            if node.quest_id and quest_system:
                quest_system.accept_quest(player, node.quest_id)
                npc.remember_interaction(player.name, "quest_offered", {"quest_id": node.quest_id})
            if node.faction_change:
                for faction, change in node.faction_change.items():
                    player.reputation[faction] = player.reputation.get(faction, 0) + change

            if not node.choices:
                break

            options = list(node.choices.keys())
            if choice_iter:
                try:
                    chosen_key = next(choice_iter)
                except StopIteration:
                    break
                if chosen_key not in node.choices:
                    break
            else:
                for idx, opt in enumerate(options, 1):
                    print(f"{idx}. {opt}")
                try:
                    selection = int(input("Choose an option: ")) - 1
                    chosen_key = options[selection]
                except (ValueError, IndexError):
                    print("Invalid choice.")
                    continue

            current = node.choices[chosen_key]
        
        # Enhanced: Store conversation in history
        npc.conversation_history.append({
            "player": player.name,
            "history": history,
            "timestamp": time.time()
        })

        return {"success": True, "history": history, "npc": npc, "greeting": greeting}

    def get_conversation_options(self, npc: NPC) -> List[str]:
        """Get available conversation options"""
        options = ["Ask about services", "Ask about location", "Ask about rumors"]

        # Add type-specific options
        if npc.npc_type == "trader":
            options.extend(["Browse goods", "Negotiate prices", "Ask about trade secrets", "Ask for a story"])
        elif npc.npc_type == "scientist":
            options.extend(["Discuss research", "Share discoveries", "Ask about classified data", "Ask for a story"])
        elif npc.npc_type == "entertainer":
            options.extend(["Request performance", "Book holodeck", "Ask for stories", "Ask for a story"])
        elif npc.npc_type == "official":
            options.extend(
                ["Request permits", "File complaints", "Ask about classified information", "Ask for a story"]
            )
        elif npc.npc_type == "pirate":
            options.extend(
                ["Negotiate passage", "Offer tribute", "Ask about dangerous information", "Ask for a story"]
            )
        elif npc.npc_type == "mystic":
            options.extend(["Seek prophecy", "Ask about the void", "Request mystical guidance", "Ask for a story"])
        
        # All NPCs can tell stories, so add it as a general option if not already there
        if "Ask for a story" not in options:
            options.append("Ask for a story")

        # Add secret dialogue option (random chance)
        if random.random() < 0.3:  # 30% chance
            options.append("Ask about secrets")

        options.append("End conversation")
        return options

    def handle_conversation_choice(self, player: Player, npc: NPC, choice: str) -> Dict:
        """Handle player's conversation choice"""
        if choice == "Ask about services":
            result = self._handle_services_inquiry(npc)
        elif choice == "Ask about location":
            result = self._handle_location_inquiry(npc)
        elif choice == "Ask about rumors":
            result = self._handle_rumors_inquiry(player, npc)
        elif choice == "Ask about secrets":
            result = self._handle_secrets_inquiry(npc)
        elif choice == "Browse goods" and npc.npc_type == "trader":
            result = self._handle_browse_goods(npc)
        elif choice == "Negotiate prices" and npc.npc_type == "trader":
            result = self._handle_negotiate_prices(player, npc)
        elif choice == "Ask about trade secrets" and npc.npc_type == "trader":
            result = self._handle_trade_secrets(npc)
        elif choice == "Discuss research" and npc.npc_type == "scientist":
            result = self._handle_discuss_research(npc)
        elif choice == "Ask about classified data" and npc.npc_type == "scientist":
            result = self._handle_classified_data(npc)
        elif choice == "Request performance" and npc.npc_type == "entertainer":
            result = self._handle_request_performance(npc)
        elif choice == "Ask for stories" and npc.npc_type == "entertainer":
            result = self._handle_stories_request(npc)
        elif choice == "Ask for a story" or choice == "Tell me a story":
            result = self._handle_stories_request(npc)
        elif choice == "Ask about classified information" and npc.npc_type == "official":
            result = self._handle_classified_information(npc)
        elif choice == "Ask about dangerous information" and npc.npc_type == "pirate":
            result = self._handle_dangerous_information(npc)
        elif choice == "Seek prophecy" and npc.npc_type == "mystic":
            result = self._handle_prophecy_request(npc)
        elif choice == "Ask about the void" and npc.npc_type == "mystic":
            result = self._handle_void_inquiry(npc)
        elif choice == "Request mystical guidance" and npc.npc_type == "mystic":
            result = self._handle_mystical_guidance(npc)
        elif choice == "End conversation":
            result = self._handle_end_conversation(npc)
        else:
            result = {"message": "That option is not available."}

        if result.get("rep_change"):
            npc.adjust_relationship(player.name, result["rep_change"])
        return result

    def _handle_services_inquiry(self, npc: NPC) -> Dict:
        """Handle services inquiry"""
        services_text = f"{npc.name} offers the following services:\n"
        for service in npc.services:
            services_text += f"• {service.title()}\n"

        return {"message": services_text}

    def _handle_location_inquiry(self, npc: NPC) -> Dict:
        """Handle location inquiry"""
        location_info = [
            f"{npc.name} tells you about {npc.location}:",
            "This is a busy trading hub with many opportunities.",
            "The locals are mostly friendly, but watch out for pirates.",
            "There's always something interesting happening here.",
        ]

        return {"message": "\n".join(location_info)}

    def _handle_rumors_inquiry(self, player: Player, npc: NPC) -> Dict:
        """Handle rumors inquiry - may trigger quests or market effects"""
        if "rumors" in npc.dialogue:
            rumor = random.choice(npc.dialogue["rumors"])
            response = {"message": f"{npc.name} shares a rumor: {rumor}", "rep_change": 1}
        else:
            generic_rumors = [
                "I heard there's a new trade route opening up.",
                "Rumors say there's a hidden pirate base nearby.",
                "Some say there's a mysterious alien artifact in the sector.",
                "I've heard whispers about a secret research facility.",
                "There's talk of a massive space battle coming.",
                "Some claim there's a lost colony out there somewhere.",
            ]
            rumor = random.choice(generic_rumors)
            response = {"message": f"{npc.name} shares a rumor: {rumor}", "rep_change": 1}

        quest = self._convert_choice_to_quest(player, npc)
        if quest:
            response["quest_offer"] = quest.id
            response["message"] += f" They mention a mission: {quest.name}."

        if npc.npc_type == "trader":
            modifier = self._apply_market_modifier(npc)
            if modifier:
                response["price_modifier"] = modifier
                response["message"] += " Market prices seem more favorable now."

        return response

    def _handle_browse_goods(self, npc: NPC) -> Dict:
        """Handle browsing goods"""
        goods = [
            "Rare minerals from the outer sectors",
            "Advanced technology from the core worlds",
            "Exotic spices from distant planets",
            "Precious metals and gems",
            "Strange alien artifacts",
        ]

        goods_text = f"{npc.name} shows you their wares:\n"
        for good in random.sample(goods, 3):
            goods_text += f"• {good}\n"

        return {"message": goods_text}

    def _handle_negotiate_prices(self, player: Player, npc: NPC) -> Dict:
        """Handle price negotiation - now uses negotiation system"""
        if player.credits < 100:
            return {"message": f"{npc.name} looks unimpressed with your credit balance."}

        # Use negotiation system for multi-step negotiation
        if npc.personality_profile is None:
            npc.personality_profile = PersonalityProfile.from_base_personality(npc.personality)
        
        # Start negotiation for a discount
        base_price = 1000  # Example base price
        session = self.negotiation_system.start_negotiation(
            npc_name=npc.name,
            npc_personality=npc.personality_profile,
            offer_type="discount",
            initial_value=base_price,
            minimum_acceptable=base_price * 0.85,  # 15% discount max
            maximum_possible=base_price * 0.95,  # 5% discount min
        )
        
        return {
            "message": session.conversation_history[0]["message"],
            "negotiation_started": True,
            "npc_name": npc.name,
            "offer_range": {
                "min": session.offer.minimum_acceptable,
                "max": session.offer.maximum_possible
            }
        }
    
    def _handle_start_negotiation(self, player: Player, npc: NPC, negotiation_type: str) -> Dict:
        """Start a new negotiation session"""
        if npc.personality_profile is None:
            npc.personality_profile = PersonalityProfile.from_base_personality(npc.personality)
        
        # Determine negotiation parameters based on type
        if "price" in negotiation_type.lower() or "discount" in negotiation_type.lower():
            base_value = 1000
            min_value = base_value * 0.85
            max_value = base_value * 0.95
            offer_type = "discount"
        elif "trade" in negotiation_type.lower():
            base_value = 500
            min_value = base_value * 0.8
            max_value = base_value * 1.2
            offer_type = "trade"
        else:
            base_value = 100
            min_value = base_value * 0.9
            max_value = base_value * 1.1
            offer_type = "service"
        
        session = self.negotiation_system.start_negotiation(
            npc_name=npc.name,
            npc_personality=npc.personality_profile,
            offer_type=offer_type,
            initial_value=base_value,
            minimum_acceptable=min_value,
            maximum_possible=max_value,
        )
        
        return {
            "message": session.conversation_history[0]["message"],
            "negotiation_started": True,
            "npc_name": npc.name,
            "offer_range": {
                "min": session.offer.minimum_acceptable,
                "max": session.offer.maximum_possible
            },
            "round": session.round,
            "max_rounds": session.max_rounds
        }

    def _handle_discuss_research(self, npc: NPC) -> Dict:
        """Handle research discussion"""
        research_topics = [
            "The nature of subspace communication",
            "Advanced propulsion systems",
            "Alien civilizations and their technology",
            "The mysteries of dark matter",
            "Time dilation effects in deep space",
        ]

        topic = random.choice(research_topics)
        return {"message": f"{npc.name} discusses {topic} with great enthusiasm."}

    def _handle_request_performance(self, npc: NPC) -> Dict:
        """Handle performance request"""
        performances = [
            "A dramatic space opera",
            "A comedy about life on space stations",
            "A musical about star travel",
            "A mystery set in deep space",
        ]

        performance = random.choice(performances)
        return {"message": f"{npc.name} offers to perform '{performance}' for you."}

    def _handle_book_holodeck(self, player: Player, npc: NPC) -> Dict:
        """Handle holodeck booking"""
        if player.credits < 50:
            return {"message": f"{npc.name} says holodeck time costs 50 credits."}

        programs = [
            "Beach Resort Simulation",
            "Mountain Adventure",
            "Historical Battle Reenactment",
            "Alien World Exploration",
            "Space Battle Simulation",
        ]

        program = random.choice(programs)
        return {"message": f"{npc.name} books you for '{program}' on the holodeck."}

    def _handle_end_conversation(self, npc: NPC) -> Dict:
        """Handle ending conversation"""
        farewell = random.choice(npc.dialogue.get("farewell", ["Goodbye."]))
        return {"message": f"{npc.name}: {farewell}", "end_conversation": True}

    def generate_random_npcs(self, location: str, num_npcs: int = 3) -> List[NPC]:
        """Generate random NPCs for a location"""
        npc_types = list(self.npc_templates.keys())
        npc_names = [
            "Captain",
            "Commander",
            "Doctor",
            "Professor",
            "Trader",
            "Merchant",
            "Pilot",
            "Engineer",
            "Technician",
            "Guard",
            "Official",
            "Scientist",
            "Artist",
            "Musician",
            "Chef",
            "Mystic",
            "Oracle",
            "Seer",
            "Prophet",
            "Sage",
        ]

        npcs = []
        for i in range(num_npcs):
            npc_type = random.choice(npc_types)
            name = f"{random.choice(npc_names)} {chr(65 + i)}"
            faction = random.choice(
                ["Federation", "Pirates", "Scientists", "Traders", "Neutral", "Mystics"]
            )

            npc = self.create_npc(name, npc_type, location, faction)
            npcs.append(npc)

        return npcs

    def _handle_secrets_inquiry(self, npc: NPC) -> Dict:
        """Handle secrets inquiry - uses the new secrets dialogue"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} leans in close and whispers: {secret}", "rep_change": 2}
        else:
            return {
                "message": f"{npc.name} looks uncomfortable and changes the subject.",
                "rep_change": -1,
            }

    def _handle_trade_secrets(self, npc: NPC) -> Dict:
        """Handle trade secrets inquiry"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} shares a trade secret: {secret}"}
        else:
            return {"message": f"{npc.name} says they don't know any trade secrets."}

    def _handle_classified_data(self, npc: NPC) -> Dict:
        """Handle classified data inquiry"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} looks around nervously and says: {secret}"}
        else:
            return {"message": f"{npc.name} says all their research is public domain."}

    def _handle_stories_request(self, npc: NPC) -> Dict:
        """Handle stories request"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} tells you a story: {secret}"}
        else:
            return {"message": f"{npc.name} tells you a story about their travels."}

    def _handle_classified_information(self, npc: NPC) -> Dict:
        """Handle classified information inquiry"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} checks for surveillance and whispers: {secret}"}
        else:
            return {"message": f"{npc.name} says they can't discuss classified matters."}

    def _handle_dangerous_information(self, npc: NPC) -> Dict:
        """Handle dangerous information inquiry"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} grins and says: {secret}"}
        else:
            return {"message": f"{npc.name} says they don't deal in dangerous information."}

    def _handle_prophecy_request(self, npc: NPC) -> Dict:
        """Handle prophecy request"""
        if "prophecy" in npc.dialogue:
            prophecy = random.choice(npc.dialogue["prophecy"])
            return {"message": f"{npc.name} speaks in a mystical voice: {prophecy}"}
        else:
            return {"message": f"{npc.name} says they don't make prophecies."}

    def _handle_void_inquiry(self, npc: NPC) -> Dict:
        """Handle void inquiry"""
        if "secrets" in npc.dialogue:
            secret = random.choice(npc.dialogue["secrets"])
            return {"message": f"{npc.name} speaks of the void: {secret}"}
        else:
            return {"message": f"{npc.name} says the void is unknowable."}

    def _handle_mystical_guidance(self, npc: NPC) -> Dict:
        """Handle mystical guidance request"""
        if "prophecy" in npc.dialogue:
            prophecy = random.choice(npc.dialogue["prophecy"])
            return {"message": f"{npc.name} offers mystical guidance: {prophecy}"}
        else:
            return {"message": f"{npc.name} says they can't provide mystical guidance."}
