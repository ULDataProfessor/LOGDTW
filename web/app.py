#!/usr/bin/env python3
"""
Flask Web Application for LOGDTW2002
A complete web interface for the space trading game
"""

import os
import sys
import json
from copy import deepcopy
from flask import Flask, session, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash

# Add the parent directory to the path to import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from game.player import Player
    from game.world import World
    from game.enhanced_combat import EnhancedCombatSystem
    from game.procedural_generator import ProceduralGenerator
    from game.save_system import SaveGameSystem, GameState
    from game.dynamic_markets import DynamicMarketSystem
    from game.enhanced_missions import MissionManager
    from game.skills import SkillTree
    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import game modules: {e}")
    print("Running in basic mode without full game integration")
    GAME_MODULES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

# Global game systems (initialized on first use)
game_systems = {
    'procedural_generator': None,
    'save_system': None,
    'dynamic_markets': None,
    'mission_manager': None,
    'skill_tree': None,
    'enhanced_combat': None
}

def get_game_systems():
    """Initialize game systems on first use"""
    if not GAME_MODULES_AVAILABLE:
        return {}
    
    if game_systems['procedural_generator'] is None:
        game_systems['procedural_generator'] = ProceduralGenerator()
        game_systems['save_system'] = SaveGameSystem('web_saves')
        game_systems['dynamic_markets'] = DynamicMarketSystem()
        game_systems['mission_manager'] = MissionManager()
        game_systems['skill_tree'] = SkillTree()
        game_systems['enhanced_combat'] = EnhancedCombatSystem()
    
    return game_systems

DEFAULT_GAME_DATA = {
    'player': {
        'name': 'Captain',
        'ship_name': 'Starfarer',
        'level': 1,
        'credits': 1000,
        'health': 100,
        'max_health': 100,
        'energy': 100,
        'max_energy': 100,
        'fuel': 100,
        'max_fuel': 100,
        'experience': 0,
        'current_sector': 1
    },
    'world': {
        'current_location': 'Alpha Station',
        'discovered_sectors': [1],
        'turn_counter': 0
    },
    'inventory': [],
    'skills': {
        'Combat': 1,
        'Piloting': 1,
        'Trading': 1,
        'Engineering': 1
    },
    'missions': {
        'active': [],
        'completed': [],
        'available': []
    },
    'reputation': {
        'Federation': 0,
        'Empire': 0,
        'Pirates': 0,
        'Traders': 0
    }
}

def get_game_data():
    """Get or initialize game data from session"""
    if 'game_data' not in session:
        session['game_data'] = deepcopy(DEFAULT_GAME_DATA)
    return session['game_data']

def create_player_from_session():
    """Create a Player object from session data"""
    if not GAME_MODULES_AVAILABLE:
        return None
    
    data = get_game_data()
    player = Player()
    
    # Update player with session data
    player.name = data['player']['name']
    player.ship_name = data['player']['ship_name']
    player.level = data['player']['level']
    player.credits = data['player']['credits']
    player.health = data['player']['health']
    player.max_health = data['player']['max_health']
    player.energy = data['player']['energy']
    player.max_energy = data['player']['max_energy']
    player.fuel = data['player']['fuel']
    player.max_fuel = data['player']['max_fuel']
    player.experience = data['player']['experience']
    
    return player

@app.route('/')
def index():
    """Main game interface"""
    return render_template('index.html')

@app.route('/game')
def game():
    """Alternative game route"""
    return render_template('index.html')

# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current game status"""
    data = get_game_data()
    return jsonify({
        'success': True,
        'player': data['player'],
        'world': data['world'],
        'inventory': data['inventory'],
        'skills': data['skills'],
        'reputation': data['reputation']
    })

@app.route('/api/travel', methods=['POST'])
def travel():
    """Travel to a new sector"""
    data = get_game_data()
    json_data = request.get_json() or {}
    sector = int(json_data.get('sector', 0))
    
    if not (1 <= sector <= 100):  # Expanded range for procedural sectors
        return jsonify(success=False, message='Invalid sector')
    
    if data['player']['fuel'] < 10:
        return jsonify(success=False, message='Insufficient fuel')
    
    # Update player location
    data['player']['current_sector'] = sector
    data['player']['fuel'] -= 10
    data['world']['turn_counter'] += 1
    
    # Add to discovered sectors
    if sector not in data['world']['discovered_sectors']:
        data['world']['discovered_sectors'].append(sector)
    
    # Generate sector info if game modules available
    sector_info = {}
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        proc_gen = systems['procedural_generator']
        sector_data = proc_gen.generate_galaxy_sector(sector)
        sector_info = {
            'name': sector_data.name,
            'faction': sector_data.faction_control,
            'danger_level': sector_data.danger_level,
            'planets': len(sector_data.planets),
            'stations': len(sector_data.stations)
        }
    
    session.modified = True
    return jsonify({
        'success': True,
        'message': f"Jumped to Sector {sector}",
        'player': data['player'],
        'sector_info': sector_info
    })

