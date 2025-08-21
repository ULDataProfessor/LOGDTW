#!/usr/bin/env python3
"""
Flask Web Application for LOGDTW2002
A complete web interface for the space trading game with SQLite database
"""

import os
import sys
import json
import time
from copy import deepcopy
from datetime import datetime, timedelta
from flask import Flask, session, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy

# Add the parent directory to the path to import game modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Core game modules
    from game.player import Player as GamePlayer
    from game.world import World
    from game.save_system import SaveGameSystem, GameState

    # Combat systems
    from game.combat import CombatSystem
    from game.enhanced_combat import EnhancedCombatSystem

    # Trading and economy
    from game.trading import TradingSystem
    from game.dynamic_markets import DynamicMarketSystem
    from game.stock_market import StockMarket

    # Missions and quests
    from game.enhanced_missions import MissionManager
    from game.quests import QuestSystem

    # Procedural content
    from game.procedural_generator import ProceduralGenerator
    from game.world_generator import WorldGenerator
    from game.event_engine import EventEngine

    # Character progression
    from game.skills import SkillTree
    from game.achievements import AchievementSystem
    from game.crew import Crew

    # Game mechanics
    from game.fog_of_war import FogOfWarSystem
    from game.random_events import EventContext  # Only import what exists
    from game.ship_customization import ShipCustomization
    from game.crafting import craft_item, RECIPES  # Import functions instead of non-existent class
    from game.diplomacy import Diplomacy  # Correct class name
    from game.npcs import NPCSystem  # Correct class name
    from game.story_content import FactionStoryline  # Correct class name
    from game.holodeck import HolodeckSystem
    from game.ai_counselor import CounselorResponse  # Correct class name
    from game.sos_system import SOSSystem

    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import game modules: {e}")
    print("Running in basic mode without full game integration")
    GAME_MODULES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Database configuration
database_path = os.path.join(os.path.dirname(__file__), "logdtw2002.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_timeout": 20,
    "pool_recycle": -1,
    "pool_pre_ping": True,
}

# Import models after app configuration
from web.models import (
    db,
    init_database,
    get_or_create_player,
    cleanup_old_sessions,
    get_database_stats,
    User,
    Player,
    InventoryItem,
    SectorVisibility,
    EventHistory,
    MarketData,
    PlayerMission,
    GameSettings,
)

# Initialize database
init_database(app)

# Global game systems (initialized on first use)
game_systems = {
    "procedural_generator": None,
    "save_system": None,
    "dynamic_markets": None,
    "mission_manager": None,
    "skill_tree": None,
    "enhanced_combat": None,
}


def get_game_systems():
    """Initialize game systems on first use"""
    if not GAME_MODULES_AVAILABLE:
        return {}

    if game_systems["procedural_generator"] is None:
        game_systems["procedural_generator"] = ProceduralGenerator()
        game_systems["save_system"] = SaveGameSystem("web_saves")
        game_systems["dynamic_markets"] = DynamicMarketSystem()
        game_systems["mission_manager"] = MissionManager()
        game_systems["skill_tree"] = SkillTree()
        game_systems["enhanced_combat"] = EnhancedCombatSystem()
        # Empire system for web API
        try:
            from game.empire import EmpireSystem

            game_systems["empire"] = EmpireSystem()
        except Exception:
            game_systems["empire"] = None
        # Additional systems
        game_systems["stock_market"] = StockMarket()
        game_systems["counselor"] = AICounselor()
        game_systems["npc_manager"] = NPCManager() if "NPCManager" in globals() else None
        game_systems["crew_manager"] = CrewManager() if "CrewManager" in globals() else None
        game_systems["diplomacy"] = DiplomacySystem() if "DiplomacySystem" in globals() else None

    return game_systems


def get_session_id() -> str:
    """Get or create session ID"""
    if "session_id" not in session:
        session["session_id"] = f"web_{int(time.time())}_{os.urandom(8).hex()}"
    return session["session_id"]


