import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from game.player import Player


def test_install_and_remove_upgrade():
    player = Player()
    base_engine = player.ship["engine_power"]

    assert player.install_upgrade("engine_mk2")
    assert player.ship["engine_power"] == base_engine + 20
    assert player.ship["upgrades"]["engine"] == "Engine Mk II"

    # Cannot install again in same slot
    assert not player.install_upgrade("engine_mk2")

    assert player.remove_upgrade("engine")
    assert player.ship["engine_power"] == base_engine
    assert "engine" not in player.ship.get("upgrades", {})


def test_persist_upgrades():
    player = Player()
    base_shield = player.ship["shield_capacity"]
    player.install_upgrade("shield_mk2")

    saved_upgrades = player.ship_customization.to_dict()
    new_player = Player()
    new_player.ship_customization.load_from_dict(saved_upgrades, apply_stats=True)

    assert new_player.ship["shield_capacity"] == base_shield + 50
    assert new_player.ship["upgrades"]["shield"] == "Shield Mk II"
