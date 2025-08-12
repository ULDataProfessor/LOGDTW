import random
import pytest

from game.stock_market import StockMarket
from game.player import Player
from game.world import World


@pytest.fixture
def player():
    return Player()


@pytest.fixture
def world():
    return World()


def test_stock_price_update(player, world):
    random.seed(0)
    market = StockMarket()
    market.last_update -= 1000
    initial_price = market.stocks["TECH"].current_price
    market.update_market()
    updated_price = market.stocks["TECH"].current_price
    assert updated_price == pytest.approx(161.30058485616797)
    assert updated_price != initial_price
