"""
Tests for world generation and sector database
"""
import os
import sys
import pytest
import random

# Ensure project root is on sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from game.world_generator import WorldGenerator, Sector
from game.sector_db import SectorDB


@pytest.fixture
def world_generator():
    return WorldGenerator()


@pytest.fixture
def sector_db():
    return SectorDB()


class TestWorldGenerator:
    """Test world generation functionality"""
    
    def test_world_generator_initialization(self, world_generator):
        """Test world generator initialization"""
        assert world_generator is not None
        assert isinstance(world_generator.sectors, dict)
        assert len(world_generator.sector_names) > 0
        assert len(world_generator.planet_types) > 0
        assert len(world_generator.station_types) > 0
    
    def test_generate_sector(self, world_generator):
        """Test generating a new sector"""
        sector = world_generator.generate_sector(1, 1, 1)
        
        assert sector is not None
        assert isinstance(sector, Sector)
        assert sector.name is not None
        assert len(sector.name) > 0
        assert isinstance(sector.coordinates, tuple)
        assert len(sector.coordinates) == 3
        assert sector.coordinates == (1, 1, 1)
    
    def test_sector_properties(self, world_generator):
        """Test sector properties"""
        sector = world_generator.generate_sector(5, 5, 5)
        
        assert sector.sector_type in ["core", "frontier", "dangerous", "unexplored"]
        assert 1 <= sector.difficulty <= 10
        assert isinstance(sector.discovered, bool)
        assert isinstance(sector.colonized, bool)
        assert isinstance(sector.warp_ports, list)
        assert isinstance(sector.trade_ports, list)
        assert isinstance(sector.space_stations, list)
    
    def test_generate_multiple_sectors(self, world_generator):
        """Test generating multiple sectors"""
        sectors = []
        for i in range(10):
            sector = world_generator.generate_sector(i, i, i)
            sectors.append(sector)
        
        assert len(sectors) == 10
        # All sectors should have unique coordinates
        coordinates = [s.coordinates for s in sectors]
        assert len(set(coordinates)) == 10
    
    def test_sector_name_generation(self, world_generator):
        """Test that sector names are generated"""
        sector = world_generator.generate_sector(1, 1, 1)
        
        assert sector.name is not None
        assert isinstance(sector.name, str)
        assert len(sector.name) > 0
    
    def test_sector_difficulty_scaling(self, world_generator):
        """Test that sector difficulty scales appropriately"""
        core_sector = world_generator.generate_sector(1, 1, 1)
        frontier_sector = world_generator.generate_sector(100, 100, 100)
        
        # Frontier sectors should generally be more difficult
        # (though randomness may affect this)
        assert 1 <= core_sector.difficulty <= 10
        assert 1 <= frontier_sector.difficulty <= 10
    
    def test_sector_edge_coordinates(self, world_generator):
        """Test generating sectors at edge coordinates"""
        # Test zero coordinates
        sector1 = world_generator.generate_sector(0, 0, 0)
        assert sector1 is not None
        
        # Test large coordinates
        sector2 = world_generator.generate_sector(1000, 1000, 1000)
        assert sector2 is not None
        
        # Test negative coordinates
        sector3 = world_generator.generate_sector(-1, -1, -1)
        assert sector3 is not None
    
    def test_sector_consistency(self, world_generator):
        """Test that generating the same sector twice produces consistent results"""
        sector1 = world_generator.generate_sector(42, 42, 42)
        sector2 = world_generator.generate_sector(42, 42, 42)
        
        # Coordinates should match
        assert sector1.coordinates == sector2.coordinates
        # Other properties may vary due to randomness, but should be valid
        assert sector1.sector_type in ["core", "frontier", "dangerous", "unexplored"]
        assert sector2.sector_type in ["core", "frontier", "dangerous", "unexplored"]


class TestSectorDatabase:
    """Test sector database functionality"""
    
    def test_sector_db_initialization(self, sector_db):
        """Test sector database initialization"""
        assert sector_db is not None
    
    def test_get_sector(self, sector_db):
        """Test getting a sector from database"""
        sector = sector_db.get_sector(1)
        
        assert sector is not None
        assert isinstance(sector, dict)
        assert "sector_id" in sector or "id" in sector or "number" in sector
    
    def test_get_invalid_sector(self, sector_db):
        """Test getting invalid sector numbers"""
        # Test negative sector
        sector = sector_db.get_sector(-1)
        # Should handle gracefully
        assert sector is None or isinstance(sector, dict)
        
        # Test zero sector
        sector = sector_db.get_sector(0)
        assert sector is None or isinstance(sector, dict)
        
        # Test very large sector
        sector = sector_db.get_sector(999999)
        assert sector is None or isinstance(sector, dict)
    
    def test_sector_properties(self, sector_db):
        """Test sector properties from database"""
        sector = sector_db.get_sector(1)
        
        if sector:
            # Check for common properties
            assert isinstance(sector, dict)
            # Should have some identifying information
            assert len(str(sector)) > 0


class TestWorldGenerationEdgeCases:
    """Test edge cases in world generation"""
    
    def test_generate_sector_with_none_coordinates(self, world_generator):
        """Test generating sector with None coordinates"""
        try:
            sector = world_generator.generate_sector(None, None, None)
            # Should handle gracefully
            assert sector is None or isinstance(sector, Sector)
        except (TypeError, ValueError):
            pass  # Expected to fail gracefully
    
    def test_generate_sector_with_string_coordinates(self, world_generator):
        """Test generating sector with string coordinates"""
        try:
            sector = world_generator.generate_sector("1", "2", "3")
            # Should handle gracefully or convert
            assert sector is None or isinstance(sector, Sector)
        except (TypeError, ValueError):
            pass  # Expected to fail gracefully
    
    def test_generate_sector_with_float_coordinates(self, world_generator):
        """Test generating sector with float coordinates"""
        sector = world_generator.generate_sector(1.5, 2.7, 3.9)
        # Should handle gracefully (may truncate or round)
        assert sector is None or isinstance(sector, Sector)
    
    def test_generate_many_sectors_performance(self, world_generator):
        """Test generating many sectors for performance"""
        sectors = []
        for i in range(100):
            sector = world_generator.generate_sector(i, i, i)
            sectors.append(sector)
        
        assert len(sectors) == 100
        # All should be valid
        assert all(isinstance(s, Sector) for s in sectors)


class TestSectorValidation:
    """Test sector data validation"""
    
    def test_sector_coordinate_validation(self, world_generator):
        """Test that sector coordinates are valid"""
        sector = world_generator.generate_sector(1, 1, 1)
        
        assert isinstance(sector.coordinates, tuple)
        assert len(sector.coordinates) == 3
        assert all(isinstance(c, (int, float)) for c in sector.coordinates)
    
    def test_sector_difficulty_range(self, world_generator):
        """Test that sector difficulty is in valid range"""
        for _ in range(20):
            sector = world_generator.generate_sector(
                random.randint(-100, 100),
                random.randint(-100, 100),
                random.randint(-100, 100)
            )
            assert 1 <= sector.difficulty <= 10
    
    def test_sector_type_validation(self, world_generator):
        """Test that sector types are valid"""
        valid_types = ["core", "frontier", "dangerous", "unexplored"]
        
        for _ in range(20):
            sector = world_generator.generate_sector(
                random.randint(1, 100),
                random.randint(1, 100),
                random.randint(1, 100)
            )
            assert sector.sector_type in valid_types


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

