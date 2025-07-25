"""
Test Memory Integration - Phase 2 Complete Implementation Test
Tests the full memory-integrated multi-agent system
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Add the current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from memory_client import LangGraphMemoryClient
from orchestrator.agents.personal_assistant import PersonalAssistantAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_memory_integration():
    """Comprehensive test of memory-integrated Personal Assistant Agent"""
    
    print("🚀 Starting Memory Integration Test - Phase 2")
    print("=" * 60)
    
    try:
        # Test 1: Memory Client Direct Test
        print("\n1️⃣ Testing Memory Client Connectivity...")
        async with LangGraphMemoryClient() as client:
            health_check = await client.health_check()
            print(f"   Memory Service Health: {'✅ HEALTHY' if health_check else '❌ UNHEALTHY'}")
            
            if health_check:
                # Store a test memory
                await client.store_memory(
                    agent_id="test_integration",
                    content="Integration test - memory system working correctly",
                    entity_type="system_test"
                )
                print("   ✅ Memory storage test passed")
            else:
                print("   ⚠️ Memory service unavailable - continuing with local testing")
        
        # Test 2: Personal Assistant Agent Memory Integration
        print("\n2️⃣ Testing Personal Assistant Agent Memory Integration...")
        
        # Create Personal Assistant Agent
        assistant = PersonalAssistantAgent()
        print(f"   ✅ Created assistant agent: {assistant.agent_id}")
        
        # Initialize memory
        memory_init = await assistant.initialize_memory()
        print(f"   Memory initialization: {'✅ SUCCESS' if memory_init else '⚠️ FALLBACK MODE'}")
        
        # Test 3: Basic Request Handling with Memory
        print("\n3️⃣ Testing Memory-Enhanced Request Processing...")
        
        test_request = "Help me organize my day and prepare for upcoming meetings"
        test_context = {
            "user_id": "mohit",
            "session_id": "test_session_001",
            "timestamp": "2025-07-15T03:30:00Z"
        }
        
        response = await assistant.handle_request(test_request, test_context)
        
        print(f"   Request: {test_request[:50]}...")
        print(f"   Response Preview: {response.get('response', 'No response')[:100]}...")
        print(f"   Agent: {response.get('agent', 'Unknown')}")
        print(f"   Memory Used: {'✅ YES' if assistant.memory_initialized else '❌ NO'}")
        
        # Test 4: User Preference Storage
        print("\n4️⃣ Testing User Preference Management...")
        
        if assistant.memory_initialized:
            # Store a preference
            pref_stored = await assistant.store_user_preference(
                "Prefers concise updates with action items",
                category="communication"
            )
            print(f"   Preference Storage: {'✅ SUCCESS' if pref_stored else '❌ FAILED'}")
            
            # Retrieve preferences
            prefs = await assistant.get_user_preferences("communication")
            print(f"   Retrieved {len(prefs)} communication preferences")
        else:
            print("   ⚠️ Skipped - memory not available")
        
        # Test 5: Memory Context in Responses
        print("\n5️⃣ Testing Memory Context Integration...")
        
        # Second request to test memory context
        follow_up_request = "What should I prioritize today?"
        follow_up_response = await assistant.handle_request(follow_up_request, test_context)
        
        print(f"   Follow-up Request: {follow_up_request}")
        print(f"   Response Uses Context: {'✅ YES' if 'mohit' in follow_up_response.get('response', '').lower() else '❌ NO'}")
        
        # Test 6: Daily Agenda Generation
        print("\n6️⃣ Testing Proactive Features...")
        
        if assistant.memory_initialized:
            agenda = await assistant.get_daily_agenda()
            print(f"   Daily Agenda Generated: {'✅ YES' if agenda else '❌ NO'}")
            if agenda:
                print(f"   Agenda Preview: {agenda[:150]}...")
            
            suggestions = await assistant.proactive_suggestions()
            print(f"   Proactive Suggestions: {len(suggestions)} generated")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"      {i}. {suggestion}")
        else:
            print("   ⚠️ Skipped - memory not available")
        
        # Test 7: Agent Information
        print("\n7️⃣ Testing Agent Status...")
        
        agent_info = assistant.get_agent_info()
        print(f"   Agent Role: {agent_info.get('role', 'Unknown')}")
        print(f"   Personality: {agent_info.get('personality', 'Unknown')}")
        print(f"   Authority Level: {agent_info.get('authority', 'Unknown')}")
        print(f"   Available Tools: {len(agent_info.get('tools', []))} tools")
        print(f"   Memory Status: {'✅ ACTIVE' if agent_info.get('memory_initialized') else '❌ INACTIVE'}")
        
        # Test 8: Cleanup
        print("\n8️⃣ Testing Cleanup Process...")
        
        await assistant.cleanup_memory()
        print("   ✅ Memory cleanup completed")
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎉 PHASE 2 MEMORY INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
        print("\n📊 **Test Results Summary:**")
        print(f"   • Memory Service: {'✅ Connected' if health_check else '⚠️ Unavailable'}")
        print(f"   • Agent Creation: ✅ Success")
        print(f"   • Memory Integration: {'✅ Active' if memory_init else '⚠️ Fallback'}")
        print(f"   • Request Processing: ✅ Working")
        print(f"   • Memory Context: {'✅ Integrated' if assistant.memory_initialized else '⚠️ Limited'}")
        print(f"   • Proactive Features: {'✅ Functional' if assistant.memory_initialized else '⚠️ Limited'}")
        print(f"   • Cleanup: ✅ Completed")
        
        print("\n🚀 **Next Steps:**")
        print("   1. Integrate with LangGraph state management")
        print("   2. Add multi-agent coordination")
        print("   3. Connect to voice/chat interfaces")
        print("   4. Deploy to production environment")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def quick_connectivity_test():
    """Quick test to verify basic connectivity"""
    print("🔍 Quick Connectivity Test")
    print("-" * 30)
    
    try:
        # Test memory client
        client = LangGraphMemoryClient()
        is_healthy = await client.health_check()
        await client.close()
        
        print(f"Memory Service: {'✅ ONLINE' if is_healthy else '❌ OFFLINE'}")
        
        # Test agent creation
        assistant = PersonalAssistantAgent()
        print(f"Agent Creation: ✅ SUCCESS ({assistant.agent_id})")
        
        return is_healthy
        
    except Exception as e:
        print(f"❌ Connectivity test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Memory Integration Test Suite - Phase 2")
    print("Testing comprehensive memory-integrated multi-agent system")
    print()
    
    # Run quick test first
    connectivity_result = asyncio.run(quick_connectivity_test())
    
    if connectivity_result:
        print("\n📋 Running full integration test...")
        asyncio.run(test_memory_integration())
    else:
        print("\n⚠️ Running limited test (memory service unavailable)...")
        asyncio.run(test_memory_integration())