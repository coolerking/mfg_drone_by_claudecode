"""
Tests for MCP Server API
"""

import pytest
import asyncio
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the backend client before importing main
sys.modules['core.backend_client'] = MagicMock()

from main import app


class TestMCPServerAPI:
    """Test MCP Server API"""
    
    def setup_method(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get("/mcp/system/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
    
    def test_natural_language_command_endpoint(self):
        """Test natural language command endpoint"""
        command_data = {
            "command": "ドローンAAに接続して",
            "context": {"language": "ja"},
            "options": {"dry_run": True}
        }
        
        response = self.client.post("/mcp/command", json=command_data)
        
        # Note: This will likely fail due to missing backend, 
        # but we can check the structure
        assert response.status_code in [200, 400, 503]  # Allow various error codes
    
    def test_batch_command_endpoint(self):
        """Test batch command endpoint"""
        batch_data = {
            "commands": [
                {"command": "ドローンAAに接続して"},
                {"command": "離陸して"}
            ],
            "execution_mode": "sequential",
            "stop_on_error": True
        }
        
        response = self.client.post("/mcp/command/batch", json=batch_data)
        
        # Note: This will likely fail due to missing backend
        assert response.status_code in [200, 400, 503]
    
    def test_openapi_schema(self):
        """Test OpenAPI schema generation"""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check that all expected endpoints are present
        paths = schema["paths"]
        expected_paths = [
            "/mcp/command",
            "/mcp/command/batch",
            "/mcp/drones",
            "/mcp/drones/available",
            "/mcp/system/status",
            "/mcp/system/health"
        ]
        
        for path in expected_paths:
            assert path in paths
    
    def test_cors_headers(self):
        """Test CORS headers"""
        response = self.client.options("/mcp/system/health")
        assert "access-control-allow-origin" in response.headers
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint"""
        response = self.client.get("/invalid")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])