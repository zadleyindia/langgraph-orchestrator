# Docker Configurations

This directory contains Docker configurations for different services:

## Services

### orchestrator/
The main LangGraph orchestrator service (Python-based multi-agent system)
- Standalone deployment
- Connects to external memory service
- Port: 8000

### Usage

To run the orchestrator:
```bash
cd orchestrator
docker-compose up -d
```

## Notes
- Memory service (conversation-persistence-mcp) is deployed separately
- Update MEMORY_SERVICE_URL in docker-compose.yml to point to your memory service
- Each service has its own Docker configuration for independent deployment