@app.route('/api/trade', methods=['POST'])
def trade():
    """Execute a trade transaction"""
    data = get_game_data()
    json_data = request.get_json() or {}
    item = json_data.get('item')
    quantity = int(json_data.get('quantity', 0))
    action = json_data.get('trade_action')
    
    # Get dynamic prices if available
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        markets = systems['dynamic_markets']
        current_sector = data['player']['current_sector']
        
        # Initialize sector economy if needed
        if current_sector not in markets.sector_economies:
            markets.initialize_sector_economy(current_sector)
        
        market_prices = markets.get_sector_prices(current_sector)
    else:
        # Fallback static prices
        market_prices = {
            'Food': 50, 'Iron': 100, 'Electronics': 300,
            'Weapons': 800, 'Medicine': 400, 'Fuel': 75,
            'Tritium': 5000, 'Dilithium': 8000, 'Ammolite': 12000
        }
    
    if item not in market_prices:
        return jsonify(success=False, message='Invalid item')
    
    price = market_prices[item] * quantity
    
    if action == 'buy':
        if data['player']['credits'] >= price:
            data['player']['credits'] -= price
            
            # Add to inventory
            for inv_item in data['inventory']:
                if inv_item['name'] == item:
                    inv_item['quantity'] += quantity
                    break
            else:
                data['inventory'].append({'name': item, 'quantity': quantity})
            
            session.modified = True
            return jsonify({
                'success': True,
                'message': f"Bought {quantity} {item} for {price} credits",
                'credits': data['player']['credits'],
                'inventory': data['inventory']
            })
        return jsonify(success=False, message='Insufficient credits')
    
    elif action == 'sell':
        for inv_item in data['inventory']:
            if inv_item['name'] == item and inv_item['quantity'] >= quantity:
                inv_item['quantity'] -= quantity
                data['player']['credits'] += price
                
                if inv_item['quantity'] <= 0:
                    data['inventory'] = [i for i in data['inventory'] if i['name'] != item]
                
                session.modified = True
                return jsonify({
                    'success': True,
                    'message': f"Sold {quantity} {item} for {price} credits",
                    'credits': data['player']['credits'],
                    'inventory': data['inventory']
                })
        return jsonify(success=False, message='Insufficient inventory')

@app.route('/api/market', methods=['GET'])
def get_market():
    """Get current market prices"""
    data = get_game_data()
    current_sector = data['player']['current_sector']
    
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        markets = systems['dynamic_markets']
        
        if current_sector not in markets.sector_economies:
            markets.initialize_sector_economy(current_sector)
        
        prices = markets.get_sector_prices(current_sector)
        economy_info = markets.sector_economies[current_sector]
        
        return jsonify({
            'success': True,
            'prices': prices,
            'economy': {
                'wealth_level': economy_info.wealth_level,
                'specializations': economy_info.specializations,
                'market_condition': economy_info.market_condition.value
            }
        })
    else:
        # Fallback static market
        prices = {
            'Food': 50, 'Iron': 100, 'Electronics': 300,
            'Weapons': 800, 'Medicine': 400, 'Fuel': 75
        }
        return jsonify({'success': True, 'prices': prices, 'economy': {}})

@app.route('/api/combat', methods=['POST'])
def combat():
    """Handle combat encounters"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message='Combat system not available')
    
    data = get_game_data()
    json_data = request.get_json() or {}
    action = json_data.get('action', 'scan')
    
    if action == 'scan':
        # Scan for enemies
        danger_level = min(data['player']['current_sector'] // 10 + 1, 5)
        enemy_chance = danger_level * 0.2
        
        if random.random() < enemy_chance:
            enemy_types = ['space_pirate', 'alien_scout', 'rogue_trader']
            enemy = random.choice(enemy_types)
            return jsonify({
                'success': True,
                'enemies_found': True,
                'enemy_type': enemy,
                'message': f"Warning: {enemy.replace('_', ' ').title()} detected!"
            })
        else:
            return jsonify({
                'success': True,
                'enemies_found': False,
                'message': "No hostile contacts detected"
            })
    
    return jsonify(success=False, message='Unknown combat action')

@app.route('/api/missions', methods=['GET'])
def get_missions():
    """Get available missions"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=True, missions=[])
    
    data = get_game_data()
    systems = get_game_systems()
    mission_manager = systems['mission_manager']
    
    available_missions = mission_manager.get_available_missions(
        data['player']['level'],
        data['player']['current_sector'],
        data
    )
    
    # Convert missions to JSON-serializable format
    missions_data = []
    for mission in available_missions:
        missions_data.append({
            'id': mission.id,
            'title': mission.title,
            'description': mission.description,
            'type': mission.type.value,
            'difficulty': mission.difficulty.value,
            'rewards': {
                'credits': mission.rewards.credits,
                'experience': mission.rewards.experience,
                'items': mission.rewards.items
            }
        })
    
    return jsonify(success=True, missions=missions_data)