def get_current_player() -> Player:
    """Get the current player from database"""
    session_id = get_session_id()
    return get_or_create_player(session_id)


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    email = str(data.get("email", "")).strip() or None
    if not username or not password:
        return jsonify(success=False, message="Username and password required"), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(success=False, message="User already exists"), 400
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    # Link current session player to this user
    player = get_current_player()
    player.user_id = user.id
    db.session.commit()
    return jsonify(success=True, user_id=user.id)


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify(success=False, message="Invalid credentials"), 401
    user.last_login = datetime.utcnow()
    db.session.commit()
    # Attach current session player to the user (merge progress)
    player = get_current_player()
    player.user_id = user.id
    db.session.commit()
    return jsonify(success=True, user_id=user.id)


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify(success=True)


def get_game_data() -> dict:
    """Get current game data formatted for legacy API compatibility"""
    player = get_current_player()

    # Get inventory items
    inventory_items = [item.to_dict() for item in player.inventory]

    # Get discovered sectors
    discovered_sectors = [
        v.sector_id
        for v in SectorVisibility.query.filter_by(player_id=player.id, discovered=True).all()
    ]

    # Get active missions
    active_missions = [
        mission.to_dict()
        for mission in PlayerMission.query.filter_by(player_id=player.id, status="active").all()
    ]

    # Format data for legacy compatibility
    return {
        "player": player.to_dict(),
        "world": {
            "current_location": player.current_location,
            "discovered_sectors": discovered_sectors,
            "turn_counter": player.turn_counter,
        },
        "inventory": inventory_items,
        "missions": active_missions,
        "skills": player.skills,
        "reputation": player.reputation,
    }


def update_fog_of_war(player: Player, new_sector: int = None):
    """Update fog of war for player's current position"""
    if not GAME_MODULES_AVAILABLE:
        return

    current_sector = new_sector or player.current_sector
    sensor_range = player.skills.get("Piloting", 1)  # Piloting affects sensor range

    # Get or create fog of war system
    fog_system = FogOfWarSystem(max_sectors=GameSettings.get_setting("max_sectors", 1000))

    # Load existing visibility data
    visibility_records = SectorVisibility.query.filter_by(player_id=player.id).all()
    for record in visibility_records:
        fog_system.sector_visibility[record.sector_id].discovered = record.discovered
        fog_system.sector_visibility[record.sector_id].visible = record.visible
        fog_system.sector_visibility[record.sector_id].visit_count = record.visit_count

    # Update visibility
    newly_visible = fog_system.update_visibility(current_sector, sensor_range)

    # Save updated visibility to database
    for sector_id in newly_visible:
        vis_record = SectorVisibility.query.filter_by(
            player_id=player.id, sector_id=sector_id
        ).first()

        if not vis_record:
            vis_record = SectorVisibility(
                player_id=player.id,
                sector_id=sector_id,
                discovered=True,
                visible=True,
                visit_count=1,
                last_visited=datetime.utcnow(),
            )
            db.session.add(vis_record)
        else:
            vis_record.discovered = True
            vis_record.visible = True
            vis_record.visit_count += 1
            vis_record.last_visited = datetime.utcnow()

    db.session.commit()


