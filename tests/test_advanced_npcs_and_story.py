import pytest
from game.npcs import NPCSystem
from game.story_content import (
    get_faction_storyline,
    get_campaign_missions,
    get_character_backstory,
    get_lore_entry,
)


def test_npc_relationship_and_behavior():
    system = NPCSystem()
    npc = system.create_npc("Alice", "trader", "Earth Station")
    # personality traits should be populated
    assert 'friendliness' in npc.personality_traits
    # adjust relationship and verify
    npc.adjust_relationship('player', 10)
    assert npc.get_relationship('player') == 10
    # update behavior with world event
    system.update_behavior(['market_crash'])
    assert any('market crash' in line.lower() for line in npc.dialogue['rumors'])


def test_story_content_retrieval():
    federation_story = get_faction_storyline('Federation')
    assert federation_story and federation_story.faction == 'Federation'

    missions = get_campaign_missions()
    assert any(mission.title == 'First Contact' for mission in missions)

    backstory = get_character_backstory('Captain Steele')
    assert backstory and 'Federation officer' in backstory.backstory

    lore = get_lore_entry('Genesis Torpedo')
    assert lore and 'worlds' in lore.content
