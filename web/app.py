from copy import deepcopy
from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = "dev-secret"  # For session management; replace in production

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
    }
}

def get_game_data():
    if 'game_data' not in session:
        session['game_data'] = deepcopy(DEFAULT_GAME_DATA)
    return session['game_data']

@app.route('/api/get_status', methods=['GET'])
def get_status():
    data = get_game_data()
    return jsonify(success=True, player=data['player'], world=data['world'])

@app.route('/api/travel', methods=['POST'])
def travel():
    data = get_game_data()
    json_data = request.get_json() or {}
    sector = int(json_data.get('sector', 0))
    if 0 < sector <= 20:
        data['player']['current_sector'] = sector
        data['player']['fuel'] -= 10
        data['world']['turn_counter'] += 1
        if sector not in data['world']['discovered_sectors']:
            data['world']['discovered_sectors'].append(sector)
        session.modified = True
        return jsonify(success=True, message=f"Jumped to Sector {sector}", player=data['player'])
    return jsonify(success=False, message='Invalid sector')

@app.route('/api/trade', methods=['POST'])
def trade():
    data = get_game_data()
    json_data = request.get_json() or {}
    item = json_data.get('item')
    quantity = int(json_data.get('quantity', 0))
    action = json_data.get('trade_action')

    market_prices = {
        'Food': 50,
        'Iron': 100,
        'Electronics': 300,
        'Weapons': 800,
        'Medicine': 400,
        'Fuel': 75
    }

    if item not in market_prices:
        return jsonify(success=False, message='Invalid item')

    price = market_prices[item] * quantity

    if action == 'buy':
        if data['player']['credits'] >= price:
            data['player']['credits'] -= price
            for inv_item in data['inventory']:
                if inv_item['name'] == item:
                    inv_item['quantity'] += quantity
                    break
            else:
                data['inventory'].append({'name': item, 'quantity': quantity})
            session.modified = True
            return jsonify(success=True, message=f"Bought {quantity} {item} for {price} credits", credits=data['player']['credits'])
        return jsonify(success=False, message='Insufficient credits')
    else:  # sell
        for inv_item in data['inventory']:
            if inv_item['name'] == item and inv_item['quantity'] >= quantity:
                inv_item['quantity'] -= quantity
                data['player']['credits'] += price
                if inv_item['quantity'] <= 0:
                    data['inventory'] = [i for i in data['inventory'] if i['name'] != item]
                session.modified = True
                return jsonify(success=True, message=f"Sold {quantity} {item} for {price} credits", credits=data['player']['credits'])
        return jsonify(success=False, message='Insufficient inventory')

if __name__ == '__main__':
    app.run(debug=True)
