import pytest

from game.player import Player


def test_reputation_changes():
    player = Player()
    start = player.reputation["Federation"]

    player.improve_relationship("Federation", 20)
    assert player.reputation["Federation"] == start + 20

    player.ruin_relationship("Federation", 40)
    assert player.reputation["Federation"] == start - 20


def test_treaty_breaks_on_negative_reputation():
    player = Player()
    player.form_treaty("Pirates", "non-aggression")
    assert player.has_treaty("Pirates", "non-aggression")

    # Drop reputation below -50 which should break the treaty automatically
    player.ruin_relationship("Pirates", 60)
    assert player.reputation["Pirates"] == -60
    assert not player.has_treaty("Pirates")
