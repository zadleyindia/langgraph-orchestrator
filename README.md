# LangGraph Orchestrator - Multi-Agent AI System

A flexible, multi-tenant AI orchestration system built with LangGraph for managing multiple specialized AI agents.

## Features

- **Multi-Tenant Architecture**: Support for different company contexts (personal, company_a, company_b)
- **Extensible Agent Framework**: Not limited to fixed agents - easily add new specialized agents
- **Memory Integration**: Context-aware memory system with multi-tenant support
- **Flexible LLM Configuration**: Easy switching between OpenAI, Anthropic, Google AI models

## Architecture

```
orchestrator/
├── agents/           # Specialized AI agents
├── llm/             # LLM configuration system
├── clients/         # External service clients (Memory, etc.)
├── api/             # API interfaces (HTTP, WebSocket, Voice)
├── nodes/           # LangGraph processing nodes
└── brain.py         # Main orchestrator logic
```

## Setup

1. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Create `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_key_here
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4
   ENABLE_MEMORY=true
   ```

3. **Run tests**:
   ```bash
   python test_memory_simple.py  # Test memory operations
   python test_personal_assistant_memory.py  # Test full integration
   ```

## Agents

- **Personal Assistant**: Primary coordinator, handles general requests
- **Data Analyst**: Data analysis and reporting (coming soon)
- **HR Director**: HR and team management (coming soon)
- **Dev Lead**: Technical development tasks (coming soon)
- **Operations Manager**: Operations and project management (coming soon)

## Memory Integration

Currently using a simulated memory client for development. Production options:
- Local Supergateway connection
- Direct MCP connection (requires auth)
- Keep simulated client for MVP

## Next Steps

1. Complete WhatsApp integration
2. Set up production memory connection
3. Implement remaining specialized agents
4. Add more tool integrations

## Development

To switch LLM providers:
```python
from orchestrator.llm import switch_provider
switch_provider("anthropic", "claude-3-opus-20240229")
```

## Status

- ✅ Memory integration (simulated)
- ✅ Multi-tenant support
- ✅ Flexible LLM configuration
- ✅ Personal Assistant agent
- 🔄 WhatsApp integration (next)
- 📅 Additional agents (planned)