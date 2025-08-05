"""
Test data generator untuk observability testing.
"""
import asyncio
import httpx
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Generate test data untuk observability tools."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def generate_traffic(self, requests_count: int = 20):
        """Generate HTTP traffic untuk create logs dan traces."""
        endpoints = [
            "/",
            "/health", 
            "/settings",
            "/api/v1/adk/status",
            "/api/v1/adk/metrics",
            "/nonexistent-endpoint",  # Generate 404 errors
        ]
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for i in range(requests_count):
                endpoint = random.choice(endpoints)
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    logger.info(f"Generated request {i+1}: {endpoint} -> {response.status_code}")
                    
                    # Add some delay untuk realistic traffic
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                except Exception as e:
                    logger.error(f"Request failed: {endpoint} -> {str(e)}")
    
    async def generate_errors(self, error_count: int = 5):
        """Generate error scenarios."""
        error_endpoints = [
            "/api/v1/nonexistent",
            "/api/v1/adk/invalid",
            "/static/missing.js",
        ]
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for i in range(error_count):
                endpoint = random.choice(error_endpoints)
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    logger.warning(f"Generated error {i+1}: {endpoint} -> {response.status_code}")
                except Exception as e:
                    logger.error(f"Error request failed: {endpoint} -> {str(e)}")
    
    async def generate_slow_requests(self, slow_count: int = 3):
        """Generate slow requests untuk performance testing."""
        # Simulate slow operations dengan chat requests
        slow_messages = [
            "Analyze complete system performance in detail",
            "Generate comprehensive observability report", 
            "Check all system components thoroughly"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, message in enumerate(slow_messages[:slow_count]):
                try:
                    payload = {
                        "message": message,
                        "conversation_history": []
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/api/v1/adk/chat",
                        json=payload
                    )
                    
                    logger.info(f"Generated slow request {i+1}: chat -> {response.status_code}")
                    
                except Exception as e:
                    logger.error(f"Slow request failed: {str(e)}")
    
    async def run_full_test_scenario(self):
        """Run complete test scenario."""
        logger.info("🚀 Starting test data generation...")
        
        # Generate normal traffic
        await self.generate_traffic(15)
        
        # Generate some errors
        await self.generate_errors(3)
        
        # Generate slow requests
        await self.generate_slow_requests(2)
        
        logger.info("✅ Test data generation completed!")


# Global instance
test_generator = TestDataGenerator()


async def generate_test_data():
    """Helper function untuk generate test data."""
    await test_generator.run_full_test_scenario()