#!/bin/bash

# Personal AI Brain - Setup Script
# Automates the initial setup and deployment

set -e

echo "🧠 Personal AI Brain - Setup Script"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file with your actual credentials before continuing."
    echo "   Required: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
    read -p "Press Enter when you've updated .env file..."
fi

# Validate required environment variables
echo "🔍 Validating environment configuration..."
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-proj-your-openai-api-key-here" ]; then
    echo "❌ OPENAI_API_KEY not configured in .env"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://your-project.supabase.co" ]; then
    echo "❌ SUPABASE_URL not configured in .env"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ] || [ "$SUPABASE_SERVICE_ROLE_KEY" = "your-supabase-service-role-key" ]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY not configured in .env"
    exit 1
fi

echo "✅ Environment configuration validated"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs/memory
mkdir -p monitoring/grafana

# Build the memory container first
echo "🏗️  Building supergateway-memory container..."
cd ../Memory-Strategy-Evaluation/docker/supergateway-memory
./build.sh
cd ../../../langgraph-orchestrator

# Build and start services
echo "🚀 Building and starting services..."
docker-compose build
docker-compose up -d supergateway-memory

# Wait for memory service to be healthy
echo "⏳ Waiting for memory service to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:3003/health > /dev/null 2>&1; then
        echo "✅ Memory service is healthy!"
        break
    fi
    
    echo "   Attempt $((attempt + 1))/$max_attempts - waiting for memory service..."
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Memory service failed to start within timeout"
    echo "📋 Checking logs:"
    docker-compose logs supergateway-memory
    exit 1
fi

# Start the orchestrator
echo "🧠 Starting LangGraph orchestrator..."
docker-compose up -d langgraph-orchestrator

# Wait for orchestrator to be healthy
echo "⏳ Waiting for orchestrator to be ready..."
max_attempts=20
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ LangGraph orchestrator is healthy!"
        break
    fi
    
    echo "   Attempt $((attempt + 1))/$max_attempts - waiting for orchestrator..."
    sleep 3
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Orchestrator failed to start within timeout"
    echo "📋 Checking logs:"
    docker-compose logs langgraph-orchestrator
    exit 1
fi

# Run basic connectivity tests
echo "🧪 Running connectivity tests..."

# Test memory service
echo "   Testing memory service..."
if curl -s http://localhost:3003/health | grep -q "healthy"; then
    echo "   ✅ Memory service responding correctly"
else
    echo "   ❌ Memory service health check failed"
fi

# Test orchestrator
echo "   Testing orchestrator..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "   ✅ Orchestrator responding correctly"
else
    echo "   ❌ Orchestrator health check failed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Test the system: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello, remember that I like coffee\"}'"
echo "   2. View logs: docker-compose logs -f"
echo "   3. Stop services: docker-compose down"
echo ""
echo "🌐 Service URLs:"
echo "   - LangGraph Orchestrator: http://localhost:8000"
echo "   - Memory Service: http://localhost:3003"
echo "   - pgAdmin (dev): http://localhost:5050 (if using development profile)"
echo ""