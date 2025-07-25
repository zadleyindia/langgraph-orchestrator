#!/bin/bash

# Integration Test Script
# Tests the complete memory integration flow

set -e

echo "🧪 Personal AI Brain - Integration Tests"
echo "======================================="

# Check if services are running
echo "🔍 Checking service health..."

if ! curl -f http://localhost:3003/health > /dev/null 2>&1; then
    echo "❌ Memory service is not running. Please start with: docker-compose up -d"
    exit 1
fi

if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Orchestrator service is not running. Please start with: docker-compose up -d"
    exit 1
fi

echo "✅ All services are healthy"

# Test 1: Basic memory storage
echo ""
echo "📝 Test 1: Basic memory storage"
response=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Remember that I prefer morning meetings and like coffee", "user_id": "test_user"}')

if echo "$response" | grep -q "success\|remember\|stored"; then
    echo "✅ Memory storage test passed"
else
    echo "❌ Memory storage test failed"
    echo "Response: $response"
fi

# Test 2: Memory retrieval
echo ""
echo "🔍 Test 2: Memory retrieval"
response=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What do you know about my meeting preferences?", "user_id": "test_user"}')

if echo "$response" | grep -q "morning\|coffee\|meeting"; then
    echo "✅ Memory retrieval test passed"
else
    echo "❌ Memory retrieval test failed"
    echo "Response: $response"
fi

# Test 3: Direct memory service test
echo ""
echo "🧠 Test 3: Direct memory service test"
response=$(curl -s -X POST http://localhost:3003/mcp \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "smart_memory",
            "arguments": {
                "action": "search",
                "query": "coffee preferences",
                "__agent_context": {
                    "agent_id": "test_agent",
                    "agent_type": "personal_assistant",
                    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
                }
            }
        },
        "id": "test_001"
    }')

if echo "$response" | grep -q "result\|success"; then
    echo "✅ Direct memory service test passed"
else
    echo "❌ Direct memory service test failed"
    echo "Response: $response"
fi

# Test 4: Agent context preservation
echo ""
echo "👤 Test 4: Agent context preservation"
response=$(curl -s -X POST http://localhost:8000/agent/personal_assistant \
    -H "Content-Type: application/json" \
    -d '{"message": "Store information that John is the project manager", "user_id": "test_user"}')

if echo "$response" | grep -q "success\|stored\|remember"; then
    echo "✅ Agent context test passed"
else
    echo "❌ Agent context test failed"
    echo "Response: $response"
fi

# Test 5: Memory statistics
echo ""
echo "📊 Test 5: Memory statistics"
response=$(curl -s -X POST http://localhost:3003/mcp \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "smart_intelligence",
            "arguments": {
                "analysis_type": "graph_stats"
            }
        },
        "id": "stats_001"
    }')

if echo "$response" | grep -q "total_entities\|total_relations"; then
    echo "✅ Memory statistics test passed"
else
    echo "❌ Memory statistics test failed"
    echo "Response: $response"
fi

echo ""
echo "🎉 Integration tests completed!"
echo ""
echo "📋 Manual verification steps:"
echo "   1. Check memory service logs: docker-compose logs supergateway-memory"
echo "   2. Check orchestrator logs: docker-compose logs langgraph-orchestrator"
echo "   3. Test different agent types and memory operations"
echo ""