def check_random_events(player: Player, context: "EventContext") -> dict:
    """Check for random events and handle them"""
    if not GAME_MODULES_AVAILABLE:
        return None

    event_system = RandomEventSystem()

    # Build game state for event system
    game_state = {
        "player_level": player.level,
        "player_health": player.health,
        "current_sector": player.current_sector,
        "credits": player.credits,
        "reputation": player.reputation,
        "inventory": [item.to_dict() for item in player.inventory],
        "sector_danger": min(5, max(1, player.current_sector // 20 + 1)),
    }

    # Check for events
    triggered_event = event_system.check_for_events(context, game_state)

    if triggered_event:
        # Handle the event
        outcome = event_system.handle_event(triggered_event, game_state)

        # Save event to database
        event_record = EventHistory(
            player_id=player.id,
            event_id=triggered_event.event_id,
            event_type=triggered_event.event_type.value,
            event_context=triggered_event.context.value,
            sector_id=player.current_sector,
            turn_number=player.turn_counter,
            event_data={"triggered_event": triggered_event.name},
            outcome=outcome.__dict__,
        )
        db.session.add(event_record)

        # Apply effects to player
        if outcome.effects:
            if "health_damage" in outcome.effects:
                player.health = max(0, player.health - outcome.effects["health_damage"])
            if "fuel_loss" in outcome.effects:
                player.fuel = max(0, player.fuel - outcome.effects["fuel_loss"])
            if "credit_cost" in outcome.effects:
                player.credits = max(0, player.credits - outcome.effects["credit_cost"])

        if outcome.rewards:
            if "credits" in outcome.rewards:
                player.credits += outcome.rewards["credits"]
            if "experience" in outcome.rewards:
                player.add_experience(outcome.rewards["experience"])

        if outcome.penalties:
            if "health" in outcome.penalties:
                player.health = max(0, player.health - outcome.penalties["health"])
            if "credits" in outcome.penalties:
                player.credits = max(0, player.credits - outcome.penalties["credits"])
            if "fuel" in outcome.penalties:
                player.fuel = max(0, player.fuel - outcome.penalties["fuel"])

        db.session.commit()

        return {
            "event_triggered": True,
            "event_name": triggered_event.name,
            "event_description": triggered_event.description,
            "outcome": outcome.__dict__,
        }

    return None


@app.route("/")
def index():
    """Main game interface"""
    return render_template("index.html")


@app.route("/game")
def game():
    """Alternative game route"""
    return render_template("index.html")


# ============================================================================
# API Routes
@app.route("/api/stocks", methods=["GET", "POST"])
def api_stocks():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Stock market not available"), 501
    systems = get_game_systems()
    market = systems.get("stock_market")
    player = get_current_player()
    if request.method == "GET":
        # Update prices if needed
        market.update_market()
        stocks = [s.__dict__ for s in market.get_all_stocks()]
        portfolio = market.get_portfolio_summary()
        return jsonify(success=True, stocks=stocks, portfolio=portfolio)
    else:
        data = request.get_json() or {}
        action = str(data.get("action", "")).lower()
        symbol = data.get("symbol")
        shares = int(data.get("shares", 0))
        if action == "buy":
            res = market.buy_stock(player, symbol, shares)
        elif action == "sell":
            res = market.sell_stock(player, symbol, shares)
        else:
            return jsonify(success=False, message="Invalid action"), 400
        db.session.commit()
        return jsonify(res)


@app.route("/api/counselor/tip", methods=["GET"])
def api_counselor_tip():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Counselor not available"), 501
    systems = get_game_systems()
    counselor = systems.get("counselor")
    player = get_current_player()
    tip = (
        counselor.get_tip(
            {
                "level": player.level,
                "credits": player.credits,
                "sector": player.current_sector,
            }
        )
        if counselor
        else "Counselor unavailable"
    )
    return jsonify(success=True, tip=tip)


@app.route("/api/npc/list", methods=["GET"])
def api_npc_list():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="NPC system not available"), 501
    systems = get_game_systems()
    npc_manager = systems.get("npc_manager")
    if not npc_manager:
        return jsonify(success=False, message="NPC system not initialized"), 501
    # For web, list a few generic contacts
    contacts = npc_manager.get_contacts() if hasattr(npc_manager, "get_contacts") else []
    return jsonify(success=True, npcs=contacts)


@app.route("/api/npc/talk", methods=["POST"])
def api_npc_talk():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="NPC system not available"), 501
    systems = get_game_systems()
    npc_manager = systems.get("npc_manager")
    data = request.get_json() or {}
    target = data.get("name")
    if npc_manager and hasattr(npc_manager, "talk"):
        reply = npc_manager.talk(target)
    else:
        reply = f"{target} acknowledges your hail."
    return jsonify(success=True, reply=reply)


@app.route("/api/crew", methods=["GET"])
def api_crew():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Crew system not available"), 501
    systems = get_game_systems()
    crew_manager = systems.get("crew_manager")
    crew = crew_manager.list_crew() if crew_manager and hasattr(crew_manager, "list_crew") else []
    return jsonify(success=True, crew=crew)


@app.route("/api/diplomacy", methods=["GET"])
def api_diplomacy():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Diplomacy not available"), 501
    systems = get_game_systems()
    diplomacy = systems.get("diplomacy")
    status = diplomacy.get_status() if diplomacy and hasattr(diplomacy, "get_status") else {}
    return jsonify(success=True, diplomacy=status)


@app.route("/api/session", methods=["POST"])
def create_session():
    """Establish a session for the web client and return a token."""
    sid = get_session_id()
    try:
        cleanup_old_sessions(hours=24)
    except Exception:
        pass
    return jsonify(success=True, token=sid)


# ============================================================================


