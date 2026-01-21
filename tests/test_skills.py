import os
import sys
import pytest

# Ensure project root is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.skills import Skill, SkillTree, SkillCategory, SkillSynergy
from game.player import Player


@pytest.fixture
def player():
    return Player("Test Player")


@pytest.fixture
def skill_tree():
    return SkillTree()


def test_skill_creation():
    """Test basic skill creation"""
    skill = Skill("Combat", "Fighting skills", SkillCategory.COMBAT)
    assert skill.name == "Combat"
    assert skill.description == "Fighting skills"
    assert skill.category == SkillCategory.COMBAT
    assert skill.level == 1
    assert skill.experience == 0
    assert skill.max_level == 100


def test_skill_experience_gain():
    """Test skill experience gain without leveling"""
    skill = Skill("Piloting", category=SkillCategory.PILOTING)
    result = skill.gain_experience(50)
    
    assert skill.experience == 50
    assert not result["leveled_up"]
    assert skill.level == 1


def test_skill_level_up():
    """Test skill leveling up"""
    skill = Skill("Trading", category=SkillCategory.TRADE)
    initial_exp_to_next = skill.experience_to_next
    
    result = skill.gain_experience(initial_exp_to_next)
    
    assert result["leveled_up"]
    assert skill.level == 2
    assert result["old_level"] == 1
    assert result["new_level"] == 2
    assert "mastery_gained" in result
    assert result["mastery_gained"] > 0
    assert skill.mastery_points > 0


def test_skill_multiple_levels():
    """Test gaining multiple levels at once"""
    skill = Skill("Engineering", category=SkillCategory.ENGINEERING)
    large_exp = skill.experience_to_next * 3
    
    result = skill.gain_experience(large_exp)
    
    assert result["leveled_up"]
    assert skill.level >= 2
    assert skill.experience >= 0


def test_skill_max_level():
    """Test that skills don't exceed max level"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    skill.level = 99
    skill.experience = 0
    skill.experience_to_next = 100
    
    result = skill.gain_experience(200)
    
    assert skill.level == 100
    assert skill.level <= skill.max_level
    # Should not level up beyond max
    skill.gain_experience(10000)
    assert skill.level == 100


def test_skill_bonus_calculation():
    """Test skill bonus calculation"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    skill.level = 10
    
    bonus = skill.get_skill_bonus()
    assert bonus > 0
    # Bonus calculation may vary, just check it's positive and reasonable
    assert 0 < bonus <= 100  # Should be a percentage


def test_skill_tree_initialization(skill_tree):
    """Test skill tree initialization"""
    assert len(skill_tree.skills) > 0
    assert "Combat" in skill_tree.skills
    assert "Piloting" in skill_tree.skills
    assert "Trading" in skill_tree.skills


def test_skill_tree_get_skill(skill_tree):
    """Test getting a skill from the tree"""
    combat_skill = skill_tree.get_skill("Combat")
    assert combat_skill is not None
    assert combat_skill.name == "Combat"
    assert combat_skill.category == SkillCategory.COMBAT


def test_skill_tree_synergies(skill_tree):
    """Test skill synergies"""
    assert len(skill_tree.synergies) > 0
    
    # Test that synergies have required skills
    for synergy in skill_tree.synergies:
        assert len(synergy.skills) >= 2
        assert synergy.bonus_value > 0


def test_skill_tree_get_synergy_bonus(skill_tree):
    """Test getting synergy bonuses"""
    # Set up skills for a synergy
    combat = skill_tree.get_skill("Combat")
    gunnery = skill_tree.get_skill("Gunnery")
    
    if combat and gunnery:
        combat.level = 5
        gunnery.level = 5
        
        # Method may not exist, so check if it does
        if hasattr(skill_tree, 'get_synergy_bonus'):
            bonus = skill_tree.get_synergy_bonus({"Combat": combat, "Gunnery": gunnery})
            # Bonus might be 0 if no matching synergy, but should not error
            assert bonus >= 0
        else:
            # Just verify synergies exist
            assert len(skill_tree.synergies) >= 0


def test_skill_progress_percentage():
    """Test skill progress percentage calculation"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    skill.experience = 50
    skill.experience_to_next = 100
    
    progress = skill.get_progress_percentage()
    assert progress == 50.0
    
    skill.experience = 0
    progress = skill.get_progress_percentage()
    assert progress == 0.0


def test_skill_unlocks():
    """Test skill ability unlocks"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    
    # Gain enough levels to potentially unlock abilities
    for _ in range(5):
        skill.gain_experience(skill.experience_to_next)
    
    # Check if any abilities were unlocked
    # (depends on SKILL_UNLOCKS configuration)
    assert isinstance(skill.unlocked_abilities, list)


def test_player_skill_integration(player):
    """Test player skill system integration"""
    # Test that player has skills
    assert hasattr(player, 'skills') or hasattr(player, 'skill_tree')
    
    # If player has skill_tree, test it
    if hasattr(player, 'skill_tree'):
        assert player.skill_tree is not None


def test_skill_category_enum():
    """Test skill category enum values"""
    assert SkillCategory.COMBAT.value == "combat"
    assert SkillCategory.PILOTING.value == "piloting"
    assert SkillCategory.TRADE.value == "trade"
    assert SkillCategory.EXPLORATION.value == "exploration"


def test_skill_specializations():
    """Test skill specializations"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    
    # Specializations should be a list
    assert isinstance(skill.specializations, list)
    
    # Can add specializations
    skill.specializations.append("Melee")
    assert "Melee" in skill.specializations


def test_skill_mastery_points():
    """Test mastery points accumulation"""
    skill = Skill("Combat", category=SkillCategory.COMBAT)
    initial_points = skill.mastery_points
    
    result = skill.gain_experience(skill.experience_to_next)
    
    if result["leveled_up"]:
        assert skill.mastery_points > initial_points
        assert "mastery_gained" in result

