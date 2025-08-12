#!/usr/bin/env python3
"""
Database Models for LOGDTW2002 Flask Web Application
SQLite3-based models with SQLAlchemy ORM
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """Application user for web and CLI shared login"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    players = relationship('Player', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

class Player(db.Model):
    """Player character model"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False, default='Captain')
    ship_name = Column(String(100), nullable=False, default='Starfarer')
    
    # Core stats
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    credits = Column(Integer, default=1000)
    
    # Health and resources
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    energy = Column(Integer, default=100)
    max_energy = Column(Integer, default=100)
    fuel = Column(Integer, default=100)
    max_fuel = Column(Integer, default=100)
    
    # Location
    current_sector = Column(Integer, default=1)
    current_location = Column(String(100), default='Alpha Station')
    
    # Game state
    turn_counter = Column(Integer, default=0)
    play_time = Column(Float, default=0.0)  # In seconds
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # JSON fields for complex data
    reputation_json = Column(Text, default='{}')  # Faction reputations
    skills_json = Column(Text, default='{}')  # Skill levels
    ship_data_json = Column(Text, default='{}')  # Ship configuration
    
    # Relationships
    inventory = relationship('InventoryItem', back_populates='player', cascade='all, delete-orphan')
    sector_visibility = relationship('SectorVisibility', back_populates='player', cascade='all, delete-orphan')
    event_history = relationship('EventHistory', back_populates='player', cascade='all, delete-orphan')
    missions = relationship('PlayerMission', back_populates='player', cascade='all, delete-orphan')

    # Relationship to User
    user = relationship('User', back_populates='players')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, session_id: str, **kwargs):
        self.session_id = session_id
        self.name = kwargs.get('name', 'Captain')
        self.ship_name = kwargs.get('ship_name', 'Starfarer')
        
        # Initialize default JSON data
        self.reputation_json = json.dumps({
            'Federation': 0,
            'Empire': 0,
            'Pirates': 0,
            'Traders': 0
        })
        
        self.skills_json = json.dumps({
            'Combat': 1,
            'Piloting': 1,
            'Trading': 1,
            'Engineering': 1
        })
        
        self.ship_data_json = json.dumps({
            'hull_integrity': 100,
            'shield_power': 100,
            'weapon_slots': 2,
            'cargo_capacity': 50
        })
    
    @property
    def reputation(self) -> Dict[str, int]:
        """Get reputation as dict"""
        try:
            return json.loads(self.reputation_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {'Federation': 0, 'Empire': 0, 'Pirates': 0, 'Traders': 0}
    
    @reputation.setter
    def reputation(self, value: Dict[str, int]):
        """Set reputation from dict"""
        self.reputation_json = json.dumps(value)
    
    @property
    def skills(self) -> Dict[str, int]:
        """Get skills as dict"""
        try:
            return json.loads(self.skills_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {'Combat': 1, 'Piloting': 1, 'Trading': 1, 'Engineering': 1}
    
    @skills.setter
    def skills(self, value: Dict[str, int]):
        """Set skills from dict"""
        self.skills_json = json.dumps(value)
    
    @property
    def ship_data(self) -> Dict[str, Any]:
        """Get ship data as dict"""
        try:
            return json.loads(self.ship_data_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {'hull_integrity': 100, 'shield_power': 100, 'weapon_slots': 2, 'cargo_capacity': 50}
    
    @ship_data.setter
    def ship_data(self, value: Dict[str, Any]):
        """Set ship data from dict"""
        self.ship_data_json = json.dumps(value)
    
    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active = datetime.utcnow()
    
    def add_experience(self, amount: int):
        """Add experience and handle level ups"""
        self.experience += amount
        
        # Simple level calculation
        new_level = max(1, int((self.experience / 100) ** 0.5) + 1)
        if new_level > self.level:
            self.level = new_level
            # Level up bonuses
            self.max_health += 10
            self.max_energy += 5
            self.max_fuel += 5
            self.health = self.max_health  # Full heal on level up
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'ship_name': self.ship_name,
            'level': self.level,
            'experience': self.experience,
            'credits': self.credits,
            'health': self.health,
            'max_health': self.max_health,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'fuel': self.fuel,
            'max_fuel': self.max_fuel,
            'current_sector': self.current_sector,
            'current_location': self.current_location,
            'turn_counter': self.turn_counter,
            'reputation': self.reputation,
            'skills': self.skills,
            'ship_data': self.ship_data,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class InventoryItem(db.Model):
    """Player inventory items"""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    item_type = Column(String(50), nullable=False)  # weapon, commodity, equipment, etc.
    quantity = Column(Integer, default=1)
    value = Column(Integer, default=0)
    
    # Item properties as JSON
    properties_json = Column(Text, default='{}')
    
    # Relationships
    player = relationship('Player', back_populates='inventory')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def properties(self) -> Dict[str, Any]:
        """Get item properties as dict"""
        try:
            return json.loads(self.properties_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @properties.setter
    def properties(self, value: Dict[str, Any]):
        """Set item properties from dict"""
        self.properties_json = json.dumps(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'item_type': self.item_type,
            'quantity': self.quantity,
            'value': self.value,
            'properties': self.properties
        }

class SectorVisibility(db.Model):
    """Fog of war - sector visibility tracking"""
    __tablename__ = 'sector_visibility'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    sector_id = Column(Integer, nullable=False)
    
    discovered = Column(Boolean, default=False)
    visible = Column(Boolean, default=False)
    last_visited = Column(DateTime)
    visit_count = Column(Integer, default=0)
    
    # Relationships
    player = relationship('Player', back_populates='sector_visibility')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sector_id': self.sector_id,
            'discovered': self.discovered,
            'visible': self.visible,
            'last_visited': self.last_visited.isoformat() if self.last_visited else None,
            'visit_count': self.visit_count
        }

class EventHistory(db.Model):
    """Random event history tracking"""
    __tablename__ = 'event_history'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    
    event_id = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_context = Column(String(50), nullable=False)
    
    sector_id = Column(Integer)
    turn_number = Column(Integer)
    
    # Event data and outcome
    event_data_json = Column(Text, default='{}')
    outcome_json = Column(Text, default='{}')
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship('Player', back_populates='event_history')
    
    @property
    def event_data(self) -> Dict[str, Any]:
        try:
            return json.loads(self.event_data_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @event_data.setter
    def event_data(self, value: Dict[str, Any]):
        self.event_data_json = json.dumps(value)
    
    @property
    def outcome(self) -> Dict[str, Any]:
        try:
            return json.loads(self.outcome_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @outcome.setter
    def outcome(self, value: Dict[str, Any]):
        self.outcome_json = json.dumps(value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'event_id': self.event_id,
            'event_type': self.event_type,
            'event_context': self.event_context,
            'sector_id': self.sector_id,
            'turn_number': self.turn_number,
            'event_data': self.event_data,
            'outcome': self.outcome,
            'timestamp': self.timestamp.isoformat()
        }

class MarketData(db.Model):
    """Market prices and economic data"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    sector_id = Column(Integer, nullable=False)
    commodity = Column(String(100), nullable=False)
    
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    supply = Column(Integer, default=100)
    demand = Column(Integer, default=100)
    
    # Market modifiers
    market_condition = Column(String(50), default='normal')  # boom, crash, normal
    specialization_bonus = Column(Float, default=1.0)
    
    last_update = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sector_id': self.sector_id,
            'commodity': self.commodity,
            'base_price': self.base_price,
            'current_price': self.current_price,
            'supply': self.supply,
            'demand': self.demand,
            'market_condition': self.market_condition,
            'specialization_bonus': self.specialization_bonus,
            'last_update': self.last_update.isoformat()
        }

