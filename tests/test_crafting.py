import os
import sys

# Ensure project root on path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from game.player import Player, Item
from game.crafting import RECIPES

def test_successful_crafting():
    player = Player()
    player.add_material('herb', 2)
    player.add_material('water', 1)
    prev_len = len(player.inventory)

    result = player.craft('health_potion')

    assert result['success']
    assert len(player.inventory) == prev_len + 1
    assert all(player.materials.get(mat, 0) == 0 for mat in ['herb', 'water'])


def test_missing_materials():
    player = Player()
    player.add_material('herb', 1)  # Not enough
    result = player.craft('health_potion')
    assert not result['success']
    assert 'Missing materials' in result['message']


def test_inventory_overflow():
    player = Player()
    player.add_material('herb', 2)
    player.add_material('water', 1)

    # Fill inventory
    while len(player.inventory) < player.max_inventory:
        player.add_item(Item('Junk', 'junk', 1, 'equipment'))

    materials_before = dict(player.materials)
    result = player.craft('health_potion')
    assert not result['success']
    assert 'Inventory full' in result['message']
    # Materials should remain
    assert player.materials == materials_before
