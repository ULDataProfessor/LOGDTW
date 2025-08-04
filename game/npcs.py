"""
NPC system for LOGDTW2002
Handles NPCs, conversations, and interactive features
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from game.player import Player

@dataclass
class NPC:
    """Represents an NPC in the game"""
    name: str
    npc_type: str  # trader, pirate, scientist, official, etc.
    personality: str  # friendly, hostile, neutral, mysterious
    location: str
    dialogue: Dict[str, List[str]] = None
    quests: List[str] = None
    services: List[str] = None
    faction: str = "Neutral"
    reputation: int = 0  # -100 to 100
    
    def __post_init__(self):
        if self.dialogue is None:
            self.dialogue = {}
        if self.quests is None:
            self.quests = []
        if self.services is None:
            self.services = []

class NPCSystem:
    """Handles NPC interactions and conversations"""
    
    def __init__(self):
        self.npcs = {}
        self.conversations = {}
        self.npc_templates = self._create_npc_templates()
        
    def _create_npc_templates(self) -> Dict:
        """Create NPC templates"""
        return {
            'trader': {
                'personality': 'friendly',
                'dialogue': {
                    'greeting': [
                        "Welcome, traveler! Looking for some good deals?",
                        "Ah, a customer! What can I interest you in today?",
                        "Greetings! My wares are the finest in the sector."
                    ],
                    'farewell': [
                        "Safe travels, friend!",
                        "Come back soon!",
                        "May your journey be profitable!"
                    ],
                    'trade': [
                        "I have some excellent merchandise.",
                        "This is top quality, I assure you.",
                        "You won't find better prices anywhere."
                    ]
                },
                'services': ['trading', 'information']
            },
            'pirate': {
                'personality': 'hostile',
                'dialogue': {
                    'greeting': [
                        "Well, well... what do we have here?",
                        "You're in my territory now, friend.",
                        "Hand over your cargo and no one gets hurt."
                    ],
                    'farewell': [
                        "You're lucky I'm in a good mood.",
                        "Don't let me catch you here again.",
                        "Next time won't be so pleasant."
                    ],
                    'threat': [
                        "You're making a big mistake.",
                        "I don't think you understand the situation.",
                        "This can end badly for you."
                    ]
                },
                'services': ['smuggling', 'illegal_goods']
            },
            'scientist': {
                'personality': 'neutral',
                'dialogue': {
                    'greeting': [
                        "Fascinating! Another traveler from the void.",
                        "Greetings. I'm conducting important research.",
                        "Welcome to our research facility."
                    ],
                    'farewell': [
                        "Safe journey through the stars.",
                        "May your discoveries be fruitful.",
                        "Return if you have interesting data."
                    ],
                    'research': [
                        "The universe holds many mysteries.",
                        "My research could change everything.",
                        "There's so much we don't understand."
                    ]
                },
                'services': ['research', 'information']
            },
            'official': {
                'personality': 'neutral',
                'dialogue': {
                    'greeting': [
                        "Welcome to our station. Papers, please.",
                        "Greetings, citizen. How may I assist you?",
                        "Official business only, please."
                    ],
                    'farewell': [
                        "Keep your papers in order.",
                        "Safe travels, citizen.",
                        "Remember to follow regulations."
                    ],
                    'official': [
                        "All procedures must be followed.",
                        "Regulations are for everyone's safety.",
                        "The law is clear on this matter."
                    ]
                },
                'services': ['bureaucracy', 'permits']
            },
            'entertainer': {
                'personality': 'friendly',
                'dialogue': {
                    'greeting': [
                        "Welcome to the show!",
                        "Hey there, star traveler!",
                        "Ready for some entertainment?"
                    ],
                    'farewell': [
                        "Come back for more shows!",
                        "The stage is always open!",
                        "Keep the music playing!"
                    ],
                    'performance': [
                        "The crowd loves this one!",
                        "Let me show you something special.",
                        "This is my best material."
                    ]
                },
                'services': ['entertainment', 'holodeck']
            }
        }
    
    def create_npc(self, name: str, npc_type: str, location: str, faction: str = "Neutral") -> NPC:
        """Create a new NPC"""
        template = self.npc_templates.get(npc_type, self.npc_templates['trader'])
        
        npc = NPC(
            name=name,
            npc_type=npc_type,
            personality=template['personality'],
            location=location,
            dialogue=template['dialogue'],
            services=template['services'],
            faction=faction
        )
        
        self.npcs[name] = npc
        return npc
    
    def get_npcs_at_location(self, location: str) -> List[NPC]:
        """Get all NPCs at a specific location"""
        return [npc for npc in self.npcs.values() if npc.location == location]
    
    def start_conversation(self, player: Player, npc_name: str) -> Dict:
        """Start a conversation with an NPC"""
        if npc_name not in self.npcs:
            return {'success': False, 'message': 'NPC not found'}
        
        npc = self.npcs[npc_name]
        
        # Check if player can talk to this NPC
        if npc.personality == 'hostile' and player.reputation.get(npc.faction, 0) < -50:
            return {'success': False, 'message': f'{npc.name} refuses to talk to you.'}
        
        # Generate greeting
        greeting = random.choice(npc.dialogue.get('greeting', ['Hello there.']))
        
        return {
            'success': True,
            'npc': npc,
            'greeting': greeting,
            'personality': npc.personality,
            'services': npc.services
        }
    
    def get_conversation_options(self, npc: NPC) -> List[str]:
        """Get available conversation options"""
        options = ['Ask about services', 'Ask about location', 'Ask about rumors']
        
        if npc.npc_type == 'trader':
            options.extend(['Browse goods', 'Negotiate prices'])
        elif npc.npc_type == 'scientist':
            options.extend(['Discuss research', 'Share discoveries'])
        elif npc.npc_type == 'official':
            options.extend(['Request permits', 'File complaints'])
        elif npc.npc_type == 'entertainer':
            options.extend(['Request performance', 'Book holodeck'])
        elif npc.npc_type == 'pirate':
            options.extend(['Negotiate passage', 'Offer tribute'])
        
        options.append('End conversation')
        return options
    
    def handle_conversation_choice(self, player: Player, npc: NPC, choice: str) -> Dict:
        """Handle player's conversation choice"""
        if choice == 'Ask about services':
            return self._handle_services_inquiry(npc)
        elif choice == 'Ask about location':
            return self._handle_location_inquiry(npc)
        elif choice == 'Ask about rumors':
            return self._handle_rumors_inquiry(npc)
        elif choice == 'Browse goods' and npc.npc_type == 'trader':
            return self._handle_browse_goods(npc)
        elif choice == 'Negotiate prices' and npc.npc_type == 'trader':
            return self._handle_negotiate_prices(player, npc)
        elif choice == 'Discuss research' and npc.npc_type == 'scientist':
            return self._handle_discuss_research(npc)
        elif choice == 'Request performance' and npc.npc_type == 'entertainer':
            return self._handle_request_performance(npc)
        elif choice == 'Book holodeck' and npc.npc_type == 'entertainer':
            return self._handle_book_holodeck(player, npc)
        elif choice == 'End conversation':
            return self._handle_end_conversation(npc)
        else:
            return {'message': 'That option is not available.'}
    
    def _handle_services_inquiry(self, npc: NPC) -> Dict:
        """Handle services inquiry"""
        services_text = f"{npc.name} offers the following services:\n"
        for service in npc.services:
            services_text += f"• {service.title()}\n"
        
        return {'message': services_text}
    
    def _handle_location_inquiry(self, npc: NPC) -> Dict:
        """Handle location inquiry"""
        location_info = [
            f"{npc.name} tells you about {npc.location}:",
            "This is a busy trading hub with many opportunities.",
            "The locals are mostly friendly, but watch out for pirates.",
            "There's always something interesting happening here."
        ]
        
        return {'message': '\n'.join(location_info)}
    
    def _handle_rumors_inquiry(self, npc: NPC) -> Dict:
        """Handle rumors inquiry"""
        rumors = [
            "I heard there's a new trade route opening up.",
            "Rumors say there's a hidden pirate base nearby.",
            "Some say there's a mysterious alien artifact in the sector.",
            "I've heard whispers about a secret research facility.",
            "There's talk of a massive space battle coming.",
            "Some claim there's a lost colony out there somewhere."
        ]
        
        rumor = random.choice(rumors)
        return {'message': f"{npc.name} shares a rumor: {rumor}"}
    
    def _handle_browse_goods(self, npc: NPC) -> Dict:
        """Handle browsing goods"""
        goods = [
            "Rare minerals from the outer sectors",
            "Advanced technology from the core worlds",
            "Exotic spices from distant planets",
            "Precious metals and gems",
            "Strange alien artifacts"
        ]
        
        goods_text = f"{npc.name} shows you their wares:\n"
        for good in random.sample(goods, 3):
            goods_text += f"• {good}\n"
        
        return {'message': goods_text}
    
    def _handle_negotiate_prices(self, player: Player, npc: NPC) -> Dict:
        """Handle price negotiation"""
        if player.credits < 100:
            return {'message': f"{npc.name} looks unimpressed with your credit balance."}
        
        discount = random.randint(5, 15)
        return {'message': f"{npc.name} offers you a {discount}% discount on your next purchase!"}
    
    def _handle_discuss_research(self, npc: NPC) -> Dict:
        """Handle research discussion"""
        research_topics = [
            "The nature of subspace communication",
            "Advanced propulsion systems",
            "Alien civilizations and their technology",
            "The mysteries of dark matter",
            "Time dilation effects in deep space"
        ]
        
        topic = random.choice(research_topics)
        return {'message': f"{npc.name} discusses {topic} with great enthusiasm."}
    
    def _handle_request_performance(self, npc: NPC) -> Dict:
        """Handle performance request"""
        performances = [
            "A dramatic space opera",
            "A comedy about life on space stations",
            "A musical about star travel",
            "A mystery set in deep space"
        ]
        
        performance = random.choice(performances)
        return {'message': f"{npc.name} offers to perform '{performance}' for you."}
    
    def _handle_book_holodeck(self, player: Player, npc: NPC) -> Dict:
        """Handle holodeck booking"""
        if player.credits < 50:
            return {'message': f"{npc.name} says holodeck time costs 50 credits."}
        
        programs = [
            "Beach Resort Simulation",
            "Mountain Adventure",
            "Historical Battle Reenactment",
            "Alien World Exploration",
            "Space Battle Simulation"
        ]
        
        program = random.choice(programs)
        return {'message': f"{npc.name} books you for '{program}' on the holodeck."}
    
    def _handle_end_conversation(self, npc: NPC) -> Dict:
        """Handle ending conversation"""
        farewell = random.choice(npc.dialogue.get('farewell', ['Goodbye.']))
        return {'message': f"{npc.name}: {farewell}", 'end_conversation': True}
    
    def generate_random_npcs(self, location: str, num_npcs: int = 3) -> List[NPC]:
        """Generate random NPCs for a location"""
        npc_types = list(self.npc_templates.keys())
        npc_names = [
            "Captain", "Commander", "Doctor", "Professor", "Trader",
            "Merchant", "Pilot", "Engineer", "Technician", "Guard",
            "Official", "Scientist", "Artist", "Musician", "Chef"
        ]
        
        npcs = []
        for i in range(num_npcs):
            npc_type = random.choice(npc_types)
            name = f"{random.choice(npc_names)} {chr(65 + i)}"
            faction = random.choice(["Federation", "Pirates", "Scientists", "Traders", "Neutral"])
            
            npc = self.create_npc(name, npc_type, location, faction)
            npcs.append(npc)
        
        return npcs 