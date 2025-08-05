#!/usr/bin/env python3
"""
Test script untuk Observability Chat-Based API dengan Google ADK.
"""
import asyncio
import httpx
import json
from datetime import datetime


class ObservabilityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.adk_base = f"{base_url}/api/v1/adk"
    
    async def test_adk_status(self):
        """Test ADK agent status."""
        print("🔍 Testing ADK Agent Status...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.adk_base}/status")
                data = response.json()
                
                if data.get("available"):
                    print(f"✅ ADK Agent Available: {data.get('agent_name')}")
                    print(f"   Model: {data.get('model')}")
                else:
                    print("❌ ADK Agent Not Available")
                    print("   Check GEMINI_API_KEY configuration")
                
                return data.get("available", False)
            except Exception as e:
                print(f"❌ Error checking ADK status: {e}")
                return False
    
    async def test_chat_indonesian(self):
        """Test chat dengan bahasa Indonesia."""
        print("\n💬 Testing Chat in Indonesian...")
        
        messages = [
            "Tampilkan ringkasan observability sistem saat ini",
            "Ada error apa saja dalam 1 jam terakhir?",
            "Bagaimana performa sistem hari ini?",
            "Cek traces yang lambat"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for message in messages:
                try:
                    print(f"\n👤 User: {message}")
                    
                    response = await client.post(
                        f"{self.adk_base}/chat",
                        json={
                            "message": message,
                            "conversation_history": []
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"🤖 Agent: {data['response'][:200]}...")
                    else:
                        print(f"❌ Chat failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error in chat: {e}")
    
    async def test_chat_english(self):
        """Test chat dengan bahasa English."""
        print("\n💬 Testing Chat in English...")
        
        messages = [
            "What is the current health status of the system?",
            "Show me recent error logs",
            "Check slow traces and operations",
            "Analyze system performance trends"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for message in messages:
                try:
                    print(f"\n👤 User: {message}")
                    
                    response = await client.post(
                        f"{self.adk_base}/chat",
                        json={
                            "message": message,
                            "conversation_history": []
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"🤖 Agent: {data['response'][:200]}...")
                    else:
                        print(f"❌ Chat failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error in chat: {e}")
    
    async def test_direct_apis(self):
        """Test direct API endpoints."""
        print("\n🔗 Testing Direct API Endpoints...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test logs query
            try:
                print("\n📝 Testing Logs Query...")
                response = await client.get(f"{self.adk_base}/logs?limit=5")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Found {len(data.get('logs', []))} logs")
                    if data.get('logs'):
                        latest_log = data['logs'][0]
                        print(f"   Latest: [{latest_log['level']}] {latest_log['message'][:50]}...")
                else:
                    print(f"❌ Logs query failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error querying logs: {e}")
            
            # Test traces query
            try:
                print("\n🔍 Testing Traces Query...")
                response = await client.get(f"{self.adk_base}/traces?limit=5")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Found {len(data.get('traces', []))} traces")
                    if data.get('traces'):
                        latest_trace = data['traces'][0]
                        print(f"   Latest: {latest_trace['duration_ms']:.2f}ms, {latest_trace['spans']} spans")
                else:
                    print(f"❌ Traces query failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error querying traces: {e}")
            
            # Test performance analysis
            try:
                print("\n⚡ Testing Performance Analysis...")
                response = await client.get(f"{self.adk_base}/performance")
                if response.status_code == 200:
                    data = response.json()
                    analysis = data.get('analysis', {})
                    print(f"✅ Performance Analysis Complete")
                    print(f"   Errors: {analysis.get('error_count', 0)}")
                    print(f"   Avg Response: {analysis.get('avg_response_time_ms', 0)}ms")
                    print(f"   Issues: {len(analysis.get('issues', []))}")
                else:
                    print(f"❌ Performance analysis failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error analyzing performance: {e}")
            
            # Test observability summary
            try:
                print("\n📊 Testing Observability Summary...")
                response = await client.get(f"{self.adk_base}/observability-summary")
                if response.status_code == 200:
                    data = response.json()
                    summary = data.get('summary', {})
                    print(f"✅ Observability Summary Complete")
                    print(f"   Recent Logs: {summary.get('recent_logs_count', 0)}")
                    print(f"   Recent Traces: {summary.get('recent_traces_count', 0)}")
                    print(f"   CPU Usage: {summary.get('system_cpu_percent', 0):.1f}%")
                    print(f"   Memory Usage: {summary.get('system_memory_percent', 0):.1f}%")
                else:
                    print(f"❌ Observability summary failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error getting observability summary: {e}")
    
    async def test_health_and_metrics(self):
        """Test health check dan metrics."""
        print("\n🏥 Testing Health Check and Metrics...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test health check
            try:
                response = await client.get(f"{self.adk_base}/health-check")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Health Check: {data.get('overall_status', 'unknown').upper()}")
                    
                    components = data.get('components', {})
                    for component, status in components.items():
                        print(f"   {component}: {status.get('status', 'unknown')}")
                else:
                    print(f"❌ Health check failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error in health check: {e}")
            
            # Test metrics
            try:
                response = await client.get(f"{self.adk_base}/metrics")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Metrics Collection Complete")
                    
                    if 'system' in data:
                        sys_metrics = data['system']
                        print(f"   CPU: {sys_metrics.get('cpu_percent', 0):.1f}%")
                        print(f"   Memory: {sys_metrics.get('memory', {}).get('percent', 0):.1f}%")
                        print(f"   Disk: {sys_metrics.get('disk', {}).get('percent', 0):.1f}%")
                    
                    if 'application' in data:
                        app_metrics = data['application']
                        print(f"   App Memory: {app_metrics.get('memory_mb', 0):.1f}MB")
                        print(f"   Threads: {app_metrics.get('threads', 0)}")
                else:
                    print(f"❌ Metrics collection failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error collecting metrics: {e}")
    
    async def generate_test_data(self):
        """Generate some test data untuk observability."""
        print("\n🎯 Generating Test Data...")
        
        async with httpx.AsyncClient() as client:
            # Generate some requests untuk create logs dan traces
            endpoints = ["/", "/health", "/settings", "/api/v1/adk/status"]
            
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    print(f"✅ Generated request: {endpoint} -> {response.status_code}")
                except Exception as e:
                    print(f"❌ Error generating request to {endpoint}: {e}")
            
            # Generate some errors untuk testing
            try:
                response = await client.get(f"{self.base_url}/nonexistent-endpoint")
                print(f"✅ Generated error request: /nonexistent-endpoint -> {response.status_code}")
            except Exception as e:
                print(f"✅ Generated error request: /nonexistent-endpoint -> Error")
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Observability Chat-Based API Tests")
        print("=" * 60)
        
        # Check if ADK agent is available
        agent_available = await self.test_adk_status()
        
        if not agent_available:
            print("\n❌ ADK Agent not available. Please check GEMINI_API_KEY configuration.")
            print("   Set environment variable: export GEMINI_API_KEY=your_api_key")
            return
        
        # Generate test data first
        await self.generate_test_data()
        
        # Wait a bit for data to be processed
        print("\n⏳ Waiting for data to be processed...")
        await asyncio.sleep(3)
        
        # Run tests
        await self.test_health_and_metrics()
        await self.test_direct_apis()
        await self.test_chat_indonesian()
        await self.test_chat_english()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("\n📊 Access Web Interface: http://localhost:8000/adk-web")
        print("📚 API Documentation: http://localhost:8000/api/v1/docs")
        print("🔍 Jaeger UI: http://localhost:16686")
        print("📈 Grafana: http://localhost:3000 (admin/admin)")


async def main():
    """Main function."""
    tester = ObservabilityTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())