@app.route('/api/save', methods=['POST'])
def save_game():
    """Save the current game state"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message='Save system not available')
    
    json_data = request.get_json() or {}
    save_name = json_data.get('save_name', 'web_save')
    
    data = get_game_data()
    systems = get_game_systems()
    save_system = systems['save_system']
    
    # Create a GameState object
    game_state = GameState(
        player_data=data['player'],
        world_data=data['world'],
        mission_data=data['missions'],
        npc_data={},
        trading_data={},
        skill_data=data['skills'],
        combat_data={},
        settings={},
        statistics={'play_time': data['world']['turn_counter'] * 60},
        achievements=[],
        timestamp=time.time()
    )
    
    save_id = save_system.save_game(game_state, save_name, "Web save")
    
    if save_id:
        return jsonify(success=True, message=f'Game saved as {save_id}')
    else:
        return jsonify(success=False, message='Failed to save game')

@app.route('/api/load', methods=['POST'])
def load_game():
    """Load a saved game state"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message='Save system not available')
    
    json_data = request.get_json() or {}
    save_name = json_data.get('save_name', 'web_save')
    
    systems = get_game_systems()
    save_system = systems['save_system']
    
    game_state = save_system.load_game(save_name)
    
    if game_state:
        # Update session with loaded data
        session['game_data'] = {
            'player': game_state.player_data,
            'world': game_state.world_data,
            'missions': game_state.mission_data,
            'skills': game_state.skill_data,
            'inventory': [],  # Would be in player_data in full implementation
            'reputation': {}  # Would be in player_data in full implementation
        }
        session.modified = True
        
        return jsonify(success=True, message='Game loaded successfully')
    else:
        return jsonify(success=False, message='Failed to load game')

@app.route('/api/galaxy', methods=['GET'])
def get_galaxy():
    """Get galaxy map information"""
    data = get_game_data()
    discovered = data['world']['discovered_sectors']
    current = data['player']['current_sector']
    
    galaxy_map = {
        'current_sector': current,
        'discovered_sectors': discovered,
        'total_sectors': 100,
        'sectors': {}
    }
    
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        proc_gen = systems['procedural_generator']
        
        # Add info for discovered sectors
        for sector_id in discovered:
            sector_data = proc_gen.generate_galaxy_sector(sector_id)
            galaxy_map['sectors'][sector_id] = {
                'name': sector_data.name,
                'faction': sector_data.faction_control,
                'danger_level': sector_data.danger_level,
                'coordinates': sector_data.coordinates
            }
    
    return jsonify(success=True, galaxy=galaxy_map)

# ============================================================================
# Static file serving
# ============================================================================

@app.route('/css/<path:filename>')
def css_files(filename):
    """Serve CSS files"""
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    """Serve JavaScript files"""
    return send_from_directory('js', filename)

# ============================================================================
# Error handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify(success=False, message='Endpoint not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(success=False, message='Internal server error'), 500

# ============================================================================
# Development utilities
# ============================================================================

@app.route('/api/debug/reset')
def debug_reset():
    """Reset game state (development only)"""
    if app.debug:
        session.clear()
        return jsonify(success=True, message='Game state reset')
    return jsonify(success=False, message='Debug endpoint not available'), 403

@app.route('/api/debug/info')
def debug_info():
    """Get debug information"""
    if app.debug:
        return jsonify({
            'success': True,
            'game_modules_available': GAME_MODULES_AVAILABLE,
            'session_keys': list(session.keys()),
            'game_systems_initialized': any(v is not None for v in game_systems.values())
        })
    return jsonify(success=False, message='Debug endpoint not available'), 403

if __name__ == '__main__':
    import time
    import random
    
    # Set development mode
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    print("🚀 Starting LOGDTW2002 Flask Web Server")
    print("=" * 40)
    print(f"Game modules available: {GAME_MODULES_AVAILABLE}")
    print("Web interface: http://localhost:5000")
    print("API endpoints: http://localhost:5000/api/")
    print("=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=5000)