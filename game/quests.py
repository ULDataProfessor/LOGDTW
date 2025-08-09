"""
Quest system for LOGDTW2002
Handles missions, quests, and objectives
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from game.player import Player, Item
from game.enhanced_missions import MissionGenerator, MissionDifficulty

@dataclass
class Quest:
    """Represents a quest or mission"""
    id: str
    name: str
    description: str
    quest_type: str  # delivery, combat, exploration, trading, etc.
    location: str
    requirements: Dict[str, Any] = None
    objectives: List[str] = None
    rewards: Dict[str, Any] = None
    difficulty: int = 1  # 1-10 scale
    time_limit: Optional[int] = None  # in game days
    faction: str = "Neutral"
    status: str = "available"  # available, active, completed, failed
    next_quest: Optional[str] = None
    branching_paths: Dict[str, str] = None
    chain_id: Optional[str] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}
        if self.objectives is None:
            self.objectives = []
        if self.rewards is None:
            self.rewards = {}
        if self.branching_paths is None:
            self.branching_paths = {}

class QuestSystem:
    """Handles quests and missions"""
    
    def __init__(self):
        self.available_quests = {}
        self.active_quests = {}
        self.completed_quests = {}
        self.failed_quests = {}
        self.mission_generator = MissionGenerator()
        
        # Initialize quests
        self._create_quests()

    def generate_dynamic_quest(self, player: Player) -> Quest:
        """Generate a dynamic quest using the MissionGenerator"""
        mission = self.mission_generator.generate_mission(
            player_level=player.level,
            player_location=player.coordinates[0] if isinstance(player.coordinates, tuple) else player.coordinates,
            player_reputation=player.reputation
        )

        difficulty_map = {
            MissionDifficulty.TRIVIAL: 1,
            MissionDifficulty.EASY: 2,
            MissionDifficulty.NORMAL: 4,
            MissionDifficulty.HARD: 6,
            MissionDifficulty.EXTREME: 8,
            MissionDifficulty.LEGENDARY: 10,
        }

        rewards = {}
        if mission.rewards.experience:
            rewards['experience'] = mission.rewards.experience
        if mission.rewards.credits:
            rewards['credits'] = mission.rewards.credits
        if mission.rewards.reputation:
            rewards['reputation'] = mission.rewards.reputation
        if mission.rewards.items:
            rewards['items'] = [
                {
                    'name': item_name,
                    'description': item_name,
                    'value': 0,
                    'type': 'special'
                }
                for item_name in mission.rewards.items
            ]

        quest = Quest(
            id=mission.id,
            name=mission.title,
            description=mission.description,
            quest_type=mission.type.value,
            location=f"Sector {mission.sector_id}" if mission.sector_id is not None else "Unknown",
            requirements={},
            objectives=[obj.description for obj in mission.objectives],
            rewards=rewards,
            difficulty=difficulty_map.get(mission.difficulty, 1),
            time_limit=mission.time_limit,
            faction=mission.faction or 'Neutral',
            status=mission.status.value,
            next_quest=mission.next_mission,
            branching_paths=mission.branching_paths,
            chain_id=mission.chain_id
        )

        self.available_quests[quest.id] = quest
        return quest
    
    def _create_quests(self):
        """Create available quests"""
        quests_data = [
            {
                'id': 'delivery_001',
                'name': 'Medical Supplies Delivery',
                'description': 'Deliver medical supplies to Luna Base. The research facility is running low on supplies.',
                'quest_type': 'delivery',
                'location': 'Earth Station',
                'requirements': {'level': 1, 'credits': 0},
                'objectives': ['Travel to Luna Base', 'Deliver Med Kits'],
                'rewards': {'experience': 50, 'credits': 200, 'reputation': {'Scientists': 10}},
                'difficulty': 2,
                'faction': 'Scientists'
            },
            {
                'id': 'combat_001',
                'name': 'Pirate Hunt',
                'description': 'Eliminate space pirates in the Asteroid Belt. They have been attacking merchant ships.',
                'quest_type': 'combat',
                'location': 'Mars Colony',
                'requirements': {'level': 3, 'combat_skill': 2},
                'objectives': ['Travel to Asteroid Belt', 'Defeat 3 Space Pirates'],
                'rewards': {'experience': 150, 'credits': 500, 'reputation': {'Federation': 20}},
                'difficulty': 4,
                'faction': 'Federation'
            },
            {
                'id': 'trading_001',
                'name': 'Luxury Goods Run',
                'description': 'Transport luxury goods from Pirate Haven to Earth Station. High risk, high reward.',
                'quest_type': 'trading',
                'location': 'Pirate Haven',
                'requirements': {'level': 2, 'credits': 1000},
                'objectives': ['Buy luxury goods at Pirate Haven', 'Sell goods at Earth Station'],
                'rewards': {'experience': 100, 'credits': 800, 'reputation': {'Traders': 15}},
                'difficulty': 3,
                'faction': 'Traders'
            },
            {
                'id': 'exploration_001',
                'name': 'Deep Space Survey',
                'description': 'Explore the Outer Rim and collect data for the Deep Space Lab.',
                'quest_type': 'exploration',
                'location': 'Deep Space Lab',
                'requirements': {'level': 5, 'navigation_skill': 3},
                'objectives': ['Travel to Outer Rim', 'Collect exploration data'],
                'rewards': {'experience': 300, 'credits': 1000, 'reputation': {'Scientists': 25}},
                'difficulty': 6,
                'faction': 'Scientists'
            },
            {
                'id': 'mining_001',
                'name': 'Mineral Extraction',
                'description': 'Mine valuable minerals from the Asteroid Belt for Mars Colony.',
                'quest_type': 'mining',
                'location': 'Mars Colony',
                'requirements': {'level': 2, 'engineering_skill': 1},
                'objectives': ['Travel to Asteroid Belt', 'Collect 10 Raw Minerals'],
                'rewards': {'experience': 75, 'credits': 300, 'reputation': {'Federation': 10}},
                'difficulty': 3,
                'faction': 'Federation'
            },
            {
                'id': 'diplomacy_001',
                'name': 'Peace Negotiations',
                'description': 'Help broker peace between warring factions in the Outer Rim.',
                'quest_type': 'diplomacy',
                'location': 'Earth Station',
                'requirements': {'level': 7, 'diplomacy_skill': 4},
                'objectives': ['Travel to Outer Rim', 'Negotiate with factions'],
                'rewards': {'experience': 500, 'credits': 2000, 'reputation': {'Federation': 50}},
                'difficulty': 8,
                'faction': 'Federation'
            }
        ]
        
        for quest_data in quests_data:
            quest = Quest(
                id=quest_data['id'],
                name=quest_data['name'],
                description=quest_data['description'],
                quest_type=quest_data['quest_type'],
                location=quest_data['location'],
                requirements=quest_data['requirements'],
                objectives=quest_data['objectives'],
                rewards=quest_data['rewards'],
                difficulty=quest_data['difficulty'],
                faction=quest_data['faction']
            )
            self.available_quests[quest_data['id']] = quest
    
    def get_available_quests(self, player: Player, location: str = None) -> List[Quest]:
        """Get quests available to the player"""
        available = []
        
        for quest in self.available_quests.values():
            if quest.status != "available":
                continue
            
            if location and quest.location != location:
                continue
            
            # Check if player meets requirements
            if self._check_requirements(player, quest):
                available.append(quest)
        
        return available
    
    def _check_requirements(self, player: Player, quest: Quest) -> bool:
        """Check if player meets quest requirements"""
        for req_type, req_value in quest.requirements.items():
            if req_type == 'level':
                if player.level < req_value:
                    return False
            elif req_type == 'credits':
                if player.credits < req_value:
                    return False
            elif req_type.endswith('_skill'):
                skill_name = req_type.replace('_skill', '')
                if player.get_skill_level(skill_name) < req_value:
                    return False
        
        return True
    
    def accept_quest(self, player: Player, quest_id: str) -> Dict:
        """Accept a quest"""
        if quest_id not in self.available_quests:
            return {'success': False, 'message': 'Quest not found'}
        
        quest = self.available_quests[quest_id]
        
        # Check requirements again
        if not self._check_requirements(player, quest):
            return {'success': False, 'message': 'You do not meet the requirements for this quest'}
        
        # Move quest to active
        quest.status = "active"
        self.active_quests[quest_id] = quest
        del self.available_quests[quest_id]
        
        return {
            'success': True,
            'message': f'Quest accepted: {quest.name}',
            'quest': quest
        }
    
    def complete_quest(self, player: Player, quest_id: str) -> Dict:
        """Complete a quest and give rewards"""
        if quest_id not in self.active_quests:
            return {'success': False, 'message': 'Quest not found in active quests'}
        
        quest = self.active_quests[quest_id]
        
        # Give rewards
        rewards_given = self._give_rewards(player, quest)
        
        # Move quest to completed
        quest.status = "completed"
        self.completed_quests[quest_id] = quest
        del self.active_quests[quest_id]

        return {
            'success': True,
            'message': f'Quest completed: {quest.name}',
            'rewards': rewards_given,
            'next_quest': quest.next_quest,
            'branching_paths': quest.branching_paths
        }
    
    def fail_quest(self, quest_id: str) -> Dict:
        """Mark a quest as failed"""
        if quest_id not in self.active_quests:
            return {'success': False, 'message': 'Quest not found in active quests'}
        
        quest = self.active_quests[quest_id]
        quest.status = "failed"
        self.failed_quests[quest_id] = quest
        del self.active_quests[quest_id]

        return {
            'success': True,
            'message': f'Quest failed: {quest.name}',
            'next_quest': quest.next_quest,
            'branching_paths': quest.branching_paths
        }
    
    def _give_rewards(self, player: Player, quest: Quest) -> Dict:
        """Give quest rewards to player"""
        rewards_given = {}
        
        # Experience
        if 'experience' in quest.rewards:
            exp_gained = quest.rewards['experience']
            leveled_up = player.add_experience(exp_gained)
            rewards_given['experience'] = exp_gained
            if leveled_up:
                rewards_given['leveled_up'] = True
        
        # Credits
        if 'credits' in quest.rewards:
            credits_gained = quest.rewards['credits']
            player.add_credits(credits_gained)
            rewards_given['credits'] = credits_gained
        
        # Reputation
        if 'reputation' in quest.rewards:
            for faction, amount in quest.rewards['reputation'].items():
                if faction in player.reputation:
                    player.reputation[faction] += amount
                    rewards_given['reputation'] = rewards_given.get('reputation', {})
                    rewards_given['reputation'][faction] = amount
        
        # Items
        if 'items' in quest.rewards:
            for item_data in quest.rewards['items']:
                item = Item(
                    name=item_data['name'],
                    description=item_data['description'],
                    value=item_data['value'],
                    item_type=item_data['type']
                )
                if player.add_item(item):
                    rewards_given['items'] = rewards_given.get('items', [])
                    rewards_given['items'].append(item.name)
        
        return rewards_given
    
    def get_quest_progress(self, quest_id: str) -> Dict:
        """Get progress on a specific quest"""
        if quest_id not in self.active_quests:
            return {'found': False}
        
        quest = self.active_quests[quest_id]
        
        # This would track actual progress based on player actions
        # For now, return basic quest info
        return {
            'found': True,
            'name': quest.name,
            'description': quest.description,
            'objectives': quest.objectives,
            'difficulty': quest.difficulty,
            'faction': quest.faction
        }
    
    def get_quest_summary(self, player: Player) -> str:
        """Get a summary of all quests"""
        summary = "\n[bold cyan]Quest Summary[/bold cyan]\n"
        
        # Active quests
        if self.active_quests:
            summary += "\n[bold yellow]Active Quests:[/bold yellow]\n"
            for quest in self.active_quests.values():
                summary += f"  {quest.name} ({quest.quest_type.title()})\n"
        else:
            summary += "\n[dim]No active quests[/dim]\n"
        
        # Available quests
        available = self.get_available_quests(player)
        if available:
            summary += "\n[bold green]Available Quests:[/bold green]\n"
            for quest in available:
                summary += f"  {quest.name} - Level {quest.difficulty}\n"
        
        # Completed quests
        if self.completed_quests:
            summary += f"\n[bold blue]Completed Quests: {len(self.completed_quests)}[/bold blue]\n"
        
        return summary
    
    def generate_random_quest(self, location: str, player_level: int) -> Optional[Quest]:
        """Generate a random quest for a location"""
        quest_types = ['delivery', 'combat', 'trading', 'exploration', 'mining']
        quest_type = random.choice(quest_types)
        
        # Generate quest based on type and location
        if quest_type == 'delivery':
            return self._generate_delivery_quest(location, player_level)
        elif quest_type == 'combat':
            return self._generate_combat_quest(location, player_level)
        elif quest_type == 'trading':
            return self._generate_trading_quest(location, player_level)
        elif quest_type == 'exploration':
            return self._generate_exploration_quest(location, player_level)
        elif quest_type == 'mining':
            return self._generate_mining_quest(location, player_level)
        
        return None
    
    def _generate_delivery_quest(self, location: str, player_level: int) -> Quest:
        """Generate a delivery quest"""
        destinations = ['Earth Station', 'Mars Colony', 'Luna Base', 'Deep Space Lab']
        destination = random.choice([d for d in destinations if d != location])
        
        return Quest(
            id=f"delivery_{random.randint(1000, 9999)}",
            name=f"Delivery to {destination}",
            description=f"Deliver goods to {destination}.",
            quest_type='delivery',
            location=location,
            requirements={'level': max(1, player_level - 1)},
            objectives=[f'Travel to {destination}', 'Deliver goods'],
            rewards={'experience': 50 + player_level * 10, 'credits': 100 + player_level * 20},
            difficulty=max(1, player_level - 1)
        )
    
    def _generate_combat_quest(self, location: str, player_level: int) -> Quest:
        """Generate a combat quest"""
        return Quest(
            id=f"combat_{random.randint(1000, 9999)}",
            name="Eliminate Threats",
            description="Defeat enemies in the area.",
            quest_type='combat',
            location=location,
            requirements={'level': player_level, 'combat_skill': max(1, player_level // 2)},
            objectives=['Defeat enemies'],
            rewards={'experience': 100 + player_level * 20, 'credits': 200 + player_level * 30},
            difficulty=player_level
        )
    
    def _generate_trading_quest(self, location: str, player_level: int) -> Quest:
        """Generate a trading quest"""
        return Quest(
            id=f"trading_{random.randint(1000, 9999)}",
            name="Trade Mission",
            description="Buy and sell goods for profit.",
            quest_type='trading',
            location=location,
            requirements={'level': player_level, 'credits': 500},
            objectives=['Buy goods', 'Sell goods'],
            rewards={'experience': 75 + player_level * 15, 'credits': 150 + player_level * 25},
            difficulty=max(1, player_level - 1)
        )
    
    def _generate_exploration_quest(self, location: str, player_level: int) -> Quest:
        """Generate an exploration quest"""
        return Quest(
            id=f"exploration_{random.randint(1000, 9999)}",
            name="Exploration Mission",
            description="Explore unknown areas and gather data.",
            quest_type='exploration',
            location=location,
            requirements={'level': player_level, 'navigation_skill': max(1, player_level // 2)},
            objectives=['Explore area', 'Collect data'],
            rewards={'experience': 125 + player_level * 25, 'credits': 300 + player_level * 40},
            difficulty=player_level + 1
        )
    
    def _generate_mining_quest(self, location: str, player_level: int) -> Quest:
        """Generate a mining quest"""
        return Quest(
            id=f"mining_{random.randint(1000, 9999)}",
            name="Mining Operation",
            description="Extract valuable resources from asteroids.",
            quest_type='mining',
            location=location,
            requirements={'level': player_level, 'engineering_skill': max(1, player_level // 2)},
            objectives=['Mine resources'],
            rewards={'experience': 80 + player_level * 15, 'credits': 200 + player_level * 30},
            difficulty=player_level
        )
