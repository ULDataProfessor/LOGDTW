from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import uuid
from typing import Dict, List

from game.player import Player, Item
from game.world import World
from game.trading import TradingSystem

app = FastAPI()

# In-memory session store
sessions: Dict[str, Dict] = {}


class TravelRequest(BaseModel):
    sector: int


class TradeRequest(BaseModel):
    item: str
    quantity: int
    trade_action: str  # "buy" or "sell"


def get_session(x_token: str = Header(...)):
    session = sessions.get(x_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session


def serialize_item(item: Item) -> Dict:
    return {
        "name": item.name,
        "quantity": item.quantity,
        "description": item.description,
        "value": item.value,
        "item_type": item.item_type,
    }


def serialize_player(player: Player) -> Dict:
    return {
        "name": player.name,
        "ship_name": player.ship_name,
        "level": player.level,
        "credits": player.credits,
        "health": player.health,
        "max_health": player.max_health,
        "energy": player.energy,
        "max_energy": player.max_energy,
        "fuel": player.fuel,
        "max_fuel": player.max_fuel,
        "inventory": [serialize_item(i) for i in player.inventory],
        "skills": {k: v.level for k, v in player.skills.items()},
    }


def serialize_world(world: World) -> Dict:
    return {
        "current_location": world.current_location,
        "current_sector": world.current_sector,
        "discovered_sectors": list(world.discovered_sectors),
        "turn_counter": getattr(world, "turn_counter", 0),
    }


@app.post("/api/session")
def create_session():
    token = str(uuid.uuid4())
    player = Player()
    world = World()
    trading = TradingSystem()
    sessions[token] = {"player": player, "world": world, "trading": trading}
    return {"token": token}


@app.get("/api/status")
def get_status(session: Dict = Depends(get_session)):
    player = session["player"]
    world = session["world"]
    return {
        "success": True,
        "player": serialize_player(player),
        "world": serialize_world(world),
    }


@app.post("/api/travel")
def travel(req: TravelRequest, session: Dict = Depends(get_session)):
    player = session["player"]
    world = session["world"]
    result = world.jump_to_sector(req.sector, player)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    # Complete the jump immediately
    world._complete_jump(player)  # type: ignore
    return {
        "success": True,
        "message": result.get("message", "Jump complete"),
        "player": serialize_player(player),
        "world": serialize_world(world),
    }


@app.post("/api/trade")
def trade(req: TradeRequest, session: Dict = Depends(get_session)):
    player = session["player"]
    world = session["world"]
    trading = session["trading"]
    location = world.current_location
    if req.trade_action == "buy":
        result = trading.buy_item(player, location, req.item, req.quantity)
    else:
        result = trading.sell_item(player, location, req.item, req.quantity)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return {
        "success": True,
        "message": result.get("message"),
        "player": serialize_player(player),
    }
