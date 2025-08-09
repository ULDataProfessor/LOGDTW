import random
import pytest

from game.save_system import SaveGameSystem, GameState
from game.player import Player
from game.world import World


@pytest.fixture
def player():
    return Player()


@pytest.fixture
def world():
    return World()


def test_save_load_round_trip(tmp_path, player, world):
    random.seed(0)
    save_system = SaveGameSystem(save_directory=str(tmp_path))
    state = GameState(
        player_data={
            'name': player.name,
            'ship_name': player.ship_name,
            'level': player.level,
            'credits': player.credits
        },
        world_data={'current_sector': world.current_sector},
        mission_data={},
        npc_data={},
        trading_data={},
        skill_data={},
        combat_data={},
        settings={},
        statistics={'play_time': 0},
        achievements=[],
        timestamp=0.0
    )
    save_id = save_system.save_game(state, save_name='test_save', overwrite=True)
    loaded = save_system.load_game(save_id)
    assert loaded == state

