"""
Enhanced Skills system for LOGDTW2002
Handles player skill progression, specializations, and advanced abilities
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class SkillCategory(Enum):
    COMBAT = "combat"
    PILOTING = "piloting"
    ENGINEERING = "engineering"
    TRADE = "trade"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    SCIENCE = "science"
    SURVIVAL = "survival"


@dataclass
class SkillUnlock:
    """Represents an ability unlocked at a certain skill level"""

    name: str
    description: str
    level_required: int
    category: str
    effect: Dict
    prerequisites: List[str] = None


@dataclass
class SkillSynergy:
    """Represents bonuses when combining multiple skills"""

    skills: List[str]
    name: str
    description: str
    bonus_type: str
    bonus_value: float


class Skill:
    """Enhanced skill with specializations and unlocks"""

    def __init__(self, name: str, description: str = "", category: SkillCategory = None):
        self.name = name
        self.description = description
        self.category = category or SkillCategory.COMBAT
        self.level = 1
        self.experience = 0
        self.max_level = 100
        self.experience_to_next = 100
        self.specializations = []
        self.unlocked_abilities = []
        self.mastery_points = 0  # Points for unlocking special abilities

    def gain_experience(self, amount: int) -> Dict:
        """Gain experience in this skill, return leveling info"""
        self.experience += amount
        result = {"leveled_up": False, "new_unlocks": [], "messages": []}

        # Check for level up
        if self.experience >= self.experience_to_next and self.level < self.max_level:
            old_level = self.level
            self.level += 1
            self.experience -= self.experience_to_next
            self.experience_to_next = int(self.experience_to_next * 1.2)

            # Gain mastery points
            mastery_gained = random.randint(1, 3)
            self.mastery_points += mastery_gained

            result["leveled_up"] = True
            result["old_level"] = old_level
            result["new_level"] = self.level
            result["mastery_gained"] = mastery_gained

            # Check for new unlocks
            new_unlocks = self._check_new_unlocks()
            result["new_unlocks"] = new_unlocks

            # Generate level up message
            result["messages"].append(f"{self.name} advanced to level {self.level}!")
            if new_unlocks:
                result["messages"].append(
                    f"New abilities unlocked: {', '.join([u.name for u in new_unlocks])}"
                )

        return result

    def _check_new_unlocks(self) -> List[SkillUnlock]:
        """Check for new abilities unlocked at current level"""
        unlocks = SKILL_UNLOCKS.get(self.name, [])
        new_unlocks = []

        for unlock in unlocks:
            if unlock.level_required <= self.level and unlock.name not in [
                u.name for u in self.unlocked_abilities
            ]:

                # Check prerequisites
                if self._check_prerequisites(unlock.prerequisites):
                    self.unlocked_abilities.append(unlock)
                    new_unlocks.append(unlock)

        return new_unlocks

    def _check_prerequisites(self, prerequisites: List[str]) -> bool:
        """Check if prerequisites are met"""
        if not prerequisites:
            return True
        
        # For now, this checks if other skills exist in the skill tree
        # In a full implementation, this would check actual player skill levels
        # TODO: This needs access to player skills to check actual levels
        # For now, we'll assume basic prerequisites are met after level 5
        return self.level >= 5

    def get_progress_percentage(self) -> float:
        """Get progress percentage to next level"""
        if self.level >= self.max_level:
            return 100.0
        return (self.experience / self.experience_to_next) * 100

    def get_skill_bonus(self) -> float:
        """Get skill bonus based on level"""
        base_bonus = self.level * 0.05  # 5% per level

        # Specialization bonuses
        for spec in self.specializations:
            base_bonus += 0.02  # 2% per specialization

        return base_bonus

    def get_effectiveness(self, task_type: str = None) -> float:
        """Get effectiveness for specific task types"""
        base_effectiveness = self.level / 100.0

        # Task-specific bonuses
        if task_type and hasattr(self, f"_{task_type}_bonus"):
            base_effectiveness += getattr(self, f"_{task_type}_bonus")()

        return min(1.0, base_effectiveness)

    def add_specialization(self, specialization: str) -> bool:
        """Add a specialization to this skill"""
        if specialization not in self.specializations and len(self.specializations) < 3:
            self.specializations.append(specialization)
            return True
        return False

    def get_description(self) -> str:
        """Get detailed skill description"""
        desc = f"[bold cyan]{self.name}[/bold cyan] ([italic]{self.category.value}[/italic])\n"
        desc += f"[italic]{self.description}[/italic]\n\n"
        desc += f"Level: {self.level}/{self.max_level}\n"
        desc += f"Experience: {self.experience}/{self.experience_to_next}\n"
        desc += f"Progress: {self.get_progress_percentage():.1f}%\n"
        desc += f"Effectiveness: {self.get_effectiveness() * 100:.1f}%\n"
        desc += f"Mastery Points: {self.mastery_points}\n"

        if self.specializations:
            desc += f"\nSpecializations: {', '.join(self.specializations)}\n"

        if self.unlocked_abilities:
            desc += f"\nUnlocked Abilities:\n"
            for ability in self.unlocked_abilities:
                desc += f"  • {ability.name}: {ability.description}\n"

        return desc


class SkillTree:
    """Manages skill relationships and advancement paths"""

    def __init__(self):
        self.skills = {}
        self.synergies = []
        self._initialize_default_skills()
        self._initialize_synergies()

    def _initialize_default_skills(self):
        """Initialize the default skill set"""
        default_skills = [
            # Combat Skills
            ("Combat", "Proficiency in ship-to-ship combat", SkillCategory.COMBAT),
            ("Gunnery", "Accuracy and effectiveness with weapons", SkillCategory.COMBAT),
            ("Tactics", "Strategic combat planning and execution", SkillCategory.COMBAT),
            ("Defense", "Shield management and damage mitigation", SkillCategory.COMBAT),
            # Piloting Skills
            ("Piloting", "Ship maneuvering and navigation", SkillCategory.PILOTING),
            ("Evasion", "Avoiding attacks and hazards", SkillCategory.PILOTING),
            ("Precision", "Precise ship control and docking", SkillCategory.PILOTING),
            ("Speed", "Fast travel and quick maneuvers", SkillCategory.PILOTING),
            # Engineering Skills
            ("Engineering", "Ship systems and maintenance", SkillCategory.ENGINEERING),
            ("Repair", "Fixing damaged systems and equipment", SkillCategory.ENGINEERING),
            ("Modification", "Upgrading and customizing equipment", SkillCategory.ENGINEERING),
            ("Energy Management", "Optimizing power systems", SkillCategory.ENGINEERING),
            # Trade Skills
            ("Trading", "Buying and selling goods profitably", SkillCategory.TRADE),
            ("Negotiation", "Getting better prices and deals", SkillCategory.TRADE),
            ("Market Analysis", "Understanding market trends", SkillCategory.TRADE),
            ("Smuggling", "Moving illegal goods undetected", SkillCategory.TRADE),
            # Exploration Skills
            ("Exploration", "Discovering new sectors and secrets", SkillCategory.EXPLORATION),
            ("Scanning", "Analyzing planets and phenomena", SkillCategory.EXPLORATION),
            ("Cartography", "Mapping and navigation", SkillCategory.EXPLORATION),
            ("Xenobiology", "Understanding alien life forms", SkillCategory.EXPLORATION),
            # Social Skills
            ("Diplomacy", "Peaceful resolution of conflicts", SkillCategory.SOCIAL),
            ("Leadership", "Commanding crew and inspiring others", SkillCategory.SOCIAL),
            ("Intimidation", "Using fear to achieve goals", SkillCategory.SOCIAL),
            ("Charisma", "Personal magnetism and persuasion", SkillCategory.SOCIAL),
            # Science Skills
            ("Science", "Understanding of scientific principles", SkillCategory.SCIENCE),
            ("Research", "Conducting experiments and analysis", SkillCategory.SCIENCE),
            ("Archaeology", "Studying ancient civilizations", SkillCategory.SCIENCE),
            ("Astrophysics", "Understanding stellar phenomena", SkillCategory.SCIENCE),
            # Survival Skills
            ("Survival", "Thriving in dangerous environments", SkillCategory.SURVIVAL),
            ("Medicine", "Healing and medical treatment", SkillCategory.SURVIVAL),
            ("Security", "Protecting against threats", SkillCategory.SURVIVAL),
            ("Resourcefulness", "Making do with limited supplies", SkillCategory.SURVIVAL),
        ]

        for name, desc, category in default_skills:
            self.skills[name] = Skill(name, desc, category)

    def _initialize_synergies(self):
        """Initialize skill synergies"""
        self.synergies = [
            SkillSynergy(
                skills=["Gunnery", "Tactics"],
                name="Combat Mastery",
                description="Enhanced combat effectiveness through combined firepower and strategy",
                bonus_type="combat_damage",
                bonus_value=0.25,
            ),
            SkillSynergy(
                skills=["Piloting", "Evasion"],
                name="Ace Pilot",
                description="Superior maneuverability and survival in space",
                bonus_type="evasion_chance",
                bonus_value=0.20,
            ),
            SkillSynergy(
                skills=["Trading", "Negotiation"],
                name="Master Trader",
                description="Maximum profit from all trade transactions",
                bonus_type="trade_profit",
                bonus_value=0.30,
            ),
            SkillSynergy(
                skills=["Engineering", "Repair"],
                name="Master Engineer",
                description="Faster repairs and better equipment efficiency",
                bonus_type="repair_speed",
                bonus_value=0.50,
            ),
            SkillSynergy(
                skills=["Exploration", "Scanning"],
                name="Master Explorer",
                description="Enhanced discovery rates and detailed analysis",
                bonus_type="discovery_bonus",
                bonus_value=0.40,
            ),
            SkillSynergy(
                skills=["Diplomacy", "Leadership"],
                name="Natural Leader",
                description="Exceptional ability to influence and command",
                bonus_type="crew_effectiveness",
                bonus_value=0.35,
            ),
        ]

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)

    def check_skill_prerequisites(
        self, skill_name: str, player_skills: Dict[str, int]
    ) -> bool:
        """Check if player meets prerequisites for a skill's next unlock"""
        skill = self.get_skill(skill_name)
        if not skill:
            return False

        # Check if player has any unlocks available at current level
        if skill_name in SKILL_UNLOCKS:
            unlocks = SKILL_UNLOCKS[skill_name]
            current_level = player_skills.get(skill_name, 1)
            
            for unlock in unlocks:
                if unlock.level_required <= current_level:
                    # Check if prerequisites for this unlock are met
                    if unlock.prerequisites:
                        for prereq in unlock.prerequisites:
                            if ':' in prereq:
                                # Format: "skill_name:level"
                                req_skill, req_level = prereq.split(':')
                                if player_skills.get(req_skill, 0) < int(req_level):
                                    return False
                            else:
                                # Simple skill requirement - check if player has it
                                if prereq not in player_skills or player_skills[prereq] < 1:
                                    return False
        return True

    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a category"""
        return [skill for skill in self.skills.values() if skill.category == category]

    def get_active_synergies(self, player_skills: Dict[str, int]) -> List[SkillSynergy]:
        """Get synergies that are currently active"""
        active_synergies = []

        for synergy in self.synergies:
            # Check if all required skills are at sufficient level (10+)
            if all(player_skills.get(skill, 0) >= 10 for skill in synergy.skills):
                active_synergies.append(synergy)

        return active_synergies

    def calculate_skill_bonus(
        self, skill_name: str, base_value: float, player_skills: Dict[str, int]
    ) -> float:
        """Calculate final value with skill bonuses"""
        skill = self.get_skill(skill_name)
        if not skill:
            return base_value

        skill_level = player_skills.get(skill_name, 1)
        bonus = skill_level * 0.05  # 5% per level

        # Check for applicable synergies
        for synergy in self.get_active_synergies(player_skills):
            if skill_name in synergy.skills:
                bonus += synergy.bonus_value

        return base_value * (1.0 + bonus)

    def get_skill_recommendations(
        self, player_skills: Dict[str, int], player_actions: Dict[str, int]
    ) -> List[str]:
        """Recommend skills to improve based on player behavior"""
        recommendations = []

        # Analyze player actions to suggest relevant skills
        if player_actions.get("combat_encounters", 0) > 5:
            recommendations.extend(["Combat", "Gunnery", "Tactics"])

        if player_actions.get("trade_transactions", 0) > 10:
            recommendations.extend(["Trading", "Negotiation", "Market Analysis"])

        if player_actions.get("sectors_explored", 0) > 5:
            recommendations.extend(["Exploration", "Scanning", "Cartography"])

        if player_actions.get("repairs_made", 0) > 3:
            recommendations.extend(["Engineering", "Repair"])

        # Remove duplicates and skills already at high level
        recommendations = list(set(recommendations))
        recommendations = [skill for skill in recommendations if player_skills.get(skill, 1) < 50]

        return recommendations[:5]  # Top 5 recommendations


# Global skill unlocks definition
SKILL_UNLOCKS = {
    "Combat": [
        SkillUnlock(
            "Weapon Overcharge",
            "Increase weapon damage by 50% for 3 rounds",
            10,
            "active",
            {"type": "combat_boost", "duration": 3, "effect": "damage_boost"},
        ),
        SkillUnlock(
            "Battle Frenzy",
            "Attack twice per round when below 25% health",
            25,
            "passive",
            {"type": "conditional", "trigger": "low_health", "effect": "double_attack"},
        ),
        SkillUnlock(
            "Combat Veteran",
            "Immunity to fear and morale effects",
            50,
            "passive",
            {"type": "immunity", "effect": "fear_immunity"},
        ),
        SkillUnlock(
            "Legendary Warrior",
            "Critical hits have 25% chance to instantly defeat weak enemies",
            75,
            "passive",
            {"type": "critical", "effect": "instant_kill"},
        ),
    ],
    "Piloting": [
        SkillUnlock(
            "Evasive Maneuvers",
            "Double evasion chance for next 3 turns",
            15,
            "active",
            {"type": "evasion_boost", "duration": 3, "multiplier": 2.0},
        ),
        SkillUnlock(
            "Precision Strike",
            "Next attack has 100% accuracy and +25% damage",
            30,
            "active",
            {"type": "attack_boost", "accuracy": 1.0, "damage": 1.25},
        ),
        SkillUnlock(
            "Ace Pilot",
            "Can perform special maneuvers unavailable to others",
            60,
            "passive",
            {"type": "unlock", "effect": "special_maneuvers"},
        ),
        SkillUnlock(
            "Legendary Pilot",
            "Ship automatically evades first attack each combat",
            90,
            "passive",
            {"type": "auto_defense", "effect": "first_attack_immunity"},
        ),
    ],
    "Trading": [
        SkillUnlock(
            "Market Insight",
            "See exact supply/demand for all goods",
            20,
            "passive",
            {"type": "information", "effect": "market_transparency"},
        ),
        SkillUnlock(
            "Bulk Discount",
            "Buying 10+ units gives 15% discount",
            35,
            "passive",
            {"type": "trade_bonus", "threshold": 10, "discount": 0.15},
        ),
        SkillUnlock(
            "Trade Empire",
            "Establish trade routes that generate passive income",
            70,
            "active",
            {"type": "passive_income", "effect": "trade_routes"},
        ),
        SkillUnlock(
            "Economic Mastermind",
            "Can manipulate sector economies",
            95,
            "active",
            {"type": "market_control", "effect": "price_manipulation"},
        ),
    ],
    "Engineering": [
        SkillUnlock(
            "Emergency Repair",
            "Instantly restore 50% hull and shields",
            12,
            "active",
            {"type": "healing", "hull": 0.5, "shields": 0.5},
        ),
        SkillUnlock(
            "Jury Rig",
            "Temporarily boost any ship system by 100%",
            28,
            "active",
            {"type": "system_boost", "multiplier": 2.0, "duration": 5},
        ),
        SkillUnlock(
            "Master Engineer",
            "All ship systems operate at 150% efficiency",
            55,
            "passive",
            {"type": "efficiency", "multiplier": 1.5},
        ),
        SkillUnlock(
            "Technological Singularity",
            "Create unique, one-of-a-kind equipment",
            85,
            "active",
            {"type": "crafting", "effect": "unique_items"},
        ),
    ],
}


class SkillChallenge:
    """Represents a skill-based challenge with success chances"""

    def __init__(
        self,
        name: str,
        description: str,
        required_skills: Dict[str, int],
        success_rewards: Dict,
        failure_consequences: Dict,
    ):
        self.name = name
        self.description = description
        self.required_skills = required_skills
        self.success_rewards = success_rewards
        self.failure_consequences = failure_consequences

    def calculate_success_chance(self, player_skills: Dict[str, int]) -> float:
        """Calculate chance of success based on player skills"""
        total_chance = 0.0
        skill_count = len(self.required_skills)

        for skill, required_level in self.required_skills.items():
            player_level = player_skills.get(skill, 1)
            skill_chance = min(1.0, player_level / required_level)
            total_chance += skill_chance

        return min(0.95, total_chance / skill_count)  # Max 95% success

    def attempt_challenge(self, player_skills: Dict[str, int]) -> Dict:
        """Attempt the challenge and return results"""
        success_chance = self.calculate_success_chance(player_skills)
        success = random.random() < success_chance

        result = {
            "success": success,
            "chance": success_chance,
            "rewards": self.success_rewards if success else {},
            "consequences": {} if success else self.failure_consequences,
            "experience_gained": {},
        }

        # Award experience for attempt
        for skill in self.required_skills:
            base_exp = 50 if success else 25
            result["experience_gained"][skill] = base_exp

        return result
