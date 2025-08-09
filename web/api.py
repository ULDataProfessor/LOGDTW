from flask import Flask, request, jsonify
from dataclasses import asdict
import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from game.save_system import SaveGameSystem, GameState

app = Flask(__name__)
save_system = SaveGameSystem(save_directory=str(BASE_DIR / 'saves'))

@app.post('/save')
def save():
    data = request.get_json(force=True)
    save_name = data.get('save_name', 'quicksave')
    game_data = data.get('game_data', {})

    player = game_data.get('player', {}).copy()
    player['inventory'] = game_data.get('inventory', [])

    game_state = GameState(
        player_data=player,
        world_data=game_data.get('world', {}),
        mission_data=game_data.get('missions', {}),
        npc_data=game_data.get('npcs', {}),
        trading_data=game_data.get('trading', {}),
        skill_data=game_data.get('skills', {}),
        combat_data=game_data.get('combat', {}),
        settings=game_data.get('settings', {}),
        statistics=game_data.get('statistics', {}),
        achievements=game_data.get('achievements', []),
        timestamp=time.time()
    )

    save_id = save_system.save_game(game_state, save_name, overwrite=True)
    if save_id:
        metadata = save_system.get_save_info(save_id)
        return jsonify({'success': True, 'message': 'Game saved successfully', 'metadata': asdict(metadata)})
    return jsonify({'success': False, 'message': 'Failed to save game'}), 500

@app.post('/load')
def load():
    data = request.get_json(force=True)
    save_name = data.get('save_name', 'quicksave')

    integrity = save_system.verify_save_integrity(save_name)
    if not integrity.get('valid'):
        return jsonify({'success': False, 'message': integrity.get('error', 'Invalid save')})

    game_state = save_system.load_game(save_name)
    if not game_state:
        return jsonify({'success': False, 'message': 'Failed to load game'})

    player_data = game_state.player_data.copy()
    inventory = player_data.pop('inventory', [])
    game_data = {
        'player': player_data,
        'world': game_state.world_data,
        'inventory': inventory,
        'skills': game_state.skill_data,
        'missions': game_state.mission_data
    }
    return jsonify({'success': True, 'message': 'Game loaded successfully', 'game_data': game_data})

if __name__ == '__main__':
    app.run()
