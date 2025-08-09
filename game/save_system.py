#!/usr/bin/env python3
"""
Enhanced Save Game System for LOGDTW2002
Persistent progress with compressed saves, multiple save slots, and auto-save functionality
"""

import json
import pickle
import gzip
import os
import time
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import base64

@dataclass
class SaveMetadata:
    """Metadata for a save file"""
    save_id: str
    player_name: str
    ship_name: str
    player_level: int
    current_sector: int
    credits: int
    play_time: int  # in seconds
    game_version: str
    save_date: str
    file_size: int
    checksum: str
    description: str = ""
    screenshot: Optional[str] = None  # Base64 encoded image

@dataclass
class GameState:
    """Complete game state for saving/loading"""
    player_data: Dict
    world_data: Dict
    mission_data: Dict
    npc_data: Dict
    trading_data: Dict
    skill_data: Dict
    combat_data: Dict
    settings: Dict
    statistics: Dict
    achievements: List[str]
    timestamp: float

class SaveGameSystem:
    """Manages game saves with multiple slots and compression"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self.last_auto_save = 0
        self.max_auto_saves = 5
        
        # Backup settings
        self.backup_enabled = True
        self.max_backups = 10
        
        # Compression settings
        self.compression_level = 6
        self.use_compression = True
        
        # File paths
        self.metadata_file = self.save_directory / "save_metadata.json"
        self.settings_file = self.save_directory / "settings.json"
        
        # Load existing metadata
        self.save_metadata = self._load_metadata()
        
        # Game version for compatibility
        self.game_version = "1.0.0"
    
    def _load_metadata(self) -> Dict[str, SaveMetadata]:
        """Load save file metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    return {
                        save_id: SaveMetadata(**save_data) 
                        for save_id, save_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading save metadata: {e}")
        
        return {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            data = {
                save_id: asdict(metadata) 
                for save_id, metadata in self.save_metadata.items()
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def _generate_save_id(self, player_name: str) -> str:
        """Generate unique save ID"""
        timestamp = str(int(time.time()))
        player_hash = hashlib.md5(player_name.encode()).hexdigest()[:8]
        return f"{player_name.lower().replace(' ', '_')}_{player_hash}_{timestamp}"
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for save data integrity"""
        return hashlib.sha256(data).hexdigest()
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress save data"""
        if self.use_compression:
            return gzip.compress(data, compresslevel=self.compression_level)
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress save data"""
        if self.use_compression:
            try:
                return gzip.decompress(data)
            except gzip.BadGzipFile:
                # Data might not be compressed (old save format)
                return data
        return data
    
    def save_game(self, game_state: GameState, save_name: str = None, 
                  description: str = "", overwrite: bool = False) -> str:
        """Save the current game state"""
        
        # Generate save ID if not provided
        player_name = game_state.player_data.get('name', 'Unknown')
        if save_name:
            save_id = save_name
        else:
            save_id = self._generate_save_id(player_name)
        
        # Check if save already exists
        if save_id in self.save_metadata and not overwrite:
            # Create backup
            if self.backup_enabled:
                self._create_backup(save_id)
        
        try:
            # Serialize game state
            save_data = pickle.dumps(game_state)
            
            # Compress data
            compressed_data = self._compress_data(save_data)
            
            # Calculate checksum
            checksum = self._calculate_checksum(compressed_data)
            
            # Write save file
            save_file = self.save_directory / f"{save_id}.sav"
            with open(save_file, 'wb') as f:
                f.write(compressed_data)
            
            # Create metadata
            metadata = SaveMetadata(
                save_id=save_id,
                player_name=player_name,
                ship_name=game_state.player_data.get('ship_name', 'Unknown Ship'),
                player_level=game_state.player_data.get('level', 1),
                current_sector=game_state.world_data.get('current_sector', 1),
                credits=game_state.player_data.get('credits', 0),
                play_time=game_state.statistics.get('play_time', 0),
                game_version=self.game_version,
                save_date=datetime.now().isoformat(),
                file_size=len(compressed_data),
                checksum=checksum,
                description=description
            )
            
            # Store metadata
            self.save_metadata[save_id] = metadata
            self._save_metadata()
            
            print(f"✅ Game saved successfully as '{save_id}'")
            return save_id
            
        except Exception as e:
            print(f"❌ Error saving game: {e}")
            return None
    
    def load_game(self, save_id: str) -> Optional[GameState]:
        """Load a game state from save file"""
        
        if save_id not in self.save_metadata:
            print(f"❌ Save '{save_id}' not found")
            return None
        
        save_file = self.save_directory / f"{save_id}.sav"
        if not save_file.exists():
            print(f"❌ Save file not found: {save_file}")
            return None
        
        try:
            # Read save file
            with open(save_file, 'rb') as f:
                compressed_data = f.read()
            
            # Verify checksum
            metadata = self.save_metadata[save_id]
            if self._calculate_checksum(compressed_data) != metadata.checksum:
                print(f"⚠️ Warning: Save file checksum mismatch for '{save_id}'")
                if not self._confirm_load_corrupted():
                    return None
            
            # Decompress data
            save_data = self._decompress_data(compressed_data)
            
            # Deserialize game state
            game_state = pickle.loads(save_data)
            
            # Version compatibility check
            if hasattr(game_state, 'game_version'):
                if game_state.game_version != self.game_version:
                    print(f"⚠️ Loading save from different game version: {game_state.game_version}")
                    game_state = self._migrate_save_data(game_state)
            
            print(f"✅ Game loaded successfully: '{save_id}'")
            return game_state
            
        except Exception as e:
            print(f"❌ Error loading game: {e}")
            return None
    
    def _confirm_load_corrupted(self) -> bool:
        """Ask user if they want to load potentially corrupted save"""
        # In a real implementation, this would show a dialog
        # For now, just return True to allow loading
        return True
    
    def _migrate_save_data(self, game_state: GameState) -> GameState:
        """Migrate save data from older versions"""
        # Handle version compatibility issues
        
        # Add missing fields with defaults
        if not hasattr(game_state, 'achievements'):
            game_state.achievements = []
        
        if not hasattr(game_state, 'statistics'):
            game_state.statistics = {}
        
        # Update game state fields as needed
        return game_state
    
    def auto_save(self, game_state: GameState) -> bool:
        """Perform auto-save if enough time has passed"""
        if not self.auto_save_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_auto_save < self.auto_save_interval:
            return False
        
        # Create auto-save
        auto_save_id = f"autosave_{int(current_time)}"
        result = self.save_game(game_state, auto_save_id, "Auto-save", overwrite=True)
        
        if result:
            self.last_auto_save = current_time
            self._cleanup_old_auto_saves()
            return True
        
        return False
    
    def _cleanup_old_auto_saves(self):
        """Remove old auto-saves to keep only the most recent ones"""
        auto_saves = [
            (save_id, metadata) for save_id, metadata in self.save_metadata.items()
            if save_id.startswith("autosave_")
        ]
        
        # Sort by save date
        auto_saves.sort(key=lambda x: x[1].save_date, reverse=True)
        
        # Remove old auto-saves
        for save_id, metadata in auto_saves[self.max_auto_saves:]:
            self.delete_save(save_id)
    
    def _create_backup(self, save_id: str):
        """Create a backup of existing save"""
        if save_id not in self.save_metadata:
            return
        
        original_file = self.save_directory / f"{save_id}.sav"
        if not original_file.exists():
            return
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{save_id}_backup_{timestamp}"
        backup_file = self.save_directory / f"{backup_id}.sav"
        
        # Copy file
        with open(original_file, 'rb') as src, open(backup_file, 'wb') as dst:
            dst.write(src.read())
        
        # Create backup metadata
        original_metadata = self.save_metadata[save_id]
        backup_metadata = SaveMetadata(
            save_id=backup_id,
            player_name=original_metadata.player_name,
            ship_name=original_metadata.ship_name,
            player_level=original_metadata.player_level,
            current_sector=original_metadata.current_sector,
            credits=original_metadata.credits,
            play_time=original_metadata.play_time,
            game_version=original_metadata.game_version,
            save_date=datetime.now().isoformat(),
            file_size=original_metadata.file_size,
            checksum=original_metadata.checksum,
            description=f"Backup of {save_id}"
        )
        
        self.save_metadata[backup_id] = backup_metadata
        
        # Cleanup old backups
        self._cleanup_old_backups(save_id)
    
    def _cleanup_old_backups(self, save_id: str):
        """Remove old backups for a specific save"""
        backups = [
            (backup_id, metadata) for backup_id, metadata in self.save_metadata.items()
            if backup_id.startswith(f"{save_id}_backup_")
        ]
        
        # Sort by save date
        backups.sort(key=lambda x: x[1].save_date, reverse=True)
        
        # Remove old backups
        for backup_id, metadata in backups[self.max_backups:]:
            self.delete_save(backup_id)
    
    def delete_save(self, save_id: str) -> bool:
        """Delete a save file"""
        if save_id not in self.save_metadata:
            return False
        
        try:
            # Remove save file
            save_file = self.save_directory / f"{save_id}.sav"
            if save_file.exists():
                save_file.unlink()
            
            # Remove metadata
            del self.save_metadata[save_id]
            self._save_metadata()
            
            print(f"✅ Save '{save_id}' deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False
    
    def get_save_list(self, include_backups: bool = False) -> List[SaveMetadata]:
        """Get list of available saves"""
        saves = []
        
        for save_id, metadata in self.save_metadata.items():
            # Skip auto-saves and backups unless requested
            if save_id.startswith("autosave_") and not include_backups:
                continue
            if "_backup_" in save_id and not include_backups:
                continue
            
            saves.append(metadata)
        
        # Sort by save date (newest first)
        saves.sort(key=lambda x: x.save_date, reverse=True)
        return saves
    
    def get_save_info(self, save_id: str) -> Optional[SaveMetadata]:
        """Get detailed information about a specific save"""
        return self.save_metadata.get(save_id)
    
    def export_save(self, save_id: str, export_path: str) -> bool:
        """Export a save file to external location"""
        if save_id not in self.save_metadata:
            return False
        
        try:
            source_file = self.save_directory / f"{save_id}.sav"
            export_file = Path(export_path)
            
            # Copy save file
            with open(source_file, 'rb') as src, open(export_file, 'wb') as dst:
                dst.write(src.read())
            
            # Create metadata file
            metadata_export = export_file.with_suffix('.json')
            with open(metadata_export, 'w') as f:
                json.dump(asdict(self.save_metadata[save_id]), f, indent=2)
            
            print(f"✅ Save exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting save: {e}")
            return False
    
    def import_save(self, import_path: str, new_save_id: str = None) -> bool:
        """Import a save file from external location"""
        try:
            import_file = Path(import_path)
            metadata_file = import_file.with_suffix('.json')
            
            # Load metadata
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                    metadata = SaveMetadata(**metadata_data)
            else:
                # Create basic metadata if not available
                metadata = SaveMetadata(
                    save_id=new_save_id or f"imported_{int(time.time())}",
                    player_name="Imported",
                    ship_name="Unknown",
                    player_level=1,
                    current_sector=1,
                    credits=0,
                    play_time=0,
                    game_version=self.game_version,
                    save_date=datetime.now().isoformat(),
                    file_size=import_file.stat().st_size,
                    checksum="",
                    description="Imported save"
                )
            
            # Use new save ID if provided
            if new_save_id:
                metadata.save_id = new_save_id
            
            # Copy save file
            destination_file = self.save_directory / f"{metadata.save_id}.sav"
            with open(import_file, 'rb') as src, open(destination_file, 'wb') as dst:
                data = src.read()
                dst.write(data)
                
                # Update checksum
                metadata.checksum = self._calculate_checksum(data)
                metadata.file_size = len(data)
            
            # Add to metadata
            self.save_metadata[metadata.save_id] = metadata
            self._save_metadata()
            
            print(f"✅ Save imported as '{metadata.save_id}'")
            return True
            
        except Exception as e:
            print(f"❌ Error importing save: {e}")
            return False
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """Get statistics about save files"""
        saves = list(self.save_metadata.values())
        
        if not saves:
            return {"total_saves": 0}
        
        total_size = sum(save.file_size for save in saves)
        avg_play_time = sum(save.play_time for save in saves) / len(saves)
        
        return {
            "total_saves": len(saves),
            "total_size_mb": total_size / (1024 * 1024),
            "average_play_time": avg_play_time,
            "oldest_save": min(saves, key=lambda x: x.save_date).save_date,
            "newest_save": max(saves, key=lambda x: x.save_date).save_date,
            "auto_saves": len([s for s in saves if s.save_id.startswith("autosave_")]),
            "backups": len([s for s in saves if "_backup_" in s.save_id])
        }
    
    def cleanup_saves(self, max_age_days: int = 30) -> int:
        """Clean up old saves beyond specified age"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        saves_to_delete = []
        for save_id, metadata in self.save_metadata.items():
            save_time = datetime.fromisoformat(metadata.save_date).timestamp()
            if save_time < cutoff_time:
                # Don't delete main saves, only auto-saves and backups
                if save_id.startswith("autosave_") or "_backup_" in save_id:
                    saves_to_delete.append(save_id)
        
        for save_id in saves_to_delete:
            if self.delete_save(save_id):
                deleted_count += 1
        
        return deleted_count
    
    def verify_save_integrity(self, save_id: str) -> Dict[str, Any]:
        """Verify the integrity of a save file"""
        if save_id not in self.save_metadata:
            return {"valid": False, "error": "Save not found"}
        
        metadata = self.save_metadata[save_id]
        save_file = self.save_directory / f"{save_id}.sav"
        
        if not save_file.exists():
            return {"valid": False, "error": "Save file missing"}
        
        try:
            # Check file size
            actual_size = save_file.stat().st_size
            if actual_size != metadata.file_size:
                return {
                    "valid": False, 
                    "error": f"File size mismatch: expected {metadata.file_size}, got {actual_size}"
                }
            
            # Check checksum
            with open(save_file, 'rb') as f:
                data = f.read()
            
            actual_checksum = self._calculate_checksum(data)
            if actual_checksum != metadata.checksum:
                return {
                    "valid": False,
                    "error": "Checksum mismatch - file may be corrupted"
                }
            
            # Try to load the save
            try:
                decompressed = self._decompress_data(data)
                game_state = pickle.loads(decompressed)
                
                return {
                    "valid": True,
                    "file_size": actual_size,
                    "checksum": actual_checksum,
                    "can_load": True
                }
                
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Cannot deserialize save data: {e}"
                }
        
        except Exception as e:
            return {"valid": False, "error": f"Error verifying save: {e}"}
    
    def create_game_state(self, player, world, missions, npcs, trading,
                         skills, combat, settings, statistics,
                         achievements: Optional[List[str]] = None) -> GameState:
        """Create a GameState object from game components"""
        
        # Convert objects to serializable dictionaries
        player_data = self._serialize_object(player)
        world_data = self._serialize_object(world)
        mission_data = self._serialize_object(missions)
        npc_data = self._serialize_object(npcs)
        trading_data = self._serialize_object(trading)
        skill_data = self._serialize_object(skills)
        combat_data = self._serialize_object(combat)
        
        return GameState(
            player_data=player_data,
            world_data=world_data,
            mission_data=mission_data,
            npc_data=npc_data,
            trading_data=trading_data,
            skill_data=skill_data,
            combat_data=combat_data,
            settings=settings or {},
            statistics=statistics or {},
            achievements=achievements or [],
            timestamp=time.time()
        )
    
    def _serialize_object(self, obj) -> Dict:
        """Serialize an object to a dictionary"""
        if obj is None:
            return {}
        
        if hasattr(obj, '__dict__'):
            # Convert object attributes to dictionary
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    try:
                        # Handle different data types
                        if hasattr(value, '__dict__'):
                            result[key] = self._serialize_object(value)
                        elif isinstance(value, (list, tuple)):
                            result[key] = [self._serialize_object(item) if hasattr(item, '__dict__') else item for item in value]
                        elif isinstance(value, dict):
                            result[key] = {k: self._serialize_object(v) if hasattr(v, '__dict__') else v for k, v in value.items()}
                        else:
                            result[key] = value
                    except Exception:
                        # Skip problematic attributes
                        continue
            return result
        
        return {}

# Quick save/load functions for convenience
def quick_save(save_system: SaveGameSystem, game_state: GameState) -> str:
    """Quick save with auto-generated name"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_id = f"quicksave_{timestamp}"
    return save_system.save_game(game_state, save_id, "Quick save", overwrite=True)

def quick_load(save_system: SaveGameSystem) -> Optional[GameState]:
    """Load the most recent quick save"""
    saves = save_system.get_save_list()
    quick_saves = [save for save in saves if save.save_id.startswith("quicksave_")]
    
    if quick_saves:
        # Load most recent quick save
        latest_save = max(quick_saves, key=lambda x: x.save_date)
        return save_system.load_game(latest_save.save_id)
    
    return None
