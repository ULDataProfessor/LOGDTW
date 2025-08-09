#!/usr/bin/env python3
"""
Fog of War System for LOGDTW2002
Manages sector visibility and discovery mechanics
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

@dataclass
class SectorVisibility:
    """Tracks visibility state for a single sector"""
    sector_id: int
    discovered: bool = False
    visible: bool = False
    last_visited: Optional[float] = None
    visit_count: int = 0

class FogOfWarSystem:
    """
    Manages the fog of war system for the galaxy
    
    Features:
    - Track discovered vs visible sectors
    - Sensor range determines visibility
    - Persistent discovery state
    - Save/load visibility data
    """
    
    def __init__(self, max_sectors: int = 1000):
        self.max_sectors = max_sectors
        self.sector_visibility: Dict[int, SectorVisibility] = {}
        self.discovery_percentage = 0.0
        
        # Initialize all sectors as undiscovered
        for sector_id in range(1, max_sectors + 1):
            self.sector_visibility[sector_id] = SectorVisibility(sector_id)
    
    def get_sector_visibility(self, sector_id: int) -> SectorVisibility:
        """Get visibility data for a sector"""
        if sector_id not in self.sector_visibility:
            self.sector_visibility[sector_id] = SectorVisibility(sector_id)
        return self.sector_visibility[sector_id]
    
    def is_sector_discovered(self, sector_id: int) -> bool:
        """Check if a sector has been discovered"""
        return self.get_sector_visibility(sector_id).discovered
    
    def is_sector_visible(self, sector_id: int) -> bool:
        """Check if a sector is currently visible"""
        return self.get_sector_visibility(sector_id).visible
    
    def discover_sector(self, sector_id: int, timestamp: float = None) -> bool:
        """
        Mark a sector as discovered
        Returns True if this was a new discovery
        """
        visibility = self.get_sector_visibility(sector_id)
        was_new = not visibility.discovered
        
        visibility.discovered = True
        visibility.visible = True
        if timestamp:
            visibility.last_visited = timestamp
        visibility.visit_count += 1
        
        if was_new:
            self._update_discovery_percentage()
        
        return was_new
    
    def update_visibility(self, current_sector: int, sensor_range: int, 
                         sector_connections: Dict[int, List[int]] = None) -> List[int]:
        """
        Update sector visibility based on current location and sensor range
        Returns list of newly visible sectors
        """
        newly_visible = []
        
        # Clear all visibility first
        for visibility in self.sector_visibility.values():
            visibility.visible = False
        
        # Always see current sector
        current_vis = self.get_sector_visibility(current_sector)
        if not current_vis.visible:
            current_vis.visible = True
            newly_visible.append(current_sector)
        
        # Discover current sector
        self.discover_sector(current_sector)
        
        # Use connections if available, otherwise use range-based visibility
        if sector_connections and current_sector in sector_connections:
            # Show connected sectors within sensor range
            visible_sectors = self._get_connected_sectors_in_range(
                current_sector, sensor_range, sector_connections
            )
        else:
            # Fallback to adjacent sectors based on numbering
            visible_sectors = self._get_adjacent_sectors_by_range(
                current_sector, sensor_range
            )
        
        for sector_id in visible_sectors:
            visibility = self.get_sector_visibility(sector_id)
            if not visibility.visible:
                visibility.visible = True
                newly_visible.append(sector_id)
        
        return newly_visible
    
    def _get_connected_sectors_in_range(self, current_sector: int, sensor_range: int,
                                      sector_connections: Dict[int, List[int]]) -> List[int]:
        """Get sectors visible through connections within sensor range"""
        visible = set()
        to_explore = [(current_sector, 0)]  # (sector_id, distance)
        explored = set()
        
        while to_explore:
            sector_id, distance = to_explore.pop(0)
            
            if sector_id in explored or distance > sensor_range:
                continue
                
            explored.add(sector_id)
            visible.add(sector_id)
            
            # Add connected sectors
            if sector_id in sector_connections:
                for connected_sector in sector_connections[sector_id]:
                    if connected_sector not in explored:
                        to_explore.append((connected_sector, distance + 1))
        
        return list(visible)
    
    def _get_adjacent_sectors_by_range(self, current_sector: int, sensor_range: int) -> List[int]:
        """Get sectors visible by numeric adjacency within sensor range"""
        visible = []
        
        for distance in range(1, sensor_range + 1):
            # Add sectors before and after current sector
            for offset in [-distance, distance]:
                sector_id = current_sector + offset
                if 1 <= sector_id <= self.max_sectors:
                    visible.append(sector_id)
        
        return visible
    
    def get_discovered_sectors(self) -> List[int]:
        """Get list of all discovered sectors"""
        return [
            sector_id for sector_id, visibility in self.sector_visibility.items()
            if visibility.discovered
        ]
    
    def get_visible_sectors(self) -> List[int]:
        """Get list of currently visible sectors"""
        return [
            sector_id for sector_id, visibility in self.sector_visibility.items()
            if visibility.visible
        ]
    
    def get_discovery_stats(self) -> Dict[str, float]:
        """Get discovery statistics"""
        discovered_count = len(self.get_discovered_sectors())
        return {
            'discovered_count': discovered_count,
            'total_sectors': self.max_sectors,
            'discovery_percentage': (discovered_count / self.max_sectors) * 100,
            'visible_count': len(self.get_visible_sectors())
        }
    
    def _update_discovery_percentage(self):
        """Update the discovery percentage"""
        stats = self.get_discovery_stats()
        self.discovery_percentage = stats['discovery_percentage']
    
    def get_sector_display_char(self, sector_id: int, player_sector: int = None) -> str:
        """
        Get the display character for a sector in the map
        
        Returns:
        - "🛸" for player location
        - "▩" for undiscovered
        - "·" for discovered but not visible  
        - "○" for visible
        """
        if player_sector and sector_id == player_sector:
            return "🛸"
        
        visibility = self.get_sector_visibility(sector_id)
        
        if not visibility.discovered:
            return "▩"  # Unknown
        elif visibility.visible:
            return "○"  # Visible
        else:
            return "·"  # Discovered but not currently visible
    
    def render_sector_map(self, current_sector: int, width: int = 10, height: int = 10) -> List[str]:
        """
        Render a text-based map showing fog of war
        Returns list of strings representing map rows
        """
        lines = []
        center_x, center_y = width // 2, height // 2
        
        # Calculate sector range to display
        sectors_per_row = 10  # How many sectors per map row
        base_sector = current_sector - (center_y * sectors_per_row) - center_x
        
        for y in range(height):
            row = []
            for x in range(width):
                sector_id = base_sector + (y * sectors_per_row) + x
                
                if sector_id < 1 or sector_id > self.max_sectors:
                    row.append(" ")  # Out of bounds
                else:
                    char = self.get_sector_display_char(sector_id, current_sector)
                    row.append(char)
            
            lines.append(" ".join(row))
        
        return lines
    
    def save_to_file(self, save_path: Path):
        """Save fog of war data to file"""
        data = {
            'max_sectors': self.max_sectors,
            'discovery_percentage': self.discovery_percentage,
            'sectors': {}
        }
        
        # Only save discovered sectors to reduce file size
        for sector_id, visibility in self.sector_visibility.items():
            if visibility.discovered:
                data['sectors'][str(sector_id)] = {
                    'discovered': visibility.discovered,
                    'last_visited': visibility.last_visited,
                    'visit_count': visibility.visit_count
                }
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, save_path: Path) -> bool:
        """
        Load fog of war data from file
        Returns True if successful
        """
        try:
            if not save_path.exists():
                return False
            
            with open(save_path, 'r') as f:
                data = json.load(f)
            
            self.max_sectors = data.get('max_sectors', 1000)
            self.discovery_percentage = data.get('discovery_percentage', 0.0)
            
            # Reset all sectors
            self.sector_visibility = {}
            for sector_id in range(1, self.max_sectors + 1):
                self.sector_visibility[sector_id] = SectorVisibility(sector_id)
            
            # Load discovered sectors
            sectors_data = data.get('sectors', {})
            for sector_id_str, sector_data in sectors_data.items():
                sector_id = int(sector_id_str)
                visibility = self.get_sector_visibility(sector_id)
                visibility.discovered = sector_data.get('discovered', False)
                visibility.last_visited = sector_data.get('last_visited')
                visibility.visit_count = sector_data.get('visit_count', 0)
            
            return True
            
        except Exception as e:
            print(f"Error loading fog of war data: {e}")
            return False
    
    def reset_all_visibility(self):
        """Reset all fog of war data (for new game)"""
        for visibility in self.sector_visibility.values():
            visibility.discovered = False
            visibility.visible = False
            visibility.last_visited = None
            visibility.visit_count = 0
        
        self.discovery_percentage = 0.0
    
    def get_exploration_hints(self, current_sector: int, count: int = 3) -> List[str]:
        """Get hints about nearby unexplored areas"""
        hints = []
        discovered = self.get_discovered_sectors()
        
        # Find gaps in discovered sectors
        gaps = []
        for sector_id in range(1, self.max_sectors + 1):
            if sector_id not in discovered:
                gaps.append(sector_id)
        
        if not gaps:
            return ["🎉 You've discovered the entire galaxy!"]
        
        # Find closest undiscovered sectors
        closest_gaps = sorted(gaps, key=lambda x: abs(x - current_sector))[:count]
        
        for gap in closest_gaps:
            distance = abs(gap - current_sector)
            direction = "ahead" if gap > current_sector else "behind"
            hints.append(f"📍 Unexplored sector {gap} ({distance} jumps {direction})")
        
        return hints
    
    def debug_info(self) -> Dict[str, any]:
        """Get debug information about the fog of war system"""
        stats = self.get_discovery_stats()
        visible_sectors = self.get_visible_sectors()
        
        return {
            'system': 'FogOfWarSystem',
            'stats': stats,
            'visible_sectors': visible_sectors[:10],  # First 10 for brevity
            'memory_usage': f"{len(self.sector_visibility)} sectors tracked"
        }

def create_fog_of_war_system(max_sectors: int = 1000) -> FogOfWarSystem:
    """Factory function to create a fog of war system"""
    return FogOfWarSystem(max_sectors)
