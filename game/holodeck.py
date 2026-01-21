"""
Holodeck system for LOGDTW2002
Provides interactive simulations and entertainment
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from game.player import Player


@dataclass
class HolodeckProgram:
    """Represents a holodeck program"""

    name: str
    description: str
    category: str  # adventure, relaxation, training, entertainment
    cost: int
    duration: int  # minutes
    difficulty: int  # 1-10 scale
    rewards: Dict = None

    def __post_init__(self):
        if self.rewards is None:
            self.rewards = {}


class HolodeckSystem:
    """Handles holodeck programs and simulations"""

    def __init__(self):
        self.programs = {}
        self.active_program = None
        self.session_start = 0
        self._create_programs()

    def _create_programs(self):
        """Create available holodeck programs"""
        programs_data = [
            {
                "name": "Beach Resort Simulation",
                "description": "Relax on a pristine beach with crystal clear waters",
                "category": "relaxation",
                "cost": 25,
                "duration": 30,
                "difficulty": 1,
                "rewards": {"energy": 20, "experience": 5},
            },
            {
                "name": "Mountain Adventure",
                "description": "Climb challenging peaks and explore alpine terrain",
                "category": "adventure",
                "cost": 40,
                "duration": 45,
                "difficulty": 5,
                "rewards": {"experience": 15, "strength": 2},
            },
            {
                "name": "Space Battle Simulation",
                "description": "Engage in intense space combat scenarios",
                "category": "training",
                "cost": 60,
                "duration": 60,
                "difficulty": 7,
                "rewards": {"experience": 25, "combat_skill": 3},
            },
            {
                "name": "Alien World Exploration",
                "description": "Explore mysterious alien landscapes and creatures",
                "category": "adventure",
                "cost": 50,
                "duration": 50,
                "difficulty": 6,
                "rewards": {"experience": 20, "knowledge": 2},
            },
            {
                "name": "Historical Battle Reenactment",
                "description": "Participate in famous historical battles",
                "category": "training",
                "cost": 45,
                "duration": 40,
                "difficulty": 6,
                "rewards": {"experience": 18, "tactics": 2},
            },
            {
                "name": "Jungle Survival",
                "description": "Survive in a hostile jungle environment",
                "category": "adventure",
                "cost": 35,
                "duration": 35,
                "difficulty": 4,
                "rewards": {"experience": 12, "survival": 2},
            },
            {
                "name": "Meditation Garden",
                "description": "Find inner peace in a serene garden setting",
                "category": "relaxation",
                "cost": 20,
                "duration": 25,
                "difficulty": 1,
                "rewards": {"energy": 15, "mental_health": 3},
            },
            {
                "name": "Zero Gravity Training",
                "description": "Practice maneuvering in zero gravity conditions",
                "category": "training",
                "cost": 30,
                "duration": 30,
                "difficulty": 3,
                "rewards": {"experience": 10, "piloting": 2},
            },
            {
                "name": "Underwater City",
                "description": "Explore a magnificent underwater civilization",
                "category": "adventure",
                "cost": 55,
                "duration": 55,
                "difficulty": 5,
                "rewards": {"experience": 22, "exploration": 3},
            },
            {
                "name": "Virtual Concert Hall",
                "description": "Enjoy classical music in a grand concert hall",
                "category": "entertainment",
                "cost": 15,
                "duration": 20,
                "difficulty": 1,
                "rewards": {"energy": 10, "culture": 2},
            },
        ]

        for prog_data in programs_data:
            program = HolodeckProgram(**prog_data)
            self.programs[prog_data["name"]] = program

    def get_available_programs(self) -> List[HolodeckProgram]:
        """Get all available programs"""
        return list(self.programs.values())

    def get_programs_by_category(self, category: str) -> List[HolodeckProgram]:
        """Get programs by category"""
        return [prog for prog in self.programs.values() if prog.category == category]

    def start_program(self, player: Player, program_name: str) -> Dict:
        """Start a holodeck program"""
        if program_name not in self.programs:
            return {"success": False, "message": "Program not found"}

        program = self.programs[program_name]

        # Check if player has enough credits
        if player.credits < program.cost:
            return {
                "success": False,
                "message": f"Not enough credits. Need {program.cost}, have {player.credits}",
            }

        # Check if player has enough energy
        if player.energy < 20:
            return {"success": False, "message": "You are too tired for holodeck activities"}

        # Start the program
        self.active_program = program
        self.session_start = time.time()

        # Deduct credits
        player.spend_credits(program.cost)

        return {"success": True, "message": f"Starting {program.name}...", "program": program}

    def update_program(self, player: Player) -> Dict:
        """Update active program progress"""
        if not self.active_program:
            return {"active": False}

        elapsed_time = (time.time() - self.session_start) / 60  # Convert to minutes
        progress = min(100, (elapsed_time / self.active_program.duration) * 100)

        if progress >= 100:
            # Program completed
            return self._complete_program(player)

        return {
            "active": True,
            "program": self.active_program,
            "progress": progress,
            "remaining_time": max(0, self.active_program.duration - elapsed_time),
        }

    def _complete_program(self, player: Player) -> Dict:
        """Complete the active program and give rewards"""
        program = self.active_program

        # Give rewards
        rewards_given = []
        for reward_type, amount in program.rewards.items():
            if reward_type == "energy":
                player.add_energy(amount)
                rewards_given.append(f"+{amount} Energy")
            elif reward_type == "experience":
                player.gain_experience(amount)
                rewards_given.append(f"+{amount} Experience")
            elif reward_type == "strength":
                player.stats["strength"] += amount
                rewards_given.append(f"+{amount} Strength")
            elif reward_type == "combat_skill":
                if "combat" in player.skills:
                    player.skills["combat"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Combat Skill")
            elif reward_type == "knowledge":
                if "knowledge" in player.skills:
                    player.skills["knowledge"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Knowledge")
            elif reward_type == "tactics":
                if "tactics" in player.skills:
                    player.skills["tactics"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Tactics")
            elif reward_type == "survival":
                if "survival" in player.skills:
                    player.skills["survival"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Survival")
            elif reward_type == "mental_health":
                player.add_mental_health(amount)
                rewards_given.append(f"+{amount} Mental Health")
            elif reward_type == "piloting":
                if "piloting" in player.skills:
                    player.skills["piloting"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Piloting")
            elif reward_type == "exploration":
                if "exploration" in player.skills:
                    player.skills["exploration"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Exploration")
            elif reward_type == "culture":
                if "culture" in player.skills:
                    player.skills["culture"].gain_experience(amount, player_skills_dict)
                rewards_given.append(f"+{amount} Culture")

        # Reset active program
        self.active_program = None
        self.session_start = 0

        return {
            "active": False,
            "completed": True,
            "program": program,
            "rewards": rewards_given,
            "message": f'Completed {program.name}! Rewards: {", ".join(rewards_given)}',
        }

    def end_program(self, player: Player) -> Dict:
        """End the active program early"""
        if not self.active_program:
            return {"success": False, "message": "No active program"}

        program = self.active_program
        self.active_program = None
        self.session_start = 0

        return {"success": True, "message": f"Ended {program.name} early"}

    def get_program_description(self, program_name: str) -> str:
        """Get detailed description of a program"""
        if program_name not in self.programs:
            return "Program not found"

        program = self.programs[program_name]

        desc = f"[bold cyan]{program.name}[/bold cyan]\n"
        desc += f"[italic]{program.description}[/italic]\n\n"
        desc += f"Category: {program.category.title()}\n"
        desc += f"Cost: {program.cost} credits\n"
        desc += f"Duration: {program.duration} minutes\n"
        desc += f"Difficulty: {program.difficulty}/10\n"

        if program.rewards:
            desc += "\n[bold yellow]Rewards:[/bold yellow]\n"
            for reward_type, amount in program.rewards.items():
                desc += f"  • {reward_type.title()}: +{amount}\n"

        return desc

    def get_program_suggestions(self, player: Player) -> List[HolodeckProgram]:
        """Get program suggestions based on player state"""
        suggestions = []

        # If player is low on energy, suggest relaxation programs
        if player.energy < 50:
            relaxation_programs = self.get_programs_by_category("relaxation")
            suggestions.extend(relaxation_programs[:2])

        # If player is low level, suggest training programs
        if player.level < 5:
            training_programs = self.get_programs_by_category("training")
            suggestions.extend(training_programs[:2])

        # If player has lots of credits, suggest expensive programs
        if player.credits > 200:
            expensive_programs = [prog for prog in self.programs.values() if prog.cost > 40]
            suggestions.extend(expensive_programs[:2])

        # Add some random programs
        all_programs = list(self.programs.values())
        random_programs = random.sample(all_programs, min(3, len(all_programs)))
        suggestions.extend(random_programs)

        return list(set(suggestions))  # Remove duplicates