@app.route("/api/empire/capture", methods=["POST"])
def api_empire_capture():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Empire system not available"), 501
    systems = get_game_systems()
    empire = systems.get("empire")
    if not empire:
        return jsonify(success=False, message="Empire system not initialized"), 500
    # For web, capture where player is currently located
    player = get_current_player()

    # Create a lightweight world facade with required fields
    class _W:
        pass

    w = _W()
    w.current_sector = player.current_sector

    # Fake a location-like object
    class _L:
        pass

    loc = _L()
    loc.name = player.current_location or f"Sector {player.current_sector}"
    loc.location_type = "planet"

    def _get_current_location():
        return loc

    w.get_current_location = _get_current_location
    result = empire.capture_current_planet(player, w)
    return jsonify(success=result.get("success", False), message=result.get("message", ""))


@app.route("/api/empire/policy", methods=["POST"])
def api_empire_policy():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Empire system not available"), 501
    systems = get_game_systems()
    empire = systems.get("empire")
    data = request.get_json() or {}
    player = get_current_player()
    planet = data.get("planet") or (player.current_location or "")
    res = empire.set_policy(
        planet,
        player.current_sector,
        **{
            k: int(v)
            for k, v in data.items()
            if k in ["agriculture", "industry", "defense", "research", "tax"]
        },
    )
    return jsonify(success=res.get("success", False), message=res.get("message", ""))


@app.route("/api/empire/raise", methods=["POST"])
def api_empire_raise():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Empire system not available"), 501
    systems = get_game_systems()
    empire = systems.get("empire")
    data = request.get_json() or {}
    amount = int(data.get("amount", 0))
    player = get_current_player()
    planet = data.get("planet") or (player.current_location or "")
    res = empire.raise_soldiers(planet, player.current_sector, amount, player)
    return jsonify(success=res.get("success", False), message=res.get("message", ""))


