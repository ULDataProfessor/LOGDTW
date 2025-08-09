import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from main import Game
from game.save_system import SaveGameSystem


def test_save_and_load_game_session(tmp_path):
    game = Game()
    game.save_system = SaveGameSystem(save_directory=str(tmp_path))
    game.initialize_game()

    game.player.name = "Tester"
    game.player.credits = 123
    game.world.current_sector = 5

    state = game._create_game_state()
    save_id = game.save_system.save_game(state, "unit_test_save", overwrite=True)
    assert save_id is not None

    game.player.name = "Changed"
    game.player.credits = 999
    game.world.current_sector = 9

    loaded_state = game.save_system.load_game(save_id)
    assert loaded_state is not None
    game._apply_game_state(loaded_state)

    assert game.player.name == "Tester"
    assert game.player.credits == 123
    assert game.world.current_sector == 5
