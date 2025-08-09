import os
import sys
import io

from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'game'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from main import Game
from game.save_system import SaveGameSystem
from utils.display import DisplayManager
from rich.console import Console


def test_achievement_unlock_and_persistence(tmp_path):
    game = Game()
    game.save_system = SaveGameSystem(save_directory=str(tmp_path))
    game.initialize_game()

    player = game.player
    world = game.world
    achievements = game.achievements

    # Trigger achievement conditions
    player.credits = 2500  # Rich Captain
    world.discovered_sectors.update({2, 3, 4})  # Sector Explorer
    achievements.check(player, world)

    assert 'rich_captain' in achievements.unlocked
    assert 'sector_explorer' in achievements.unlocked
    assert 'Wealthy Trader' in player.titles
    assert 'Explorer' in player.titles

    # Save game state
    state = game._create_game_state()
    save_id = game.save_system.save_game(state, 'ach_test', overwrite=True)
    assert save_id

    # Reset achievements and titles
    achievements.unlocked.clear()
    player.titles = []

    # Load and apply game state
    loaded_state = game.save_system.load_game(save_id)
    assert loaded_state is not None
    game._apply_game_state(loaded_state)

    assert 'rich_captain' in game.achievements.unlocked
    assert 'Wealthy Trader' in game.player.titles

    # Ensure status display shows achievements
    display = DisplayManager()
    buffer = io.StringIO()
    display.console = Console(file=buffer, force_terminal=False)
    display.show_status(player, achievements=game.achievements.get_unlocked_names())
    output = buffer.getvalue()
    assert 'Rich Captain' in output
    assert 'Sector Explorer' in output
