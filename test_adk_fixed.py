#!/usr/bin/env python3
"""
Quick test untuk memverifikasi ADK Observability Chat API sudah berfungsi.
"""
import requests
import json

BASE_URL = "http://localhost:8000"
ADK_BASE = f"{BASE_URL}/api/v1/adk"

def test_adk_status():
    """Test ADK status."""
    print("🔍 Testing ADK Status...")
    response = requests.get(f"{ADK_BASE}/status")
    data = response.json()
    
    if data.get("available"):
        print(f"✅ ADK Agent Available: {data.get('agent_name', 'N/A')}")
        return True
    else:
        print("❌ ADK Agent Not Available")
        return False

def test_chat_indonesian():
    """Test chat dalam bahasa Indonesia."""
    print("\n💬 Testing Chat (Indonesian)...")
    
    payload = {
        "message": "Tampilkan ringkasan observability sistem saat ini",
        "conversation_history": []
    }
    
    response = requests.post(f"{ADK_BASE}/chat", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat Response: {data['response'][:100]}...")
        return True
    else:
        print(f"❌ Chat failed: {response.status_code}")
        return False

def test_chat_english():
    """Test chat dalam bahasa English."""
    print("\n💬 Testing Chat (English)...")
    
    payload = {
        "message": "What is the current health status?",
        "conversation_history": []
    }
    
    response = requests.post(f"{ADK_BASE}/chat", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat Response: {data['response'][:100]}...")
        return True
    else:
        print(f"❌ Chat failed: {response.status_code}")
        return False

def test_observability_summary():
    """Test observability summary."""
    print("\n📊 Testing Observability Summary...")
    
    response = requests.get(f"{ADK_BASE}/observability-summary")
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', {})
        print(f"✅ Summary - Logs: {summary.get('recent_logs_count', 0)}, "
              f"Traces: {summary.get('recent_traces_count', 0)}, "
              f"CPU: {summary.get('system_cpu_percent', 0):.1f}%")
        return True
    else:
        print(f"❌ Summary failed: {response.status_code}")
        return False

def test_web_interface():
    """Test web interface."""
    print("\n🌐 Testing Web Interface...")
    
    response = requests.get(f"{BASE_URL}/adk-web")
    
    if response.status_code == 200 and "ADK Observability Dashboard" in response.text:
        print("✅ Web Interface Available")
        return True
    else:
        print("❌ Web Interface Failed")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing ADK Observability Chat API")
    print("=" * 50)
    
    tests = [
        test_adk_status,
        test_observability_summary,
        test_chat_indonesian,
        test_chat_english,
        test_web_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! ADK Observability Chat API is working!")
        print("\n📊 Access Web Interface: http://localhost:8000/adk-web")
        print("📚 API Documentation: http://localhost:8000/api/v1/docs")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()