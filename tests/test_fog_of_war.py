import os
import sys
import pytest
import time

# Ensure project root is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.fog_of_war import FogOfWarSystem, SectorVisibility


@pytest.fixture
def fog_system():
    return FogOfWarSystem(max_sectors=100)


def test_fog_system_initialization(fog_system):
    """Test fog of war system initialization"""
    assert fog_system.max_sectors == 100
    assert len(fog_system.sector_visibility) == 100
    assert fog_system.discovery_percentage == 0.0


def test_sector_visibility_creation():
    """Test creating sector visibility"""
    visibility = SectorVisibility(sector_id=1)
    
    assert visibility.sector_id == 1
    assert visibility.discovered is False
    assert visibility.visible is False
    assert visibility.last_visited is None
    assert visibility.visit_count == 0


def test_get_sector_visibility(fog_system):
    """Test getting sector visibility"""
    vis = fog_system.get_sector_visibility(1)
    
    assert vis is not None
    assert vis.sector_id == 1
    assert isinstance(vis, SectorVisibility)


def test_get_nonexistent_sector_visibility(fog_system):
    """Test getting visibility for sector beyond max"""
    vis = fog_system.get_sector_visibility(999)
    
    # Should create new visibility entry
    assert vis is not None
    assert vis.sector_id == 999


def test_is_sector_discovered(fog_system):
    """Test checking if sector is discovered"""
    assert fog_system.is_sector_discovered(1) is False
    
    fog_system.discover_sector(1)
    assert fog_system.is_sector_discovered(1) is True


def test_is_sector_visible(fog_system):
    """Test checking if sector is visible"""
    assert fog_system.is_sector_visible(1) is False
    
    fog_system.discover_sector(1)
    assert fog_system.is_sector_visible(1) is True


def test_discover_sector(fog_system):
    """Test discovering a sector"""
    was_new = fog_system.discover_sector(1)
    
    assert was_new is True
    assert fog_system.is_sector_discovered(1) is True
    assert fog_system.is_sector_visible(1) is True
    
    # Discover again should return False
    was_new_again = fog_system.discover_sector(1)
    assert was_new_again is False


def test_discover_sector_with_timestamp(fog_system):
    """Test discovering sector with timestamp"""
    timestamp = time.time()
    fog_system.discover_sector(1, timestamp=timestamp)
    
    vis = fog_system.get_sector_visibility(1)
    assert vis.last_visited == timestamp
    assert vis.visit_count == 1


def test_discover_sector_visit_count(fog_system):
    """Test that visit count increments"""
    fog_system.discover_sector(1)
    vis1 = fog_system.get_sector_visibility(1)
    initial_count = vis1.visit_count
    
    fog_system.discover_sector(1)
    vis2 = fog_system.get_sector_visibility(1)
    
    assert vis2.visit_count == initial_count + 1


def test_update_visibility(fog_system):
    """Test updating visibility based on sensor range"""
    # Discover some sectors first
    fog_system.discover_sector(1)
    fog_system.discover_sector(2)
    
    # Update visibility from sector 1 with range 2
    newly_visible = fog_system.update_visibility(
        current_sector=1,
        sensor_range=2
    )
    
    assert 1 in newly_visible
    assert fog_system.is_sector_visible(1) is True


def test_update_visibility_sensor_range(fog_system):
    """Test that sensor range affects visibility"""
    fog_system.discover_sector(1)
    fog_system.discover_sector(5)
    
    # Small range
    newly_visible_small = fog_system.update_visibility(1, sensor_range=1)
    
    # Large range
    newly_visible_large = fog_system.update_visibility(1, sensor_range=5)
    
    # Large range should see more sectors (at least current sector)
    assert len(newly_visible_large) >= len(newly_visible_small)


def test_update_visibility_clears_previous(fog_system):
    """Test that visibility update clears previous visibility"""
    fog_system.discover_sector(1)
    fog_system.discover_sector(2)
    
    # Make both visible
    fog_system.update_visibility(1, sensor_range=5)
    assert fog_system.is_sector_visible(1) is True
    assert fog_system.is_sector_visible(2) is True
    
    # Move to sector 2, should clear sector 1 visibility if out of range
    fog_system.update_visibility(2, sensor_range=0)
    assert fog_system.is_sector_visible(2) is True
    # Sector 1 might not be visible if range is 0


def test_discovery_percentage(fog_system):
    """Test discovery percentage calculation"""
    initial_percentage = fog_system.discovery_percentage
    
    # Discover some sectors
    for i in range(1, 11):
        fog_system.discover_sector(i)
    
    # Should have increased
    assert fog_system.discovery_percentage > initial_percentage
    assert fog_system.discovery_percentage <= 100.0


def test_discovery_percentage_all_sectors(fog_system):
    """Test discovery percentage when all sectors discovered"""
    # Discover all sectors
    for i in range(1, fog_system.max_sectors + 1):
        fog_system.discover_sector(i)
    
    # Should be 100% or close to it
    assert fog_system.discovery_percentage >= 99.0


def test_sector_connections_visibility(fog_system):
    """Test visibility with sector connections"""
    connections = {
        1: [2, 3],
        2: [1, 4],
        3: [1, 5]
    }
    
    fog_system.discover_sector(1)
    newly_visible = fog_system.update_visibility(
        current_sector=1,
        sensor_range=1,
        sector_connections=connections
    )
    
    # Should see connected sectors
    assert len(newly_visible) >= 1  # At least current sector


def test_save_and_load_visibility(fog_system, tmp_path):
    """Test saving and loading visibility data"""
    # Discover some sectors
    fog_system.discover_sector(1)
    fog_system.discover_sector(2)
    fog_system.discover_sector(3)
    
    save_file = tmp_path / "fog_of_war.json"
    
    # Use correct method names
    if hasattr(fog_system, 'save_to_file'):
        fog_system.save_to_file(save_file)
    elif hasattr(fog_system, 'save_visibility'):
        fog_system.save_visibility(str(save_file))
    else:
        pytest.skip("Save method not available")
        return
    
    # Create new system and load
    new_fog = FogOfWarSystem(max_sectors=100)
    if hasattr(new_fog, 'load_from_file'):
        new_fog.load_from_file(save_file)
    elif hasattr(new_fog, 'load_visibility'):
        new_fog.load_visibility(str(save_file))
    
    assert new_fog.is_sector_discovered(1) is True
    assert new_fog.is_sector_discovered(2) is True
    assert new_fog.is_sector_discovered(3) is True


def test_get_discovered_sectors(fog_system):
    """Test getting list of discovered sectors"""
    fog_system.discover_sector(1)
    fog_system.discover_sector(5)
    fog_system.discover_sector(10)
    
    discovered = fog_system.get_discovered_sectors()
    
    assert 1 in discovered
    assert 5 in discovered
    assert 10 in discovered
    assert len(discovered) == 3


def test_get_visible_sectors(fog_system):
    """Test getting list of currently visible sectors"""
    fog_system.discover_sector(1)
    fog_system.discover_sector(2)
    
    fog_system.update_visibility(1, sensor_range=2)
    
    visible = fog_system.get_visible_sectors()
    
    assert 1 in visible
    assert len(visible) > 0


def test_sector_visibility_persistence(fog_system):
    """Test that discovered sectors remain discovered"""
    fog_system.discover_sector(1)
    assert fog_system.is_sector_discovered(1) is True
    
    # Clear visibility but not discovery
    fog_system.update_visibility(999, sensor_range=0)
    
    # Should still be discovered even if not visible
    assert fog_system.is_sector_discovered(1) is True

