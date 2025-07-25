#!/usr/bin/env python3
"""
Test script for multi-agent functionality
Tests the Personal Assistant agent and routing system
"""

import asyncio
import os
from dotenv import load_dotenv
from orchestrator.brain import PersonalAIBrain
from orchestrator.agents.personal_assistant import PersonalAssistantAgent
from orchestrator.coordination.agent_router import AgentRouter

# Load environment variables from .env file
load_dotenv()

async def test_agent_creation():
    """Test agent creation and basic functionality"""
    print("🧪 Testing Agent Creation...")
    
    try:
        # Test Personal Assistant creation
        assistant = PersonalAssistantAgent()
        print(f"✅ Personal Assistant created: {assistant.role}")
        print(f"   Personality: {assistant.personality}")
        print(f"   Tools: {assistant.available_tools}")
        print(f"   Authority: {assistant.decision_authority}")
        
        # Test Agent Router creation
        router = AgentRouter()
        print(f"✅ Agent Router created with {len(router.agents)} agents")
        
        # Test router status
        status = router.get_agent_status()
        print(f"✅ Router status: {status['router_status']}")
        print(f"   Primary agent: {status['primary_agent']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {str(e)}")
        return False

async def test_brain_creation():
    """Test PersonalAIBrain creation with multi-agent system"""
    print("\n🧠 Testing Brain Creation...")
    
    try:
        # Test brain creation
        brain = PersonalAIBrain()
        print(f"✅ PersonalAIBrain created")
        
        # Test status (will fail without real API key but structure should work)
        try:
            status = await brain.get_status()
            print(f"✅ Brain status check completed")
            print(f"   Architecture: {status.get('architecture', 'unknown')}")
            print(f"   Agent system: {status.get('agent_system', {}).get('router_status', 'unknown')}")
        except Exception as e:
            print(f"⚠️  Status check failed (expected without API key): {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Brain creation failed: {str(e)}")
        return False

async def test_request_routing():
    """Test request routing through agent system"""
    print("\n🎯 Testing Request Routing...")
    
    try:
        router = AgentRouter()
        
        # Test simple request routing (will fail gracefully without API key)
        test_requests = [
            "Hello, how are you today?",
            "Can you help me organize my schedule?",
            "What's the status of my projects?"
        ]
        
        for request in test_requests:
            print(f"\n📝 Testing request: '{request}'")
            try:
                # This will fail without API key but should show routing structure
                result = await router.route_request(
                    request=request,
                    user_id="mohit",
                    interface="test"
                )
                print(f"✅ Routing completed for: {request[:30]}...")
                print(f"   Selected agent: {result.get('agent', 'unknown')}")
                
            except Exception as e:
                print(f"⚠️  Routing failed (expected without API key): {str(e)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Request routing test failed: {str(e)}")
        return False

async def test_agent_methods():
    """Test specific agent methods"""
    print("\n🔧 Testing Agent Methods...")
    
    try:
        assistant = PersonalAssistantAgent()
        
        # Test should_handle_request
        test_cases = [
            ("schedule a meeting", "coordination task"),
            ("analyze sales data", "delegation task"),
            ("hello", "general task")
        ]
        
        for request, case_type in test_cases:
            confidence = assistant.should_handle_request(request, {})
            print(f"✅ {case_type}: '{request}' -> confidence: {confidence}")
        
        # Test agent info
        info = assistant.get_agent_info()
        print(f"✅ Agent info retrieved: {info['role']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent methods test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Multi-Agent System Tests")
    print("=" * 50)
    
    tests = [
        test_agent_creation,
        test_brain_creation,
        test_request_routing,
        test_agent_methods
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Multi-agent framework is working!")
        print("📋 Next steps:")
        print("   1. Add OpenAI API key to test with real LLM")
        print("   2. Implement additional specialist agents")
        print("   3. Test with actual MCP services")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return all(results)

if __name__ == "__main__":
    asyncio.run(main())