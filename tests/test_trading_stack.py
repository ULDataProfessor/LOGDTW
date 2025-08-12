"""Tests for trading and item stacking mechanics."""

import random

from game.player import Player, Item
from game.trading import TradingSystem


def test_player_add_item_stacks_trade_goods():
    """Identical trade goods should stack via quantity."""
    player = Player()

    gold1 = Item("Gold", "Precious metal", 100, "trade_good")
    gold2 = Item("Gold", "Precious metal", 100, "trade_good")

    assert player.add_item(gold1)
    assert player.add_item(gold2)

    item = player.get_item("Gold")
    assert item is not None
    assert item.quantity == 2
    # Only one inventory slot should be used for both items
    assert len([i for i in player.inventory if i.name == "Gold"]) == 1


def test_buy_item_stacks_in_inventory():
    """Buying multiple units should stack rather than duplicate entries."""
    random.seed(0)
    player = Player()
    trading = TradingSystem()

    # Purchase two Energy Cells
    result = trading.buy_item(player, "Earth Station", "Energy Cells", quantity=2)
    assert result["success"]
    item = player.get_item("Energy Cells")
    assert item is not None
    assert item.quantity == 2
    inventory_count = len(player.inventory)

    # Purchase three more; quantity should increase but inventory count stay the same
    result = trading.buy_item(player, "Earth Station", "Energy Cells", quantity=3)
    assert result["success"]
    item = player.get_item("Energy Cells")
    assert item.quantity == 5
    assert len(player.inventory) == inventory_count
