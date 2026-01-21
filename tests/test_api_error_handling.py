"""
Tests for API error handling and edge cases
"""
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


class TestAPIErrorHandling:
    """Test API error handling scenarios"""
    
    def test_invalid_sector_travel(self):
        """Test travel with invalid sector numbers"""
        # Test sector < 1
        response = client.post("/travel", json={"sector": 0})
        assert response.status_code in [400, 422]  # Bad request or validation error
        
        # Test sector > 1000
        response = client.post("/travel", json={"sector": 1001})
        assert response.status_code in [400, 422]
        
        # Test negative sector
        response = client.post("/travel", json={"sector": -1})
        assert response.status_code in [400, 422]
    
    def test_missing_sector_parameter(self):
        """Test travel without sector parameter"""
        response = client.post("/travel", json={})
        assert response.status_code in [400, 422]
    
    def test_invalid_trade_parameters(self):
        """Test trade with invalid parameters"""
        # Missing required fields
        response = client.post("/trade", json={})
        assert response.status_code in [400, 422]
        
        # Invalid quantity
        response = client.post("/trade", json={
            "item": "Food",
            "quantity": -1,
            "trade_action": "buy"
        })
        assert response.status_code in [400, 422]
        
        # Invalid item
        response = client.post("/trade", json={
            "item": "NonExistentItem",
            "quantity": 1,
            "trade_action": "buy"
        })
        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_insufficient_funds(self):
        """Test trade with insufficient funds"""
        # Set player credits to 0
        # This would require modifying game state or using a test fixture
        # For now, we test the structure
        response = client.post("/trade", json={
            "item": "Weapons",
            "quantity": 1000,  # Very expensive
            "trade_action": "buy"
        })
        # Should handle insufficient funds gracefully
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert not data.get("success", True) or "insufficient" in str(data).lower()
    
    def test_insufficient_inventory(self):
        """Test selling more items than available"""
        # First buy some items
        client.post("/trade", json={
            "item": "Food",
            "quantity": 5,
            "trade_action": "buy"
        })
        
        # Try to sell more than we have
        response = client.post("/trade", json={
            "item": "Food",
            "quantity": 100,
            "trade_action": "sell"
        })
        # Should handle insufficient inventory gracefully
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert not data.get("success", True) or "insufficient" in str(data).lower()
    
    def test_invalid_json(self):
        """Test API with invalid JSON"""
        response = client.post(
            "/travel",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_content_type(self):
        """Test API without Content-Type header"""
        response = client.post(
            "/travel",
            json={"sector": 2},
            headers={}  # Remove Content-Type
        )
        # FastAPI should handle this, but may return error
        assert response.status_code in [200, 400, 415]
    
    def test_status_endpoint_always_works(self):
        """Test that status endpoint handles errors gracefully"""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "player" in data


class TestAPIEdgeCases:
    """Test API edge cases"""
    
    def test_very_large_quantities(self):
        """Test trade with very large quantities"""
        response = client.post("/trade", json={
            "item": "Food",
            "quantity": 999999999,
            "trade_action": "buy"
        })
        # Should handle large numbers gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_zero_quantity(self):
        """Test trade with zero quantity"""
        response = client.post("/trade", json={
            "item": "Food",
            "quantity": 0,
            "trade_action": "buy"
        })
        assert response.status_code in [400, 422]
    
    def test_float_quantity(self):
        """Test trade with float quantity"""
        response = client.post("/trade", json={
            "item": "Food",
            "quantity": 1.5,
            "trade_action": "buy"
        })
        # Should either accept or reject gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_empty_string_item(self):
        """Test trade with empty string item"""
        response = client.post("/trade", json={
            "item": "",
            "quantity": 1,
            "trade_action": "buy"
        })
        assert response.status_code in [400, 422]
    
    def test_whitespace_item(self):
        """Test trade with whitespace-only item"""
        response = client.post("/trade", json={
            "item": "   ",
            "quantity": 1,
            "trade_action": "buy"
        })
        assert response.status_code in [400, 422]
    
    def test_special_characters_in_item(self):
        """Test trade with special characters in item name"""
        response = client.post("/trade", json={
            "item": "Food<script>alert('xss')</script>",
            "quantity": 1,
            "trade_action": "buy"
        })
        # Should handle special characters safely
        assert response.status_code in [200, 400, 422]


class TestAPIResponseFormat:
    """Test API response format consistency"""
    
    def test_success_response_format(self):
        """Test that success responses have consistent format"""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "success" in data
    
    def test_error_response_format(self):
        """Test that error responses have consistent format"""
        response = client.post("/travel", json={"sector": -1})
        assert response.status_code in [400, 422]
        data = response.json()
        # Error responses should have consistent structure
        assert isinstance(data, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

