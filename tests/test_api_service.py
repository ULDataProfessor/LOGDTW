import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure the service module is importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from service import app, reset_game_state

client = TestClient(app)

@pytest.fixture(autouse=True)
def _reset():
    reset_game_state()


def test_status_endpoint():
    response = client.get('/status')
    assert response.status_code == 200
    data = response.json()
    assert data['success']
    assert data['player']['name'] == 'Captain'


def test_travel_endpoint():
    response = client.post('/travel', json={'sector': 2})
    assert response.status_code == 200
    data = response.json()
    assert data['success']
    assert data['player']['current_sector'] == 2
    status = client.get('/status').json()
    assert status['player']['fuel'] == 90


def test_trade_buy_sell_cycle():
    buy = client.post('/trade', json={'item': 'Food', 'quantity': 1, 'trade_action': 'buy'})
    assert buy.status_code == 200
    assert buy.json()['success']
    sell = client.post('/trade', json={'item': 'Food', 'quantity': 1, 'trade_action': 'sell'})
    assert sell.status_code == 200
    assert sell.json()['success']
