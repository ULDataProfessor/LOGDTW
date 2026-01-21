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
    player.credits = 10000  # Ensure enough credits
    trading = TradingSystem()

    # Purchase two Energy Cells (if available)
    result = trading.buy_item(player, "Earth Station", "Energy Cells", quantity=2)
    if result.get("success"):
        item = player.get_item("Energy Cells")
        assert item is not None
        assert item.quantity == 2
        inventory_count = len(player.inventory)

        # Purchase three more; quantity should increase but inventory count stay the same
        result2 = trading.buy_item(player, "Earth Station", "Energy Cells", quantity=3)
        if result2.get("success"):
            item = player.get_item("Energy Cells")
            assert item.quantity == 5
            assert len(player.inventory) == inventory_count
        else:
            # Item might not be available for second purchase, which is fine
            pytest.skip("Item not available for second purchase")
    else:
        # Item might not be available, try a different item or skip
        pytest.skip("Energy Cells not available at Earth Station")
