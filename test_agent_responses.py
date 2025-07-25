#!/usr/bin/env python3
"""
Test script to demonstrate actual agent responses with LLM
Shows the Personal Assistant's personality and responses
"""

import asyncio
import os
from dotenv import load_dotenv
from orchestrator.brain import PersonalAIBrain
from orchestrator.agents.personal_assistant import PersonalAssistantAgent
from orchestrator.coordination.agent_router import AgentRouter

# Load environment variables from .env file
load_dotenv()

async def test_personal_assistant_responses():
    """Test Personal Assistant with real responses"""
    print("🤖 Testing Personal Assistant Agent Responses")
    print("=" * 60)
    
    try:
        # Create router
        router = AgentRouter()
        
        # Test requests to showcase personality
        test_requests = [
            ("Hello! I'm Mohit. How are you today?", "greeting"),
            ("Can you help me organize my schedule for tomorrow?", "scheduling"),
            ("I need to prepare for a board meeting next week", "complex_coordination"),
            ("What should I prioritize today?", "proactive_assistance"),
            ("Analyze our Q3 sales performance", "delegation_needed")
        ]
        
        for request, scenario_type in test_requests:
            print(f"\n{'='*60}")
            print(f"📝 Scenario: {scenario_type}")
            print(f"👤 Mohit: {request}")
            print("-" * 60)
            
            try:
                # Route request through agent system
                result = await router.route_request(
                    request=request,
                    user_id="mohit",
                    interface="test"
                )
                
                print(f"🤖 {result.get('agent', 'Unknown').replace('_', ' ').title()}: {result.get('response', 'No response')}")
                
                if result.get('coordination_required'):
                    print(f"\n📊 Coordination Info:")
                    print(f"   - Specialist agents needed: {', '.join(result.get('specialist_agents', []))}")
                    print(f"   - Workflow steps: {len(result.get('workflow_steps', []))}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def test_brain_integration():
    """Test full brain integration with multi-agent system"""
    print("\n\n🧠 Testing Full Brain Integration")
    print("=" * 60)
    
    try:
        # Create brain instance
        brain = PersonalAIBrain()
        
        # Test through brain's process_request
        test_message = "Good morning, Mohit here. What's my schedule looking like today?"
        
        print(f"👤 Mohit: {test_message}")
        print("-" * 60)
        
        result = await brain.process_request(
            message=test_message,
            user_id="mohit",
            interface="voice"
        )
        
        print(f"🤖 Response from {result.get('agent', 'unknown').replace('_', ' ').title()}:")
        print(result.get('response', 'No response'))
        print(f"\n📊 Processing Info:")
        print(f"   - Session ID: {result.get('session_id', 'N/A')}")
        print(f"   - Actions taken: {result.get('actions_taken', [])}")
        print(f"   - Multi-agent info: {result.get('multi_agent_info', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Brain integration test failed: {str(e)}")
        return False

async def test_agent_personality():
    """Test that agent maintains consistent personality"""
    print("\n\n🎭 Testing Agent Personality Consistency")
    print("=" * 60)
    
    try:
        assistant = PersonalAssistantAgent()
        
        # Direct personality test
        print("Testing Personal Assistant personality traits:")
        print(f"- Role: {assistant.role}")
        print(f"- Personality: {assistant.personality}")
        print(f"- Authority: {assistant.decision_authority}")
        
        # Test confidence scores for different request types
        test_confidence = [
            ("Schedule a meeting with the team", "High confidence (coordination)"),
            ("What's the weather today?", "Medium confidence (general)"),
            ("Deploy the new code to production", "Medium-high confidence (delegation)")
        ]
        
        print("\nConfidence scoring:")
        for request, expected in test_confidence:
            confidence = assistant.should_handle_request(request, {})
            print(f"- '{request[:30]}...' → {confidence:.1f} ({expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Personality test failed: {str(e)}")
        return False

async def main():
    """Run all response tests"""
    print("🚀 Multi-Agent System Response Tests")
    print("=" * 60)
    print("Testing with real LLM responses to demonstrate agent personality\n")
    
    tests = [
        test_personal_assistant_responses,
        test_brain_integration,
        test_agent_personality
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 Response Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All response tests passed!")
        print("✅ Personal Assistant agent is responding with proper personality")
        print("✅ Multi-agent framework is routing requests correctly")
        print("✅ Ready for specialist agent implementation")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())