@app.route("/api/empire/status", methods=["GET"])
def api_empire_status():
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Empire system not available"), 501
    systems = get_game_systems()
    empire = systems.get("empire")
    return jsonify(success=True, empire=empire.status() if empire else [])


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current game status"""
    try:
        player = get_current_player()

        # Update fog of war
        update_fog_of_war(player)

        # Check for random events (low probability in status check)
        event_result = None
        if GAME_MODULES_AVAILABLE:
            import random

            if random.random() < 0.01:  # 1% chance per status check
                event_result = check_random_events(player, EventContext.IN_SPACE)

        # Get inventory
        inventory_items = [item.to_dict() for item in player.inventory]

        # Get discovered sectors for fog of war
        discovered_sectors = [
            v.sector_id
            for v in SectorVisibility.query.filter_by(player_id=player.id, discovered=True).all()
        ]

        response = {
            "success": True,
            "player": player.to_dict(),
            "world": {
                "current_location": player.current_location,
                "discovered_sectors": discovered_sectors,
                "turn_counter": player.turn_counter,
            },
            "inventory": inventory_items,
            "skills": player.skills,
            "reputation": player.reputation,
        }

        if event_result:
            response["random_event"] = event_result

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "message": f"Error getting status: {str(e)}"}), 500


@app.route("/api/travel", methods=["POST"])
def travel():
    """Travel to a new sector"""
    player = get_current_player()
    json_data = request.get_json() or {}
    sector = int(json_data.get("sector", 0))

    if not (1 <= sector <= 1000):  # Expanded range for procedural sectors
        return jsonify(success=False, message="Invalid sector")

    if player.fuel < 10:
        return jsonify(success=False, message="Insufficient fuel")

    # Update player location
    player.current_sector = sector
    player.fuel -= 10
    player.turn_counter += 1

    # Update fog of war (this handles adding discovered sectors)
    update_fog_of_war(player, sector)

    # Check for random events during travel
    event_result = check_random_events(player, EventContext.TRAVEL)

    # Generate sector info if game modules available
    sector_info = {}
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        proc_gen = systems["procedural_generator"]
        sector_data = proc_gen.generate_galaxy_sector(sector)
        sector_info = {
            "name": sector_data.name,
            "faction": sector_data.faction_control,
            "danger_level": sector_data.danger_level,
            "planets": len(sector_data.planets),
            "stations": len(sector_data.stations),
        }

    # Save changes to database
    db.session.commit()

    response = {
        "success": True,
        "message": f"Jumped to Sector {sector}",
        "player": player.to_dict(),
        "sector_info": sector_info,
    }

    if event_result:
        response["random_event"] = event_result

    return jsonify(response)


@app.route("/api/trade", methods=["POST"])
def trade():
    """Execute a trade transaction"""
    player = get_current_player()
    json_data = request.get_json() or {}
    item = json_data.get("item")
    quantity = int(json_data.get("quantity", 0))
    action = json_data.get("trade_action")

    # Get dynamic prices if available
    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        markets = systems["dynamic_markets"]
        current_sector = player.current_sector

        # Initialize sector economy if needed
        if current_sector not in markets.sector_economies:
            markets.initialize_sector_economy(current_sector)

        market_prices = markets.get_sector_prices(current_sector)
    else:
        # Fallback static prices
        market_prices = {
            "Food": 50,
            "Iron": 100,
            "Electronics": 300,
            "Weapons": 800,
            "Medicine": 400,
            "Fuel": 75,
            "Tritium": 5000,
            "Dilithium": 8000,
            "Ammolite": 12000,
        }

    if item not in market_prices:
        return jsonify(success=False, message="Invalid item")

    price = market_prices[item] * quantity

    if action == "buy":
        if player.credits >= price:
            player.credits -= price

            # Add to inventory
            inventory_item = InventoryItem.query.filter_by(player_id=player.id, name=item).first()

            if inventory_item:
                inventory_item.quantity += quantity
            else:
                inventory_item = InventoryItem(
                    player_id=player.id,
                    name=item,
                    item_type="commodity",
                    quantity=quantity,
                    value=market_prices[item],
                )
                db.session.add(inventory_item)

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": f"Bought {quantity} {item} for {price} credits",
                    "credits": player.credits,
                    "inventory": [item.to_dict() for item in player.inventory],
                }
            )
        return jsonify(success=False, message="Insufficient credits")

    elif action == "sell":
        inventory_item = InventoryItem.query.filter_by(player_id=player.id, name=item).first()

        if inventory_item and inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
            player.credits += price

            if inventory_item.quantity <= 0:
                db.session.delete(inventory_item)

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": f"Sold {quantity} {item} for {price} credits",
                    "credits": player.credits,
                    "inventory": [item.to_dict() for item in player.inventory],
                }
            )
        return jsonify(success=False, message="Insufficient inventory")


@app.route("/api/market", methods=["GET"])
def get_market():
    """Get current market prices"""
    player = get_current_player()
    current_sector = player.current_sector

    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        markets = systems["dynamic_markets"]

        if current_sector not in markets.sector_economies:
            markets.initialize_sector_economy(current_sector)

        prices = markets.get_sector_prices(current_sector)
        economy_info = markets.sector_economies[current_sector]

        # Consistent notes schema: always a list of strings
        notes = []
        if current_sector == 1:
            notes.append(
                "Exclusive exports: Genesis Blueprint Fragment, Void Crystal, Ancient Data Shard, Prototype AI Core, Federation Seal (Rare)."
            )
        try:
            for ev in getattr(markets, "active_events", []):
                if getattr(ev, "sector_id", None) == current_sector and ev.description:
                    turns_left = max(0, ev.duration - (markets.current_turn - ev.start_turn))
                    notes.append(f"Rumor: {ev.description} (turns left {turns_left})")
        except Exception:
            pass

        return jsonify(
            {
                "success": True,
                "prices": prices,
                "economy": {
                    "wealth_level": economy_info.wealth_level,
                    "specializations": economy_info.specializations,
                    "market_condition": economy_info.market_condition.value,
                },
                "notes": notes,
            }
        )
    else:
        # Fallback static market
        prices = {
            "Food": 50,
            "Iron": 100,
            "Electronics": 300,
            "Weapons": 800,
            "Medicine": 400,
            "Fuel": 75,
        }
        return jsonify({"success": True, "prices": prices, "economy": {}})


@app.route("/api/combat", methods=["POST"])
def combat():
    """Handle combat encounters"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Combat system not available")

    player = get_current_player()
    json_data = request.get_json() or {}
    action = json_data.get("action", "scan")

    if action == "scan":
        # Scan for enemies
        danger_level = min(player.current_sector // 10 + 1, 5)
        enemy_chance = danger_level * 0.2

        import random

        if random.random() < enemy_chance:
            enemy_types = ["space_pirate", "alien_scout", "rogue_trader"]
            enemy = random.choice(enemy_types)
            return jsonify(
                {
                    "success": True,
                    "enemies_found": True,
                    "enemy_type": enemy,
                    "message": f"Warning: {enemy.replace('_', ' ').title()} detected!",
                }
            )
        else:
            return jsonify(
                {"success": True, "enemies_found": False, "message": "No hostile contacts detected"}
            )

    return jsonify(success=False, message="Unknown combat action")


@app.route("/api/missions", methods=["GET"])
def get_missions():
    """Get available missions"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=True, missions=[])

    player = get_current_player()
    data = get_game_data()  # Still needed for legacy mission system
    systems = get_game_systems()
    mission_manager = systems["mission_manager"]

    available_missions = mission_manager.get_available_missions(
        player.level, player.current_sector, data
    )

    # Convert missions to JSON-serializable format
    missions_data = []
    for mission in available_missions:
        missions_data.append(
            {
                "id": mission.id,
                "title": mission.title,
                "description": mission.description,
                "type": mission.type.value,
                "difficulty": mission.difficulty.value,
                "rewards": {
                    "credits": mission.rewards.credits,
                    "experience": mission.rewards.experience,
                    "items": mission.rewards.items,
                },
            }
        )

    return jsonify(success=True, missions=missions_data)


@app.route("/api/save", methods=["POST"])
def save_game():
    """Save the current game state"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Save system not available")

    try:
        json_data = request.get_json() or {}
        save_name = json_data.get("save_name", "web_save")

        # Validate save name
        if not save_name or not isinstance(save_name, str):
            return jsonify(success=False, message="Invalid save name"), 400

        player = get_current_player()
        if not player:
            return jsonify(success=False, message="No active player session"), 401

        data = get_game_data()
        systems = get_game_systems()
        save_system = systems["save_system"]

        # Create a GameState object
        game_state = GameState(
            player_data=player.to_dict(),
            world_data=data["world"],
            mission_data=data["missions"],
            npc_data={},
            trading_data={},
            skill_data=player.skills,
            combat_data={},
            settings={},
            statistics={"play_time": player.turn_counter * 60},
            achievements=[],
            timestamp=time.time(),
        )

        save_id = save_system.save_game(game_state, save_name, "Web save")

        if save_id:
            return jsonify(success=True, message=f"Game saved as {save_id}")
        else:
            return jsonify(success=False, message="Failed to save game")

    except Exception as e:
        app.logger.error(f"Error saving game: {str(e)}")
        return jsonify(success=False, message="Internal server error"), 500


