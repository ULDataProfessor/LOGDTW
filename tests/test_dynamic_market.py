import random
import pytest

from game.dynamic_markets import DynamicMarketSystem
from game.player import Player
from game.world import World


@pytest.fixture
def player():
    return Player()


@pytest.fixture
def world():
    return World()


def test_price_update(player, world):
    random.seed(0)
    market = DynamicMarketSystem()
    initial_price = market.commodities["Food"].current_price
    market.update_market(1)
    updated_price = market.commodities["Food"].current_price
    assert updated_price == pytest.approx(48.3424665093561)
    assert updated_price != initial_price


def test_event_effect(player, world):
    random.seed(0)
    market = DynamicMarketSystem()
    initial_price = market.commodities["AI Cores"].current_price
    random.seed(0)
    market._trigger_random_event()
    assert market.commodities["AI Cores"].event_modifier == pytest.approx(0.6)
    market.update_market(1)
    updated_price = market.commodities["AI Cores"].current_price
    assert updated_price == pytest.approx(10587.776386834694)
    assert updated_price < initial_price
