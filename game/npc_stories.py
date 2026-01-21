#!/usr/bin/env python3
"""
NPC Story System - Subtle Hints and Lore
NPCs can tell stories that provide hints about game mechanics, lore, and strategies
without being too obvious
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from game.personality import PersonalityProfile


class StoryType(Enum):
    """Types of stories NPCs can tell"""
    MECHANICS_HINT = "mechanics_hint"  # Subtle hints about game mechanics
    LORE = "lore"  # World building and history
    STRATEGY = "strategy"  # Tactical advice
    SECRET = "secret"  # Hidden features or locations
    WARNING = "warning"  # Dangers to avoid
    RUMOR = "rumor"  # Market tips, events, opportunities


@dataclass
class Story:
    """A story an NPC can tell"""
    title: str
    content: str
    story_type: StoryType
    hint_level: int  # 1-5, how obvious the hint is (1 = very subtle, 5 = more direct)
    related_topic: str  # What game mechanic/feature this relates to
    personality_fit: List[str]  # Which personality types are likely to tell this


class NPCStoryLibrary:
    """Library of stories NPCs can tell"""
    
    def __init__(self):
        self.stories = self._initialize_stories()
    
    def _initialize_stories(self) -> List[Story]:
        """Initialize the story library"""
        stories = []
        
        # Mechanics Hints - Subtle hints about game features
        stories.extend([
            Story(
                title="The Trader's Secret",
                content="You know, I've been trading in these sectors for years. One thing I learned: some places pay better for certain goods, but only if you know when to visit. The markets... they change, you see. Not randomly, but there's a pattern. Smart traders watch the trends.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="dynamic_markets",
                personality_fit=["trader", "greedy", "friendly"]
            ),
            Story(
                title="The Explorer's Discovery",
                content="I once met a captain who claimed to have found a hidden sector. Said it wasn't on any map, but he'd discovered it by... well, let's just say he was very thorough in his exploration. Some say there are places that only appear when you're looking for them.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="sector_exploration",
                personality_fit=["explorer", "curious", "mysterious"]
            ),
            Story(
                title="The Skillful Captain",
                content="There was this old spacer I knew. Never seemed to miss a shot, always knew the best trade routes. When I asked him his secret, he just smiled and said 'Practice makes perfect, but understanding makes mastery.' He'd spend hours in the holodeck, you know.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="skills_training",
                personality_fit=["friendly", "honest", "neutral"]
            ),
            Story(
                title="The Diplomatic Approach",
                content="I've seen captains who think force solves everything. But the ones who last? They know when to talk, when to trade, when to fight. Reputation matters out here. Help someone, and they remember. Cross someone, and word spreads faster than light.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="diplomacy_reputation",
                personality_fit=["diplomat", "honest", "friendly"]
            ),
            Story(
                title="The Prepared Captain",
                content="Space is dangerous. I've seen too many ships lost because their captains weren't ready. The smart ones? They always keep their ship in good repair, stock up on fuel before long journeys, and never travel without some emergency supplies. Preparation is the difference between survival and... well, you know.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=3,
                related_topic="ship_maintenance",
                personality_fit=["cautious", "friendly", "neutral"]
            ),
            Story(
                title="The Mission Runner",
                content="Some captains just trade, but the successful ones? They take on missions. Not just for the credits, mind you. Missions lead to places you'd never go otherwise. Meet people, see things. And sometimes... sometimes the rewards are more than just credits.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="missions_quests",
                personality_fit=["friendly", "neutral", "curious"]
            ),
            Story(
                title="The Stock Market Tale",
                content="I had a friend who made a fortune in the stock market. Not by luck, mind you. He'd watch the companies, see what sectors they operated in, what events affected them. Said the market wasn't random - it reacted to the world. Smart investors pay attention to the news.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="stock_market",
                personality_fit=["trader", "greedy", "intelligent"]
            ),
            Story(
                title="The Crafty Engineer",
                content="Met an engineer once who could make anything. Said the secret wasn't just having the materials - it was knowing what to combine. Some combinations work better than others. And sometimes, the best items aren't bought, they're made.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="crafting",
                personality_fit=["scientist", "curious", "intelligent"]
            ),
            Story(
                title="The Banker's Advice",
                content="You know, I've seen captains go broke because they kept all their credits on them. Smart ones? They use banks. Not just for safety, but for interest. Money sitting in your account does nothing, but in the right bank account... it grows. Slowly, but it grows.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=3,
                related_topic="banking",
                personality_fit=["trader", "cautious", "greedy"]
            ),
            Story(
                title="The Combat Veteran",
                content="I've been in my share of fights. Learned that brute force isn't always the answer. Sometimes you need to defend, let your opponent wear themselves out. Sometimes you need to use items - medkits, energy cells. And sometimes... sometimes running away is the smartest move.",
                story_type=StoryType.MECHANICS_HINT,
                hint_level=2,
                related_topic="combat_strategy",
                personality_fit=["aggressive", "cautious", "neutral"]
            ),
        ])
        
        # Strategy Hints - Tactical advice
        stories.extend([
            Story(
                title="The Profitable Route",
                content="I've mapped out a few trade routes in my time. The trick isn't just buying low and selling high - it's finding the sectors where demand is high and supply is low. Some sectors specialize, you know. They'll pay premium for certain goods.",
                story_type=StoryType.STRATEGY,
                hint_level=2,
                related_topic="trading_routes",
                personality_fit=["trader", "greedy", "intelligent"]
            ),
            Story(
                title="The Exploration Strategy",
                content="New captains always ask me: where should I explore? I tell them: start close, work your way out. Chart the nearby sectors first. Get to know the area. Then, when you're ready, venture further. But always keep enough fuel to get back.",
                story_type=StoryType.STRATEGY,
                hint_level=3,
                related_topic="exploration",
                personality_fit=["explorer", "friendly", "cautious"]
            ),
            Story(
                title="The Faction Balance",
                content="I've seen captains who pick a side and stick with it. That's one way. But the smart ones? They stay neutral, or they balance their relationships. Too friendly with one faction, and others get suspicious. Too hostile, and you're cut off from opportunities.",
                story_type=StoryType.STRATEGY,
                hint_level=2,
                related_topic="faction_management",
                personality_fit=["diplomat", "neutral", "cautious"]
            ),
            Story(
                title="The Resource Management",
                content="Space is unforgiving. I've seen captains run out of fuel in the middle of nowhere. The smart ones always keep reserves. Fuel, energy, health - you never know when you'll need them. And credits? Always keep some emergency funds.",
                story_type=StoryType.STRATEGY,
                hint_level=3,
                related_topic="resource_management",
                personality_fit=["cautious", "friendly", "neutral"]
            ),
        ])
        
        # Secrets - Hidden features
        stories.extend([
            Story(
                title="The Hidden Holodeck",
                content="You know about holodecks, right? Most stations have them. But there's a rumor... some say there are special programs. Not the usual entertainment ones. Programs that can teach you things, improve your skills. If you know where to look.",
                story_type=StoryType.SECRET,
                hint_level=2,
                related_topic="holodeck_training",
                personality_fit=["mysterious", "curious", "scientist"]
            ),
            Story(
                title="The SOS Signal",
                content="I once picked up a distress signal. Turned out to be a ship in trouble. Helped them out, and they were very grateful. More grateful than I expected. Turns out, helping others in space... well, it pays to be helpful. In more ways than one.",
                story_type=StoryType.SECRET,
                hint_level=2,
                related_topic="sos_system",
                personality_fit=["friendly", "honest", "neutral"]
            ),
            Story(
                title="The Ship Upgrades",
                content="I've seen some impressive ships in my time. Not just big ones - efficient ones. Captains who invest in their ships, upgrade them properly. They say a well-upgraded ship can make all the difference. Not just in combat, but in everything.",
                story_type=StoryType.SECRET,
                hint_level=2,
                related_topic="ship_customization",
                personality_fit=["engineer", "intelligent", "cautious"]
            ),
            Story(
                title="The Empire Builder",
                content="There are captains out there who don't just explore - they claim. I've heard stories of captains who've built their own little empires. Captured sectors, managed resources. It's not easy, but for those who succeed... well, power has its rewards.",
                story_type=StoryType.SECRET,
                hint_level=2,
                related_topic="empire_system",
                personality_fit=["aggressive", "greedy", "mysterious"]
            ),
        ])
        
        # Warnings - Dangers to avoid
        stories.extend([
            Story(
                title="The Dangerous Sector",
                content="I've heard stories about Sector 7. They say it's dangerous - more dangerous than the charts show. Pirates, hostile aliens, strange phenomena. Some captains go there and never come back. Others... others come back changed. Be careful if you go that way.",
                story_type=StoryType.WARNING,
                hint_level=3,
                related_topic="dangerous_sectors",
                personality_fit=["cautious", "friendly", "neutral"]
            ),
            Story(
                title="The Market Crash",
                content="I've seen markets crash before. One day, prices are high. The next? Everything's worthless. It can happen fast. Smart traders diversify. Don't put all your credits in one commodity. Spread the risk.",
                story_type=StoryType.WARNING,
                hint_level=3,
                related_topic="market_volatility",
                personality_fit=["trader", "cautious", "greedy"]
            ),
            Story(
                title="The Fuel Trap",
                content="I knew a captain who got stranded. Ran out of fuel in a dead sector. No stations, no help. Had to wait for someone to come by. Took weeks. Always check your fuel before long journeys. Always.",
                story_type=StoryType.WARNING,
                hint_level=3,
                related_topic="fuel_management",
                personality_fit=["cautious", "friendly", "neutral"]
            ),
        ])
        
        # Lore - World building
        stories.extend([
            Story(
                title="The Genesis Torpedo",
                content="You've heard the rumors, right? About the Genesis Torpedo? They say it can create entire planets. Not destroy - create. The Federation's been working on it for years. Some say it's ready. Others say it's too dangerous. Me? I think it's real, and I think someone's already used it.",
                story_type=StoryType.LORE,
                hint_level=1,
                related_topic="genesis_torpedo",
                personality_fit=["mysterious", "scientist", "curious"]
            ),
            Story(
                title="The First Contact",
                content="They say the first contact with aliens didn't go well. Not the official story, mind you. The real story. There was a misunderstanding. Lives were lost. That's why the Federation is so careful now. So protocol-heavy. They learned from their mistakes.",
                story_type=StoryType.LORE,
                hint_level=1,
                related_topic="first_contact",
                personality_fit=["mysterious", "scientist", "neutral"]
            ),
            Story(
                title="The Resource Wars",
                content="Before the current peace, there were wars. Real wars. Not skirmishes - full-scale conflicts. Over resources, territory, ideology. Millions died. That's why the treaties exist. That's why everyone's so careful. The peace is fragile.",
                story_type=StoryType.LORE,
                hint_level=1,
                related_topic="resource_wars",
                personality_fit=["neutral", "cautious", "mysterious"]
            ),
            Story(
                title="The Quantum Network",
                content="You know how we communicate across sectors? Quantum entanglement. Instant communication, no matter the distance. But there's a rumor... some say the network isn't just for communication. Some say it's being used for something else. Something bigger.",
                story_type=StoryType.LORE,
                hint_level=1,
                related_topic="quantum_network",
                personality_fit=["scientist", "mysterious", "curious"]
            ),
        ])
        
        # Rumors - Market tips and opportunities
        stories.extend([
            Story(
                title="The Market Tip",
                content="I heard something interesting. The traders in Sector 12 are paying premium for electronics. Something about a new project. Don't know how long it'll last, but if you've got electronics to sell... might be worth the trip.",
                story_type=StoryType.RUMOR,
                hint_level=3,
                related_topic="market_opportunity",
                personality_fit=["trader", "friendly", "greedy"]
            ),
            Story(
                title="The Rare Find",
                content="Someone told me they found rare metals in the asteroid belt near Sector 5. Not the usual stuff - something special. Worth a fortune if you can find it. But it's dangerous out there. Pirates know about it too.",
                story_type=StoryType.RUMOR,
                hint_level=2,
                related_topic="rare_resources",
                personality_fit=["trader", "explorer", "greedy"]
            ),
            Story(
                title="The Event Coming",
                content="I've been hearing whispers. Something big is happening. A market event, maybe. Or a faction conflict. The signs are there if you know how to read them. Smart captains prepare. Stock up, save credits, be ready.",
                story_type=StoryType.RUMOR,
                hint_level=2,
                related_topic="upcoming_events",
                personality_fit=["mysterious", "cautious", "neutral"]
            ),
        ])
        
        return stories
    
    def get_stories_for_personality(
        self,
        personality_profile: PersonalityProfile,
        story_type: Optional[StoryType] = None,
        max_hint_level: int = 4
    ) -> List[Story]:
        """Get stories that fit an NPC's personality"""
        suitable_stories = []
        
        for story in self.stories:
            # Filter by story type if specified
            if story_type and story.story_type != story_type:
                continue
            
            # Filter by hint level
            if story.hint_level > max_hint_level:
                continue
            
            # Check personality fit
            personality_type = personality_profile.personality_type
            if personality_type in story.personality_fit:
                suitable_stories.append(story)
            # Also check by traits
            elif personality_profile.greed >= 7 and "greedy" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.curiosity >= 7 and "curious" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.intelligence >= 7 and "intelligent" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.friendliness >= 7 and "friendly" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.cautiousness >= 7 and "cautious" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.honesty >= 7 and "honest" in story.personality_fit:
                suitable_stories.append(story)
            elif personality_profile.aggression >= 5 and "aggressive" in story.personality_fit:
                suitable_stories.append(story)
            elif "neutral" in story.personality_fit:
                suitable_stories.append(story)
        
        return suitable_stories
    
    def get_random_story(
        self,
        personality_profile: PersonalityProfile,
        story_type: Optional[StoryType] = None,
        max_hint_level: int = 4
    ) -> Optional[Story]:
        """Get a random story suitable for an NPC"""
        stories = self.get_stories_for_personality(personality_profile, story_type, max_hint_level)
        if stories:
            return random.choice(stories)
        return None
    
    def get_story_by_topic(self, topic: str) -> Optional[Story]:
        """Get a story related to a specific topic"""
        matching_stories = [s for s in self.stories if s.related_topic == topic]
        if matching_stories:
            return random.choice(matching_stories)
        return None


# Global story library instance
_story_library: Optional[NPCStoryLibrary] = None


def get_story_library() -> NPCStoryLibrary:
    """Get the global story library instance"""
    global _story_library
    if _story_library is None:
        _story_library = NPCStoryLibrary()
    return _story_library