@app.route("/api/load", methods=["POST"])
def load_game():
    """Load a saved game state"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Save system not available")

    json_data = request.get_json() or {}
    save_name = json_data.get("save_name", "web_save")

    systems = get_game_systems()
    save_system = systems["save_system"]

    game_state = save_system.load_game(save_name)

    if game_state:
        # Note: In a full implementation, this would update the database player
        # For now, just return success - the database is the source of truth
        return jsonify(success=True, message="Load not fully implemented in database mode")
    else:
        return jsonify(success=False, message="Failed to load game")


@app.route("/api/galaxy", methods=["GET"])
def get_galaxy():
    """Get galaxy map information"""
    player = get_current_player()

    # Get discovered sectors
    discovered_sectors = [
        v.sector_id
        for v in SectorVisibility.query.filter_by(player_id=player.id, discovered=True).all()
    ]

    galaxy_map = {
        "current_sector": player.current_sector,
        "discovered_sectors": discovered_sectors,
        "total_sectors": 1000,
        "sectors": {},
    }

    if GAME_MODULES_AVAILABLE:
        systems = get_game_systems()
        proc_gen = systems["procedural_generator"]

        # Add info for discovered sectors
        for sector_id in discovered_sectors:
            sector_data = proc_gen.generate_galaxy_sector(sector_id)
            galaxy_map["sectors"][sector_id] = {
                "name": sector_data.name,
                "faction": sector_data.faction_control,
                "danger_level": sector_data.danger_level,
                "coordinates": sector_data.coordinates,
                "planets": len(sector_data.planets),
                "stations": len(sector_data.stations),
                "events": len(sector_data.events),
                "resources": list(sector_data.resources.keys()),
                "narrative": {
                    "summary": getattr(sector_data, "narrative_summary", None),
                    "hooks": getattr(sector_data, "narrative_hooks", None),
                },
            }

    return jsonify(success=True, galaxy=galaxy_map)


@app.route("/api/sector/<int:sector_id>", methods=["GET"])
def get_sector_details(sector_id):
    """Get detailed information about a specific sector"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Sector generation not available")

    try:
        player = get_current_player()

        # Check if player has discovered this sector
        visibility = SectorVisibility.query.filter_by(
            player_id=player.id, sector_id=sector_id
        ).first()

        if not visibility or not visibility.discovered:
            return jsonify(success=False, message="Sector not yet discovered")

        systems = get_game_systems()
        proc_gen = systems["procedural_generator"]

        # Generate detailed sector information
        sector_data = proc_gen.generate_galaxy_sector(sector_id)

        # Format planet information
        planets_info = []
        for planet in sector_data.planets:
            planets_info.append(
                {
                    "name": planet.name,
                    "size": planet.size,
                    "biome": (
                        planet.biome.value if hasattr(planet.biome, "value") else str(planet.biome)
                    ),
                    "population": planet.population,
                    "tech_level": planet.tech_level,
                    "trade_goods": planet.trade_goods,
                    "faction_control": planet.faction_control,
                }
            )

        # Format station information
        stations_info = []
        for station in sector_data.stations:
            stations_info.append(
                {
                    "name": station.get("name", "Unknown Station"),
                    "type": station.get("type", "Trading Post"),
                    "services": station.get("services", ["Trade", "Repair", "Fuel"]),
                    "faction": station.get("faction", "Neutral"),
                }
            )

        # Format events
        events_info = []
        for event in sector_data.events:
            events_info.append(
                {
                    "type": event.get("type", "Unknown"),
                    "description": event.get(
                        "description", "Something interesting is happening here"
                    ),
                    "active": event.get("active", True),
                }
            )

        sector_details = {
            "id": sector_data.id,
            "name": sector_data.name,
            "coordinates": sector_data.coordinates,
            "faction_control": sector_data.faction_control,
            "danger_level": sector_data.danger_level,
            "planets": planets_info,
            "stations": stations_info,
            "events": events_info,
            "trade_routes": sector_data.trade_routes,
            "stellar_objects": sector_data.stellar_objects,
            "warp_gates": sector_data.warp_gates,
            "resources": sector_data.resources,
            "discovery_date": sector_data.discovery_date,
            "narrative": {
                "summary": getattr(sector_data, "narrative_summary", None),
                "hooks": getattr(sector_data, "narrative_hooks", None),
            },
        }

        return jsonify(success=True, sector=sector_details)

    except Exception as e:
        return jsonify(success=False, message=f"Error generating sector: {str(e)}")


