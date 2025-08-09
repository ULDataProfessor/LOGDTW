from fastapi import FastAPI
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# In-memory game state
# ---------------------------------------------------------------------------

def _default_state():
    return {
        "player": {
            "name": "Captain",
            "ship_name": "Starfarer",
            "level": 1,
            "credits": 1000,
            "health": 100,
            "max_health": 100,
            "energy": 100,
            "max_energy": 100,
            "fuel": 100,
            "max_fuel": 100,
            "experience": 0,
            "current_sector": 1,
        },
        "world": {
            "current_location": "Alpha Station",
            "discovered_sectors": [1],
            "turn_counter": 0,
        },
        "inventory": [],
        "skills": {
            "Combat": 1,
            "Piloting": 1,
            "Trading": 1,
            "Engineering": 1,
        },
        "missions": {
            "active": [],
            "completed": [],
            "available": [],
        },
    }


game_state = _default_state()


def reset_game_state():
    """Reset the in-memory game state. Used by tests."""
    global game_state
    game_state = _default_state()


app = FastAPI(title="LOGDTW API")


class TravelRequest(BaseModel):
    sector: int


class TradeRequest(BaseModel):
    item: str
    quantity: int
    trade_action: str  # "buy" or "sell"


@app.get("/status")
def get_status():
    """Return current player and world state."""
    return {
        "success": True,
        "player": game_state["player"],
        "world": game_state["world"],
    }


@app.post("/travel")
def travel(req: TravelRequest):
    sector = req.sector
    if 1 <= sector <= 20:
        game_state["player"]["current_sector"] = sector
        game_state["player"]["fuel"] -= 10
        game_state["world"]["turn_counter"] += 1
        if sector not in game_state["world"]["discovered_sectors"]:
            game_state["world"]["discovered_sectors"].append(sector)
        return {
            "success": True,
            "message": f"Jumped to Sector {sector}",
            "player": game_state["player"],
        }
    return {"success": False, "message": "Invalid sector"}


MARKET_PRICES = {
    "Food": 50,
    "Iron": 100,
    "Electronics": 300,
    "Weapons": 800,
    "Medicine": 400,
    "Fuel": 75,
}


@app.post("/trade")
def trade(req: TradeRequest):
    item = req.item
    quantity = req.quantity
    action = req.trade_action

    if item not in MARKET_PRICES:
        return {"success": False, "message": "Unknown item"}

    price = MARKET_PRICES[item] * quantity

    if action == "buy":
        if game_state["player"]["credits"] >= price:
            game_state["player"]["credits"] -= price
            for inv_item in game_state["inventory"]:
                if inv_item["name"] == item:
                    inv_item["quantity"] += quantity
                    break
            else:
                game_state["inventory"].append({"name": item, "quantity": quantity})
            return {
                "success": True,
                "message": f"Bought {quantity} {item} for {price} credits",
                "credits": game_state["player"]["credits"],
            }
        return {"success": False, "message": "Insufficient credits"}

    if action == "sell":
        for inv_item in game_state["inventory"]:
            if inv_item["name"] == item and inv_item["quantity"] >= quantity:
                inv_item["quantity"] -= quantity
                game_state["player"]["credits"] += price
                if inv_item["quantity"] == 0:
                    game_state["inventory"].remove(inv_item)
                return {
                    "success": True,
                    "message": f"Sold {quantity} {item} for {price} credits",
                    "credits": game_state["player"]["credits"],
                }
        return {"success": False, "message": "Not enough items"}

    return {"success": False, "message": "Invalid trade action"}