class PlayerMission(db.Model):
    """Player missions and quests"""
    __tablename__ = 'player_missions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    
    mission_id = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    mission_type = Column(String(50), nullable=False)
    
    status = Column(String(50), default='active')  # active, completed, failed, abandoned
    progress = Column(Integer, default=0)
    max_progress = Column(Integer, default=100)
    
    # Mission data
    mission_data_json = Column(Text, default='{}')
    rewards_json = Column(Text, default='{}')
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    player = relationship('Player', back_populates='missions')
    
    @property
    def mission_data(self) -> Dict[str, Any]:
        try:
            return json.loads(self.mission_data_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @mission_data.setter
    def mission_data(self, value: Dict[str, Any]):
        self.mission_data_json = json.dumps(value)
    
    @property
    def rewards(self) -> Dict[str, Any]:
        try:
            return json.loads(self.rewards_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @rewards.setter
    def rewards(self, value: Dict[str, Any]):
        self.rewards_json = json.dumps(value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'title': self.title,
            'description': self.description,
            'mission_type': self.mission_type,
            'status': self.status,
            'progress': self.progress,
            'max_progress': self.max_progress,
            'mission_data': self.mission_data,
            'rewards': self.rewards,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class GameSettings(db.Model):
    """Global game settings and configuration"""
    __tablename__ = 'game_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key: str, default=None):
        """Get a setting value"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            try:
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                return setting.value
        return default
    
    @classmethod
    def set_setting(cls, key: str, value: Any, description: str = None):
        """Set a setting value"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key)
            db.session.add(setting)
        
        if isinstance(value, (dict, list)):
            setting.value = json.dumps(value)
        else:
            setting.value = str(value)
        
        if description:
            setting.description = description
        
        db.session.commit()

# Database utility functions
def init_database(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()

        # Ensure user_id column exists on players for existing DBs
        try:
            info = db.engine.execute("PRAGMA table_info(players)").fetchall()
            cols = {row[1] for row in info}
            if 'user_id' not in cols:
                db.engine.execute("ALTER TABLE players ADD COLUMN user_id INTEGER REFERENCES users(id)")
        except Exception as e:
            print(f"Warning: could not ensure user_id column: {e}")
        
        # Initialize default settings
        default_settings = [
            ('max_sectors', 1000, 'Maximum number of galaxy sectors'),
            ('base_commodities', [
                'Food', 'Iron', 'Electronics', 'Weapons', 'Medicine', 'Fuel',
                'Tritium', 'Dilithium', 'Ammolite', 'Rare Metals'
            ], 'Base tradeable commodities'),
            ('global_event_rate', 0.1, 'Global random event probability'),
            ('server_version', '1.0.0', 'Server version'),
            ('maintenance_mode', False, 'Maintenance mode toggle')
        ]
        
        for key, value, description in default_settings:
            if not GameSettings.query.filter_by(key=key).first():
                GameSettings.set_setting(key, value, description)
        
        print("✅ Database initialized successfully")

def get_or_create_player(session_id: str) -> Player:
    """Get existing player or create new one"""
    player = Player.query.filter_by(session_id=session_id).first()
    
    if not player:
        player = Player(session_id=session_id)
        db.session.add(player)
        
        # Add starting inventory
        starting_items = [
            ('Food', 'commodity', 10, 50),
            ('Laser Pistol', 'weapon', 1, 200),
            ('Basic Scanner', 'equipment', 1, 100)
        ]
        
        for name, item_type, quantity, value in starting_items:
            item = InventoryItem(
                player=player,
                name=name,
                item_type=item_type,
                quantity=quantity,
                value=value
            )
            db.session.add(item)
        
        db.session.commit()
        print(f"✅ Created new player: {player.name} ({session_id})")
    
    player.update_last_active()
    db.session.commit()
    
    return player

def cleanup_old_sessions(hours: int = 24):
    """Clean up old inactive player sessions"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    old_players = Player.query.filter(
        Player.last_active < cutoff_time
    ).all()
    
    for player in old_players:
        db.session.delete(player)
    
    if old_players:
        db.session.commit()
        print(f"🧹 Cleaned up {len(old_players)} old player sessions")

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    return {
        'total_players': Player.query.count(),
        'active_players_24h': Player.query.filter(
            Player.last_active >= datetime.utcnow() - timedelta(hours=24)
        ).count(),
        'total_events': EventHistory.query.count(),
        'total_missions': PlayerMission.query.count(),
        'database_size': db.engine.execute("PRAGMA page_count").scalar() * db.engine.execute("PRAGMA page_size").scalar(),
    }