@app.route("/api/sector/persistent/<int:sector_id>", methods=["GET"])
def api_sector_persistent(sector_id: int):
    """Expose DB-backed persistent sector record (id, flags, connections)."""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="World not available"), 501
    try:
        w = World()
        rec = w.get_or_create_sector(sector_id)
        return jsonify(success=True, sector=rec)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/sector/discovery/<int:sector_id>", methods=["POST"])
def api_sector_discovery(sector_id: int):
    """Mark sector explored/charted for the current player and global DB."""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="World not available"), 501
    data = request.get_json() or {}
    explored = bool(data.get("explored", True))
    charted = bool(data.get("charted", False))
    try:
        player = get_current_player()
        if explored:
            v = SectorVisibility.query.filter_by(player_id=player.id, sector_id=sector_id).first()
            if not v:
                v = SectorVisibility(player_id=player.id, sector_id=sector_id, discovered=True)
                db.session.add(v)
            else:
                v.discovered = True
            db.session.commit()
        # Global persistent flags
        w = World()
        if explored:
            w.mark_sector_explored(sector_id)
        if charted:
            w.mark_sector_charted(sector_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/sector/connections/<int:sector_id>", methods=["GET"])
def api_sector_connections(sector_id: int):
    """Lightweight neighbor list for galaxy sidebar."""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="World not available"), 501
    try:
        w = World()
        rec = w.get_or_create_sector(sector_id)
        neighbors = rec.get("connections", [])
        return jsonify(success=True, sector=sector_id, connections=neighbors)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
