"""Crafting system with recipes and crafting API."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, Any

from game.player import Item, Player

# Basic recipe definitions. Keys are recipe names, values contain required
# materials and the resulting item template. The result is deep copied when
# crafting to avoid shared state between items.
RECIPES: Dict[str, Dict[str, Any]] = {
    "health_potion": {
        "materials": {"herb": 2, "water": 1},
        "result": Item("Health Potion", "Restores health", 10, "consumable"),
    }
}


def craft_item(player: Player, recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to craft an item for the given player.

    Args:
        player: The player performing the crafting.
        recipe: Recipe dictionary containing ``materials`` and ``result``.

    Returns:
        Dictionary with ``success`` flag and additional info/message.
    """
    required = recipe.get("materials", {})

    if not player.has_materials(required):
        return {"success": False, "message": "Missing materials"}

    if len(player.inventory) >= player.max_inventory:
        return {"success": False, "message": "Inventory full"}

    # Remove materials and add crafted item
    player.remove_materials(required)
    crafted = deepcopy(recipe["result"])
    player.add_item(crafted)
    return {"success": True, "item": crafted}
