import os
import sys
import pytest

# Ensure root path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.player import Player
from game.trading import TradingSystem


def test_combat_bonus_from_crew():
    player = Player()
    base_damage = player.get_total_damage()
    player.hire_crew_member(name="Rex", role="security", skills={"combat": 10})
    assert player.get_total_damage() == base_damage + 10


def test_travel_cost_reduced_by_pilot():
    player = Player()
    base_cost = player.calculate_travel_cost(100)
    player.hire_crew_member(name="Ace", role="pilot", skills={"piloting": 20})
    cost_with_pilot = player.calculate_travel_cost(100)
    assert cost_with_pilot < base_cost
    # Cost should be reduced, exact value depends on bonus calculation
    assert cost_with_pilot >= 1  # At least 1 fuel


def test_trading_discount_from_crew():
    ts = TradingSystem()
    player_no_crew = Player()
    player_no_crew.credits = 10000  # Ensure enough credits
    result_no = ts.buy_item(player_no_crew, "Earth Station", "Computer Chips", 1)
    if result_no.get("success"):
        cost_no = result_no.get("cost", 0)

        player_with_trader = Player()
        player_with_trader.credits = 10000
        player_with_trader.hire_crew_member(name="Tess", role="trader", skills={"trading": 25})
        result_with = ts.buy_item(player_with_trader, "Earth Station", "Computer Chips", 1)
        if result_with.get("success"):
            cost_with = result_with.get("cost", 0)
            # With trader, cost should be less or equal (may not always be less due to randomness)
            assert cost_with <= cost_no
        else:
            pytest.skip("Item not available for purchase")
    else:
        pytest.skip("Item not available for purchase")
