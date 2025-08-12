#!/usr/bin/env python3
"""
Enhanced Mission System for LOGDTW2002
Structured gameplay content with quest chains, dynamic missions, and branching storylines
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum


class MissionType(Enum):
    COMBAT = "combat"
    EXPLORATION = "exploration"
    TRADE = "trade"
    DIPLOMACY = "diplomacy"
    RESCUE = "rescue"
    DELIVERY = "delivery"
    INVESTIGATION = "investigation"
    BOUNTY_HUNTING = "bounty_hunting"
    ARCHAEOLOGY = "archaeology"
    ESPIONAGE = "espionage"
    COLONIZATION = "colonization"
    PROTECTION = "protection"


class MissionDifficulty(Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXTREME = "extreme"
    LEGENDARY = "legendary"


class MissionStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    LOCKED = "locked"


class ObjectiveType(Enum):
    KILL = "kill"
    COLLECT = "collect"
    DELIVER = "deliver"
    EXPLORE = "explore"
    SURVIVE = "survive"
    NEGOTIATE = "negotiate"
    SCAN = "scan"
    PROTECT = "protect"
    REACH = "reach"
    ACTIVATE = "activate"


@dataclass
class MissionObjective:
    id: str
    type: ObjectiveType
    description: str
    target: str
    quantity: int = 1
    current_progress: int = 0
    required_skills: Dict[str, int] = field(default_factory=dict)
    optional: bool = False
    hidden: bool = False
    completed: bool = False


@dataclass
class MissionReward:
    credits: int = 0
    experience: int = 0
    items: List[str] = field(default_factory=list)
    reputation: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, int] = field(default_factory=dict)
    unlocks: List[str] = field(default_factory=list)
    special_effects: List[str] = field(default_factory=list)


@dataclass
class Mission:
    id: str
    title: str
    description: str
    type: MissionType
    difficulty: MissionDifficulty
    status: MissionStatus = MissionStatus.AVAILABLE
    objectives: List[MissionObjective] = field(default_factory=list)
    rewards: MissionReward = field(default_factory=MissionReward)
    failure_consequences: Dict[str, Any] = field(default_factory=dict)
    prerequisites: Dict[str, Any] = field(default_factory=dict)
    time_limit: Optional[int] = None  # in game turns
    expires_at: Optional[int] = None
    sector_id: Optional[int] = None
    giver_npc: Optional[str] = None
    faction: Optional[str] = None
    chain_id: Optional[str] = None
    next_mission: Optional[str] = None
    branching_paths: Dict[str, str] = field(default_factory=dict)
    dynamic_factors: Dict[str, Any] = field(default_factory=dict)
    completion_text: str = ""
    failure_text: str = ""


@dataclass
class MissionChain:
    id: str
    title: str
    description: str
    missions: List[str]
    current_mission_index: int = 0
    completed: bool = False
    final_reward: MissionReward = field(default_factory=MissionReward)
    branching_enabled: bool = False


class MissionGenerator:
    """Generates procedural missions based on player state and world conditions"""

    def __init__(self):
        self.mission_templates = {}
        self.story_fragments = {}
        self.location_modifiers = {}
        self._initialize_templates()
        self._initialize_story_fragments()

    def _initialize_templates(self):
        """Initialize mission templates"""
        self.mission_templates = {
            MissionType.COMBAT: [
                {
                    "title_template": "Eliminate {enemy_type} threat",
                    "description_template": "Pirates have been raiding trade routes near {location}. Eliminate {quantity} {enemy_type} ships.",
                    "objectives": [
                        {
                            "type": ObjectiveType.KILL,
                            "target": "{enemy_type}",
                            "quantity": "{quantity}",
                        }
                    ],
                    "base_rewards": {
                        "credits": 500,
                        "experience": 100,
                        "reputation": {"Federation": 50},
                    },
                },
                {
                    "title_template": "Defend {location}",
                    "description_template": "The station at {location} is under attack. Protect it from incoming hostiles.",
                    "objectives": [
                        {"type": ObjectiveType.PROTECT, "target": "{location}", "quantity": 1}
                    ],
                    "base_rewards": {
                        "credits": 800,
                        "experience": 150,
                        "reputation": {"Federation": 75},
                    },
                },
            ],
            MissionType.EXPLORATION: [
                {
                    "title_template": "Survey {sector_name}",
                    "description_template": "Chart the unknown sector {sector_name} and report your findings.",
                    "objectives": [
                        {"type": ObjectiveType.EXPLORE, "target": "{sector_name}", "quantity": 1}
                    ],
                    "base_rewards": {
                        "credits": 300,
                        "experience": 200,
                        "skills": {"Exploration": 100},
                    },
                },
                {
                    "title_template": "Find the Lost {artifact}",
                    "description_template": "Ancient records speak of a {artifact} hidden in {location}. Find it.",
                    "objectives": [
                        {"type": ObjectiveType.COLLECT, "target": "{artifact}", "quantity": 1}
                    ],
                    "base_rewards": {"credits": 1000, "experience": 250, "items": ["{artifact}"]},
                },
            ],
            MissionType.TRADE: [
                {
                    "title_template": "Urgent Delivery to {destination}",
                    "description_template": "Transport {quantity} units of {commodity} to {destination} urgently.",
                    "objectives": [
                        {
                            "type": ObjectiveType.DELIVER,
                            "target": "{commodity}",
                            "quantity": "{quantity}",
                        }
                    ],
                    "base_rewards": {"credits": 400, "experience": 75, "skills": {"Trading": 50}},
                },
                {
                    "title_template": "Establish Trade Route",
                    "description_template": "Create a profitable trade route between {origin} and {destination}.",
                    "objectives": [
                        {"type": ObjectiveType.COLLECT, "target": "Trade Agreement", "quantity": 1},
                        {"type": ObjectiveType.DELIVER, "target": "Sample Goods", "quantity": 5},
                    ],
                    "base_rewards": {
                        "credits": 1500,
                        "experience": 200,
                        "unlocks": ["Trade Route: {origin}-{destination}"],
                    },
                },
            ],
            MissionType.RESCUE: [
                {
                    "title_template": "Rescue Operation",
                    "description_template": "A ship carrying {passenger_type} has been captured by {enemy_faction}. Rescue them.",
                    "objectives": [
                        {"type": ObjectiveType.REACH, "target": "{location}", "quantity": 1},
                        {
                            "type": ObjectiveType.COLLECT,
                            "target": "{passenger_type}",
                            "quantity": "{quantity}",
                        },
                    ],
                    "base_rewards": {
                        "credits": 750,
                        "experience": 175,
                        "reputation": {"Federation": 100},
                    },
                }
            ],
            MissionType.INVESTIGATION: [
                {
                    "title_template": "Investigate {mystery}",
                    "description_template": "Strange reports of {mystery} have surfaced. Investigate and report your findings.",
                    "objectives": [
                        {"type": ObjectiveType.SCAN, "target": "Evidence", "quantity": 3},
                        {"type": ObjectiveType.EXPLORE, "target": "{location}", "quantity": 1},
                    ],
                    "base_rewards": {"credits": 600, "experience": 150, "skills": {"Science": 75}},
                }
            ],
        }

    def _initialize_story_fragments(self):
        """Initialize story fragments for dynamic narrative generation"""
        self.story_fragments = {
            "enemies": [
                "Pirate Raiders",
                "Alien Scouts",
                "Rogue AI Ships",
                "Mercenary Fleets",
                "Rebel Forces",
            ],
            "locations": [
                "Alpha Station",
                "Mining Colony Beta",
                "Research Outpost Gamma",
                "Trade Hub Delta",
            ],
            "artifacts": [
                "Quantum Resonator",
                "Ancient Data Core",
                "Stellar Compass",
                "Void Crystal",
            ],
            "commodities": [
                "Medical Supplies",
                "Rare Minerals",
                "Advanced Technology",
                "Food Supplies",
            ],
            "mysteries": [
                "disappearing ships",
                "temporal anomalies",
                "alien signals",
                "energy disturbances",
            ],
            "passenger_types": ["diplomats", "scientists", "refugees", "corporate executives"],
            "factions": ["Pirates", "Aliens", "Rebels", "Corporation"],
        }

    def generate_mission(
        self,
        player_level: int,
        player_location: int,
        player_reputation: Dict[str, int],
        mission_type: MissionType = None,
    ) -> Mission:
        """Generate a procedural mission"""

        # Select mission type if not specified
        if not mission_type:
            mission_type = random.choice(list(MissionType))

        # Get template
        templates = self.mission_templates.get(mission_type, [])
        if not templates:
            return self._generate_basic_mission(player_level, player_location)

        template = random.choice(templates)

        # Generate mission parameters
        params = self._generate_mission_parameters(mission_type, player_level, player_location)

        # Fill template
        title = template["title_template"].format(**params)
        description = template["description_template"].format(**params)

        # Generate objectives
        objectives = []
        for obj_template in template["objectives"]:
            objective = MissionObjective(
                id=f"obj_{random.randint(1000, 9999)}",
                type=ObjectiveType(obj_template["type"]),
                description=f"{obj_template['type'].value.title()} {obj_template['quantity']} {obj_template['target']}",
                target=obj_template["target"].format(**params),
                quantity=(
                    int(str(obj_template["quantity"]).format(**params))
                    if isinstance(obj_template["quantity"], str)
                    else obj_template["quantity"]
                ),
            )
            objectives.append(objective)

        # Calculate difficulty based on player level
        difficulty = self._calculate_difficulty(player_level, mission_type)

        # Generate rewards
        base_rewards = template["base_rewards"]
        rewards = self._scale_rewards(base_rewards, difficulty, player_level)

        # Create mission
        mission = Mission(
            id=f"mission_{random.randint(10000, 99999)}",
            title=title,
            description=description,
            type=mission_type,
            difficulty=difficulty,
            objectives=objectives,
            rewards=rewards,
            sector_id=player_location,
            time_limit=self._calculate_time_limit(difficulty),
            faction=self._select_mission_faction(player_reputation),
        )

        return mission

    def _generate_mission_parameters(
        self, mission_type: MissionType, player_level: int, location: int
    ) -> Dict[str, str]:
        """Generate parameters for mission template"""
        params = {
            "location": f"Sector {location}",
            "sector_name": f"Sector {location + random.randint(1, 5)}",
            "destination": f"Sector {location + random.randint(-3, 3)}",
            "origin": f"Sector {location}",
            "quantity": str(random.randint(1, min(10, player_level + 2))),
            "enemy_type": random.choice(self.story_fragments["enemies"]),
            "artifact": random.choice(self.story_fragments["artifacts"]),
            "commodity": random.choice(self.story_fragments["commodities"]),
            "mystery": random.choice(self.story_fragments["mysteries"]),
            "passenger_type": random.choice(self.story_fragments["passenger_types"]),
            "enemy_faction": random.choice(self.story_fragments["factions"]),
        }
        return params

    def _calculate_difficulty(
        self, player_level: int, mission_type: MissionType
    ) -> MissionDifficulty:
        """Calculate mission difficulty based on player level and type"""
        # Base difficulty distribution
        if player_level <= 5:
            choices = [MissionDifficulty.TRIVIAL, MissionDifficulty.EASY, MissionDifficulty.NORMAL]
            weights = [40, 40, 20]
        elif player_level <= 15:
            choices = [MissionDifficulty.EASY, MissionDifficulty.NORMAL, MissionDifficulty.HARD]
            weights = [30, 50, 20]
        elif player_level <= 30:
            choices = [MissionDifficulty.NORMAL, MissionDifficulty.HARD, MissionDifficulty.EXTREME]
            weights = [40, 40, 20]
        else:
            choices = [
                MissionDifficulty.HARD,
                MissionDifficulty.EXTREME,
                MissionDifficulty.LEGENDARY,
            ]
            weights = [30, 50, 20]

        return random.choices(choices, weights=weights)[0]

    def _scale_rewards(
        self, base_rewards: Dict, difficulty: MissionDifficulty, player_level: int
    ) -> MissionReward:
        """Scale rewards based on difficulty and player level"""
        multipliers = {
            MissionDifficulty.TRIVIAL: 0.5,
            MissionDifficulty.EASY: 0.8,
            MissionDifficulty.NORMAL: 1.0,
            MissionDifficulty.HARD: 1.5,
            MissionDifficulty.EXTREME: 2.0,
            MissionDifficulty.LEGENDARY: 3.0,
        }

        multiplier = multipliers[difficulty] * (1 + player_level * 0.1)

        reward = MissionReward()
        reward.credits = int(base_rewards.get("credits", 0) * multiplier)
        reward.experience = int(base_rewards.get("experience", 0) * multiplier)
        reward.items = base_rewards.get("items", [])
        reward.reputation = base_rewards.get("reputation", {})
        reward.skills = base_rewards.get("skills", {})
        reward.unlocks = base_rewards.get("unlocks", [])

        return reward

    def _calculate_time_limit(self, difficulty: MissionDifficulty) -> int:
        """Calculate mission time limit in turns"""
        base_times = {
            MissionDifficulty.TRIVIAL: 5,
            MissionDifficulty.EASY: 10,
            MissionDifficulty.NORMAL: 15,
            MissionDifficulty.HARD: 20,
            MissionDifficulty.EXTREME: 30,
            MissionDifficulty.LEGENDARY: 50,
        }

        return base_times[difficulty] + random.randint(-3, 5)

    def _select_mission_faction(self, player_reputation: Dict[str, int]) -> str:
        """Select mission-giving faction based on player reputation"""
        factions = ["Federation", "Empire", "Republic", "Independent", "Traders Guild"]

        # Weight by reputation (higher rep = more likely to give missions)
        weights = []
        for faction in factions:
            rep = player_reputation.get(faction, 0)
            weight = max(1, 10 + rep // 10)  # Base weight 1, +1 per 10 rep
            weights.append(weight)

        return random.choices(factions, weights=weights)[0]

    def _generate_basic_mission(self, player_level: int, location: int) -> Mission:
        """Generate a basic mission as fallback"""
        return Mission(
            id=f"basic_{random.randint(1000, 9999)}",
            title="Patrol Mission",
            description="Patrol the local sector and report any unusual activity.",
            type=MissionType.EXPLORATION,
            difficulty=MissionDifficulty.EASY,
            objectives=[
                MissionObjective(
                    id="patrol_obj",
                    type=ObjectiveType.EXPLORE,
                    description="Patrol the sector",
                    target=f"Sector {location}",
                    quantity=1,
                )
            ],
            rewards=MissionReward(credits=200, experience=50),
            sector_id=location,
        )


class StoryMissionManager:
    """Manages main storyline missions and quest chains"""

    def __init__(self):
        self.story_chains = {}
        self.active_chains = {}
        self.completed_chains = []
        self._initialize_story_chains()

    def _initialize_story_chains(self):
        """Initialize main story mission chains"""

        # The Ancient Conspiracy Chain
        ancient_chain = MissionChain(
            id="ancient_conspiracy",
            title="The Ancient Conspiracy",
            description="Uncover an ancient conspiracy that threatens the galaxy",
            missions=[
                "ancient_artifact_discovery",
                "decode_ancient_message",
                "investigate_conspiracy",
                "confront_conspirators",
                "final_showdown",
            ],
            final_reward=MissionReward(
                credits=10000,
                experience=2000,
                items=["Ancient Technology", "Conspiracy Files"],
                unlocks=["Ancient Sector Access", "Special Ship Upgrade"],
            ),
        )

        # The Trade War Chain
        trade_war_chain = MissionChain(
            id="trade_war",
            title="The Trade War",
            description="Navigate the dangerous politics of an interstellar trade war",
            missions=[
                "trade_disruption_investigation",
                "diplomatic_mission",
                "choose_side",
                "economic_warfare",
                "peace_negotiations",
            ],
            branching_enabled=True,
            final_reward=MissionReward(
                credits=15000,
                experience=1500,
                reputation={"Traders Guild": 500},
                unlocks=["Trade War Veteran", "Economic Influence"],
            ),
        )

        # The Alien Contact Chain
        alien_contact_chain = MissionChain(
            id="alien_contact",
            title="First Contact",
            description="Humanity's first contact with an alien civilization",
            missions=[
                "alien_signal_detection",
                "first_contact_protocol",
                "cultural_exchange",
                "alien_technology_study",
                "alliance_formation",
            ],
            final_reward=MissionReward(
                credits=20000,
                experience=3000,
                items=["Alien Technology", "Universal Translator"],
                unlocks=["Alien Sectors", "Xenobiology Research"],
            ),
        )

        self.story_chains = {
            "ancient_conspiracy": ancient_chain,
            "trade_war": trade_war_chain,
            "alien_contact": alien_contact_chain,
        }

    def get_available_story_missions(
        self, player_level: int, player_progress: Dict
    ) -> List[Mission]:
        """Get story missions available to the player"""
        available_missions = []

        for chain_id, chain in self.story_chains.items():
            if chain_id in self.completed_chains:
                continue

            if chain_id not in self.active_chains:
                # Check if player meets requirements to start this chain
                if self._check_chain_prerequisites(chain, player_level, player_progress):
                    # Start the chain
                    self.active_chains[chain_id] = 0
                    first_mission = self._create_story_mission(chain_id, 0)
                    available_missions.append(first_mission)
            else:
                # Chain is active, check for next mission
                current_index = self.active_chains[chain_id]
                if current_index < len(chain.missions):
                    next_mission = self._create_story_mission(chain_id, current_index)
                    available_missions.append(next_mission)

        return available_missions

    def _check_chain_prerequisites(
        self, chain: MissionChain, player_level: int, player_progress: Dict
    ) -> bool:
        """Check if player meets prerequisites for a story chain"""
        if chain.id == "ancient_conspiracy":
            return player_level >= 10 and player_progress.get("sectors_explored", 0) >= 5
        elif chain.id == "trade_war":
            return player_level >= 15 and player_progress.get("trade_transactions", 0) >= 20
        elif chain.id == "alien_contact":
            return player_level >= 20 and "Ancient Technology" in player_progress.get("items", [])

        return True

    def _create_story_mission(self, chain_id: str, mission_index: int) -> Mission:
        """Create a specific story mission"""
        chain = self.story_chains[chain_id]
        mission_id = chain.missions[mission_index]

        # Define story missions
        story_missions = {
            # Ancient Conspiracy Chain
            "ancient_artifact_discovery": Mission(
                id="ancient_artifact_discovery",
                title="Ancient Artifact Discovery",
                description="An ancient artifact has been discovered in a remote sector. Investigate its origins.",
                type=MissionType.ARCHAEOLOGY,
                difficulty=MissionDifficulty.NORMAL,
                objectives=[
                    MissionObjective(
                        "scan_artifact",
                        ObjectiveType.SCAN,
                        "Scan the ancient artifact",
                        "Ancient Artifact",
                        1,
                    ),
                    MissionObjective(
                        "collect_data",
                        ObjectiveType.COLLECT,
                        "Collect archaeological data",
                        "Data Samples",
                        3,
                    ),
                ],
                rewards=MissionReward(credits=1000, experience=200, items=["Ancient Data"]),
                chain_id=chain_id,
                completion_text="The artifact contains technology far beyond current understanding...",
            ),
            "decode_ancient_message": Mission(
                id="decode_ancient_message",
                title="Decode Ancient Message",
                description="The artifact contains an encrypted message. Find a way to decode it.",
                type=MissionType.INVESTIGATION,
                difficulty=MissionDifficulty.HARD,
                objectives=[
                    MissionObjective(
                        "find_linguist",
                        ObjectiveType.COLLECT,
                        "Find a xenolinguist",
                        "Xenolinguist",
                        1,
                    ),
                    MissionObjective(
                        "decode_message",
                        ObjectiveType.ACTIVATE,
                        "Decode the message",
                        "Decryption",
                        1,
                    ),
                ],
                rewards=MissionReward(credits=1500, experience=300, items=["Decoded Message"]),
                chain_id=chain_id,
                completion_text="The message warns of an ancient conspiracy still active today...",
            ),
            # Trade War Chain
            "trade_disruption_investigation": Mission(
                id="trade_disruption_investigation",
                title="Trade Route Disruption",
                description="Trade routes are being mysteriously disrupted. Investigate the cause.",
                type=MissionType.INVESTIGATION,
                difficulty=MissionDifficulty.NORMAL,
                objectives=[
                    MissionObjective(
                        "investigate_routes",
                        ObjectiveType.EXPLORE,
                        "Investigate trade routes",
                        "Trade Route",
                        3,
                    ),
                    MissionObjective(
                        "collect_evidence", ObjectiveType.COLLECT, "Collect evidence", "Evidence", 5
                    ),
                ],
                rewards=MissionReward(
                    credits=800, experience=150, reputation={"Traders Guild": 100}
                ),
                chain_id=chain_id,
            ),
            # Alien Contact Chain
            "alien_signal_detection": Mission(
                id="alien_signal_detection",
                title="Unknown Signal",
                description="A mysterious signal of unknown origin has been detected. Investigate its source.",
                type=MissionType.EXPLORATION,
                difficulty=MissionDifficulty.HARD,
                objectives=[
                    MissionObjective(
                        "trace_signal",
                        ObjectiveType.SCAN,
                        "Trace the signal source",
                        "Signal Source",
                        1,
                    ),
                    MissionObjective(
                        "approach_source",
                        ObjectiveType.REACH,
                        "Approach the source",
                        "Unknown Location",
                        1,
                    ),
                ],
                rewards=MissionReward(credits=2000, experience=400, skills={"Science": 200}),
                chain_id=chain_id,
                completion_text="The signal originates from a previously unknown alien civilization...",
            ),
        }

        return story_missions.get(
            mission_id, self._create_placeholder_mission(mission_id, chain_id)
        )

    def _create_placeholder_mission(self, mission_id: str, chain_id: str) -> Mission:
        """Create a placeholder mission for undefined story missions"""
        return Mission(
            id=mission_id,
            title=f"Story Mission: {mission_id.replace('_', ' ').title()}",
            description=f"Continue the {chain_id} storyline.",
            type=MissionType.EXPLORATION,
            difficulty=MissionDifficulty.NORMAL,
            objectives=[
                MissionObjective(
                    "continue", ObjectiveType.EXPLORE, "Continue the story", "Story Progress", 1
                )
            ],
            rewards=MissionReward(credits=500, experience=100),
            chain_id=chain_id,
        )

    def complete_story_mission(self, mission_id: str) -> Dict[str, Any]:
        """Complete a story mission and advance the chain"""
        result = {"chain_completed": False, "next_mission": None, "rewards": {}}

        for chain_id, chain in self.story_chains.items():
            if chain_id in self.active_chains and mission_id in chain.missions:
                current_index = self.active_chains[chain_id]

                # Advance to next mission
                self.active_chains[chain_id] = current_index + 1

                # Check if chain is completed
                if self.active_chains[chain_id] >= len(chain.missions):
                    self.completed_chains.append(chain_id)
                    del self.active_chains[chain_id]
                    result["chain_completed"] = True
                    result["rewards"] = chain.final_reward
                else:
                    # Generate next mission
                    next_mission = self._create_story_mission(
                        chain_id, self.active_chains[chain_id]
                    )
                    result["next_mission"] = next_mission

                break

        return result


class MissionManager:
    """Main mission management system"""

    def __init__(self):
        self.active_missions = {}
        self.completed_missions = []
        self.failed_missions = []
        self.available_missions = []
        self.mission_generator = MissionGenerator()
        self.story_manager = StoryMissionManager()
        self.turn_counter = 0

    def generate_event_mission(self, sector_id: int) -> Mission:
        """Generate a mission tied to a world event.

        This helper is used by the :class:`EventEngine` to quickly produce a
        mission when a dynamic event occurs (for example, investigating an
        anomaly or responding to pirate activity).  The mission is added to the
        pool of available missions and returned for further processing.
        """
        mission = self.mission_generator.generate_mission(
            player_level=10,
            player_location=sector_id,
            player_reputation={},
        )
        mission.sector_id = sector_id
        self.available_missions.append(mission)
        return mission

    def update_turn(self):
        """Update missions at the end of each turn"""
        self.turn_counter += 1

        # Check for expired missions
        expired_missions = []
        for mission_id, mission in self.active_missions.items():
            if mission.time_limit and self.turn_counter >= mission.time_limit:
                expired_missions.append(mission_id)

        # Remove expired missions
        for mission_id in expired_missions:
            mission = self.active_missions.pop(mission_id)
            mission.status = MissionStatus.EXPIRED
            self.failed_missions.append(mission)

        # Generate new procedural missions occasionally
        if random.random() < 0.3:  # 30% chance per turn
            self._generate_new_missions()

    def _generate_new_missions(self):
        """Generate new procedural missions"""
        # This would use player data to generate appropriate missions
        # For now, generate a random mission
        if len(self.available_missions) < 10:  # Keep pool of available missions
            mission = self.mission_generator.generate_mission(
                player_level=10,  # Would get from player
                player_location=1,  # Would get from player
                player_reputation={},  # Would get from player
            )
            self.available_missions.append(mission)

    def get_available_missions(
        self, player_level: int, player_location: int, player_progress: Dict
    ) -> List[Mission]:
        """Get all missions available to the player"""
        available = []

        # Add procedural missions in player's area
        for mission in self.available_missions:
            if mission.sector_id == player_location or mission.sector_id is None:
                available.append(mission)

        # Add story missions
        story_missions = self.story_manager.get_available_story_missions(
            player_level, player_progress
        )
        available.extend(story_missions)

        return available

    def accept_mission(self, mission_id: str) -> bool:
        """Accept a mission"""
        # Find the mission
        mission = None
        for m in self.available_missions:
            if m.id == mission_id:
                mission = m
                self.available_missions.remove(m)
                break

        if mission:
            mission.status = MissionStatus.ACTIVE
            self.active_missions[mission_id] = mission
            return True

        return False

    def update_mission_progress(self, mission_id: str, objective_id: str, amount: int = 1) -> Dict:
        """Update progress on a mission objective"""
        if mission_id not in self.active_missions:
            return {"success": False, "message": "Mission not active"}

        mission = self.active_missions[mission_id]

        for objective in mission.objectives:
            if objective.id == objective_id:
                objective.current_progress += amount

                if objective.current_progress >= objective.quantity:
                    objective.completed = True

                    # Check if all objectives are complete
                    if all(obj.completed or obj.optional for obj in mission.objectives):
                        return self._complete_mission(mission_id)

                    return {
                        "success": True,
                        "message": f"Objective '{objective.description}' completed!",
                        "objective_completed": True,
                    }

                return {
                    "success": True,
                    "message": f"Progress: {objective.current_progress}/{objective.quantity}",
                    "objective_completed": False,
                }

        return {"success": False, "message": "Objective not found"}

    def _complete_mission(self, mission_id: str) -> Dict:
        """Complete a mission"""
        mission = self.active_missions.pop(mission_id)
        mission.status = MissionStatus.COMPLETED
        self.completed_missions.append(mission)

        result = {
            "success": True,
            "message": f"Mission '{mission.title}' completed!",
            "mission_completed": True,
            "rewards": mission.rewards,
            "completion_text": mission.completion_text,
        }

        # Handle story mission completion
        if mission.chain_id:
            story_result = self.story_manager.complete_story_mission(mission.id)
            result.update(story_result)

        return result

    def abandon_mission(self, mission_id: str) -> bool:
        """Abandon an active mission"""
        if mission_id in self.active_missions:
            mission = self.active_missions.pop(mission_id)
            mission.status = MissionStatus.FAILED
            self.failed_missions.append(mission)
            return True
        return False

    def get_mission_summary(self) -> Dict:
        """Get summary of all missions"""
        return {
            "active_missions": len(self.active_missions),
            "available_missions": len(self.available_missions),
            "completed_missions": len(self.completed_missions),
            "failed_missions": len(self.failed_missions),
            "active_chains": len(self.story_manager.active_chains),
            "completed_chains": len(self.story_manager.completed_chains),
        }

    def get_active_missions_display(self) -> List[Dict]:
        """Get display information for active missions"""
        display_missions = []

        for mission in self.active_missions.values():
            objectives_info = []
            for obj in mission.objectives:
                status = "✓" if obj.completed else f"{obj.current_progress}/{obj.quantity}"
                objectives_info.append(
                    {"description": obj.description, "status": status, "completed": obj.completed}
                )

            display_missions.append(
                {
                    "id": mission.id,
                    "title": mission.title,
                    "description": mission.description,
                    "type": mission.type.value,
                    "difficulty": mission.difficulty.value,
                    "objectives": objectives_info,
                    "time_remaining": (
                        mission.time_limit - self.turn_counter if mission.time_limit else None
                    ),
                    "rewards": {
                        "credits": mission.rewards.credits,
                        "experience": mission.rewards.experience,
                        "items": mission.rewards.items,
                    },
                }
            )

        return display_missions
