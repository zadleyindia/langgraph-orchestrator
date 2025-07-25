# Personal AI Brain - Deployment Guide

This guide covers the complete deployment of the Personal AI Brain system with integrated memory capabilities.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Supabase account with PostgreSQL database
- Git access to the repositories

### 1. Environment Setup

```bash
# Clone the repositories (if not already done)
cd /Users/mohit/claude/claude-code
git pull  # Update existing repos

# Navigate to orchestrator
cd langgraph-orchestrator

# Copy environment template
cp .env.template .env

# Edit .env with your credentials
nano .env  # or your preferred editor
```

**Required environment variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
- `DATABASE_PASSWORD`: Your database password

### 2. Automated Setup

```bash
# Run the automated setup script
./scripts/setup.sh
```

This script will:
- Validate your environment configuration
- Build the supergateway-memory container
- Start all services with health checks
- Run basic connectivity tests

### 3. Manual Setup (Alternative)

If you prefer manual control:

```bash
# Build memory container
cd ../Memory-Strategy-Evaluation/docker/supergateway-memory
./build.sh

# Return to orchestrator
cd ../../../langgraph-orchestrator

# Start services
docker-compose up -d
```

## 🧪 Testing

### Automated Integration Tests

```bash
# Run comprehensive integration tests
./scripts/test-integration.sh
```

### Manual Testing

```bash
# Test basic memory storage
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Remember that I like morning meetings", "user_id": "test_user"}'

# Test memory retrieval
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you know about my preferences?", "user_id": "test_user"}'

# Test direct memory service
curl -X POST http://localhost:3003/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "smart_memory",
      "arguments": {
        "action": "search",
        "query": "meeting preferences"
      }
    },
    "id": "test_001"
  }'
```

## 📊 Monitoring

### Service Health Checks

```bash
# Check all services
curl http://localhost:8000/health  # Orchestrator
curl http://localhost:3003/health  # Memory service

# View service status
docker-compose ps

# View logs
docker-compose logs -f supergateway-memory
docker-compose logs -f langgraph-orchestrator
```

### Performance Monitoring

The system includes optional monitoring stack:

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access monitoring dashboards
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
```

## 🔧 Configuration

### Service Ports

- **LangGraph Orchestrator**: 8000
- **Memory Service (Supergateway)**: 3003
- **PostgreSQL (dev)**: 5432
- **pgAdmin (dev)**: 5050
- **Prometheus**: 9090
- **Grafana**: 3000

### Environment Profiles

```bash
# Development (includes database)
docker-compose --profile development up -d

# Production (external database)
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d

# With admin tools
docker-compose --profile admin up -d
```

### Memory Service Configuration

Key environment variables for the memory service:

```env
# Performance tuning
MAX_OBSERVATIONS_PER_ENTITY=1000
MAX_SEARCH_RESULTS=50
SUPERGATEWAY_SESSION_TIMEOUT=300000

# Feature flags
ENABLE_SMART_UPDATES=true
ENABLE_RPC_CACHE=true
ENABLE_AGENT_CONTEXT=true

# Security
REQUIRE_SSL=false  # Set to true in production
```

## 🛠️ Troubleshooting

### Common Issues

**1. Memory service not starting**
```bash
# Check database connectivity
docker-compose logs supergateway-memory | grep -i error

# Verify environment variables
docker-compose exec supergateway-memory env | grep -E "(DATABASE|SUPABASE|OPENAI)"

# Test database connection manually
docker-compose exec supergateway-memory node -e "
const { Pool } = require('pg');
const pool = new Pool({connectionString: process.env.DATABASE_URL});
pool.connect().then(() => console.log('DB OK')).catch(console.error);
"
```

**2. Orchestrator not connecting to memory**
```bash
# Check network connectivity
docker-compose exec langgraph-orchestrator curl http://supergateway-memory:3003/health

# Verify service discovery
docker-compose exec langgraph-orchestrator nslookup supergateway-memory
```

**3. Slow memory operations**
```bash
# Check database performance
docker-compose logs supergateway-memory | grep -i "slow\|timeout"

# Monitor resource usage
docker stats
```

### Health Check Commands

```bash
# Full system health check
./scripts/test-integration.sh

# Individual service checks
curl http://localhost:8000/health
curl http://localhost:3003/health

# Database connectivity
docker-compose exec supergateway-memory node -e "
const db = require('./dist/src/services/databaseService.js');
db.databaseService.initialize().then(() => console.log('DB connected')).catch(console.error);
"
```

## 🔄 Updates and Maintenance

### Updating the System

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Rolling update
docker-compose up -d --force-recreate
```

### Database Migrations

```bash
# Check migration status
docker-compose exec supergateway-memory npm run check-migration

# Run migrations manually if needed
docker-compose exec supergateway-memory npm run migrate
```

### Backup and Recovery

```bash
# Backup database
docker-compose exec postgres-dev pg_dump -U postgres knowledge_graph > backup.sql

# Restore database
docker-compose exec -T postgres-dev psql -U postgres knowledge_graph < backup.sql
```

## 🌐 Production Deployment

### Security Checklist

- [ ] Enable SSL (`REQUIRE_SSL=true`)
- [ ] Use strong database passwords
- [ ] Implement API rate limiting
- [ ] Configure proper firewall rules
- [ ] Use secrets management (not .env files)
- [ ] Enable container security scanning

### Scaling Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  langgraph-orchestrator:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
  
  supergateway-memory:
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Kubernetes Deployment

For production Kubernetes deployment, see the `kubernetes/` directory (to be created in Phase 4).

## 📞 Support

### Logs Location

- **Application logs**: `./logs/`
- **Container logs**: `docker-compose logs <service>`

### Debugging

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
docker-compose up -d

# Access container shell
docker-compose exec supergateway-memory sh
docker-compose exec langgraph-orchestrator bash

# Check resource usage
docker stats
docker system df
```

For additional support, check the implementation documentation in the `Memory-Strategy-Evaluation/` directory.