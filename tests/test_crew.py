import os
import sys
import pytest

# Ensure root path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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
    assert cost_with_pilot == 80


def test_trading_discount_from_crew():
    ts = TradingSystem()
    player_no_crew = Player()
    player_no_crew.credits = 1000
    result_no = ts.buy_item(player_no_crew, "Earth Station", "Computer Chips", 1)
    cost_no = result_no["cost"]

    player_with_trader = Player()
    player_with_trader.credits = 1000
    player_with_trader.hire_crew_member(name="Tess", role="trader", skills={"trading": 25})
    result_with = ts.buy_item(player_with_trader, "Earth Station", "Computer Chips", 1)
    cost_with = result_with["cost"]

    assert cost_with < cost_no