@app.route("/api/scan_sector", methods=["POST"])
def scan_current_sector():
    """Perform a detailed scan of the current sector"""
    if not GAME_MODULES_AVAILABLE:
        return jsonify(success=False, message="Scanning not available")

    try:
        player = get_current_player()
        current_sector = player.current_sector

        # Update fog of war
        update_fog_of_war(player, current_sector)

        # Get detailed sector information
        systems = get_game_systems()
        proc_gen = systems["procedural_generator"]
        sector_data = proc_gen.generate_galaxy_sector(current_sector)

        # Perform scan based on player's piloting skill
        piloting_skill = player.skills.get("Piloting", 1)
        scan_quality = min(piloting_skill * 20, 100)  # 20% per skill level, max 100%

        scan_results = {
            "sector_id": current_sector,
            "scan_quality": scan_quality,
            "basic_info": {
                "name": sector_data.name,
                "faction": sector_data.faction_control,
                "danger_level": sector_data.danger_level,
            },
        }

        # Add more details based on scan quality
        if scan_quality >= 20:
            scan_results["planets_detected"] = len(sector_data.planets)
            scan_results["stations_detected"] = len(sector_data.stations)

        if scan_quality >= 40:
            scan_results["stellar_objects"] = sector_data.stellar_objects[:3]  # Show first 3
            scan_results["resources_detected"] = list(sector_data.resources.keys())[:2]

        if scan_quality >= 60:
            scan_results["trade_routes"] = sector_data.trade_routes
            scan_results["warp_gates"] = sector_data.warp_gates

        if scan_quality >= 80:
            scan_results["events_detected"] = len(
                [e for e in sector_data.events if e.get("active", True)]
            )
            scan_results["detailed_resources"] = sector_data.resources

        # Check for random events during scanning
        event_result = check_random_events(player, EventContext.IN_SPACE)
        if event_result:
            scan_results["random_event"] = event_result

        return jsonify(success=True, scan_results=scan_results)

    except Exception as e:
        return jsonify(success=False, message=f"Scan failed: {str(e)}")


# ============================================================================
# Static file serving
# ============================================================================


@app.route("/css/<path:filename>")
def css_files(filename):
    """Serve CSS files"""
    return send_from_directory("css", filename)


@app.route("/js/<path:filename>")
def js_files(filename):
    """Serve JavaScript files"""
    return send_from_directory("js", filename)


# PWA assets
@app.route("/manifest.json")
def manifest_json():
    return send_from_directory(".", "manifest.json")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(".", "service-worker.js")


@app.route("/icons/<path:filename>")
def icons(filename):
    return send_from_directory("icons", filename)


# ============================================================================
# Error handlers
# ============================================================================


@app.errorhandler(404)
def not_found(error):
    return jsonify(success=False, message="Endpoint not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify(success=False, message="Internal server error"), 500


# ============================================================================
# Development utilities
# ============================================================================


@app.route("/api/debug/reset")
def debug_reset():
    """Reset game state (development only)"""
    if app.debug:
        session.clear()
        return jsonify(success=True, message="Game state reset")
    return jsonify(success=False, message="Debug endpoint not available"), 403


@app.route("/api/debug/info")
def debug_info():
    """Get debug information"""
    if app.debug:
        return jsonify(
            {
                "success": True,
                "game_modules_available": GAME_MODULES_AVAILABLE,
                "session_keys": list(session.keys()),
                "game_systems_initialized": any(v is not None for v in game_systems.values()),
            }
        )
    return jsonify(success=False, message="Debug endpoint not available"), 403


if __name__ == "__main__":
    import time
    import random
    
    # Use proper configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    from web.config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)

    print("🚀 Starting LOGDTW2002 Flask Web Server")
    print("=" * 40)
    print(f"Environment: {config_name}")
    print(f"Debug mode: {app.config.get('DEBUG', False)}")
    print(f"Game modules available: {GAME_MODULES_AVAILABLE}")
    print("Web interface: http://localhost:5002")
    print("API endpoints: http://localhost:5002/api/")
    print("=" * 40)

    app.run(debug=True, host="0.0.0.0", port=5002)
