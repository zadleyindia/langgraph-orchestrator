# LangGraph Orchestrator - Personal AI Brain

The intelligent orchestration layer for your Personal AI Brain system. This component sits between your voice/text interfaces and your 35+ MCP servers, providing intelligent routing, workflow planning, and execution coordination.

## Architecture Position

```
Voice/WhatsApp/Web → API Gateway → LangGraph Orchestrator → Supergateway → MCP Servers
```

## Features

- **Multi-Agent Architecture**: 5 specialist agents coordinated by Personal Assistant
- **Intent Analysis**: Understands what users want to accomplish
- **Workflow Planning**: Creates multi-step execution plans
- **Tool Orchestration**: Coordinates multiple MCP servers
- **Context Management**: Maintains conversation state and memory
- **Memory Integration**: Connected to Knowledge Graph MCP server
- **Error Handling**: Graceful failures and recovery
- **Multi-Interface Support**: Voice, WebSocket, WhatsApp, and REST API

## Quick Start

1. **Setup Environment**
   ```bash
   cd /Users/mohit/claude/claude-code/langgraph-orchestrator
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Orchestrator**
   ```bash
   python main.py
   ```

4. **Test the API**
   ```bash
   curl -X POST http://localhost:8000/orchestrate \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Check my GitHub PRs and send summary to team",
       "user_id": "test_user",
       "interface": "api"
     }'
   ```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LLM operations
- `SUPERGATEWAY_URL`: URL of your Supergateway service (default: http://localhost:3000)
- `ORCHESTRATOR_PORT`: Port for the orchestrator service (default: 8000)

### MCP Server Configuration

The orchestrator knows about these MCP servers:

- **Communication**: WhatsApp, Slack, Email, Telegram
- **Development**: GitHub, Docker, Jenkins, Terminal
- **Data**: BigQuery, Shopify, AWS, Google Sheets
- **Intelligence**: Memory, Search, Analysis

Add new servers in `orchestrator/nodes/executor.py`:

```python
self.tool_mapping["new_tool"] = {
    "server": "new-mcp-server",
    "methods": {
        "action_name": "mcp_method_name"
    }
}
```

## Agent Architecture

The orchestrator now uses a **multi-agent architecture** with 5 specialist agents:

1. **Personal Assistant** (Primary) - Coordinates all agents and handles general requests
2. **Data Analyst** - Statistical analysis, reporting, trends, and data visualization
3. **HR Director** - Talent acquisition, performance management, employee relations
4. **Dev Lead** - Software architecture, code review, deployment, technical mentoring
5. **Operations Manager** - Project management, resource allocation, process optimization

All agents are connected to the **Memory MCP server** for persistent knowledge storage.

## API Reference

### Core Orchestration

#### POST /orchestrate
Execute a user request through the orchestration engine.

**Request:**
```json
{
  "message": "User's natural language request",
  "user_id": "unique_user_identifier",
  "interface": "voice|whatsapp|websocket|api",
  "session_id": "optional_session_id",
  "context": {"optional": "context_data"}
}
```

**Response:**
```json
{
  "response": "Generated response for the user",
  "actions_taken": [
    {
      "tool": "github",
      "action": "list_prs",
      "result": "...",
      "success": true,
      "timestamp": "2025-07-12T10:30:00Z"
    }
  ],
  "context_updated": true,
  "session_id": "session_12345"
}
```

### Voice Interface

#### POST /voice/process
Process voice request from FastRTC.

**Request:**
```json
{
  "transcript": "User's voice transcription",
  "user_id": "mohit",
  "interface": "voice",
  "session_id": "voice_session_123",
  "context": {"audio_input": true}
}
```

#### GET /voice/status
Get voice interface status and session information.

### WebSocket Interface

#### WebSocket /ws/{user_id}
Real-time communication endpoint.

**Message Types:**
- `text` - Text message
- `voice` - Voice transcript
- `command` - System commands (status, clear, agents)
- `status` - Status request

**Example Message:**
```json
{
  "type": "text",
  "content": "Hello, how are you?",
  "user_id": "mohit",
  "interface": "websocket"
}
```

#### GET /ws/status
Get WebSocket connection status.

### WhatsApp Webhook

#### POST /webhook/whatsapp
Handle WhatsApp webhook messages.

**Supports:**
- Text messages
- Voice messages (with transcription)
- Image messages (with vision processing)
- Document messages (with content extraction)

#### GET /webhook/status
Get webhook handler status.

#### POST /webhook/whatsapp/clear/{phone_number}
Clear WhatsApp session for specific phone number.

### System Endpoints

#### GET /health
Check orchestrator health.

#### GET /status
Get detailed status including MCP server connectivity and agent information.

## Workflow Examples

### Simple Request
```
User: "Send a WhatsApp to John saying hello"

Flow:
1. Intent Analysis → communication
2. Planning → [WhatsApp: send_message]
3. Execution → WhatsApp MCP call
4. Response → "Message sent to John"
```

### Complex Request
```
User: "Check my GitHub PRs and send summary to team"

Flow:
1. Intent Analysis → complex (github + whatsapp)
2. Planning → [GitHub: list_prs, Analysis: summarize, Memory: get_team, WhatsApp: send_message]
3. Execution → Execute each step in sequence
4. Response → "Found 3 PRs, sent summary to team"
```

## Integration with Existing Components

### With Samantha (Voice Interface)

Samantha sends requests to LangGraph instead of directly to MCP servers:

```javascript
// In Samantha's tool configuration
const tools = [{
  type: "function",
  function: {
    name: "orchestrate_request",
    description: "Execute any request through the AI brain",
    parameters: {
      type: "object",
      properties: {
        message: { type: "string" },
        interface: { type: "string", enum: ["voice"] }
      }
    }
  }
}];

// Implementation
async function orchestrate_request({ message, interface = "voice" }) {
  const response = await fetch('http://localhost:8000/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, interface, user_id: "voice_user" })
  });
  return await response.json();
}
```

### With WhatsApp

WhatsApp webhook sends messages to orchestrator:

```python
@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request):
    message = extract_message(request)
    user_id = extract_user_id(request)
    
    result = await orchestrate({
        "message": message,
        "user_id": user_id,
        "interface": "whatsapp"
    })
    
    # Send response back via WhatsApp
    await send_whatsapp_reply(user_id, result["response"])
```

## Development

### Adding New Nodes

1. Create new node in `orchestrator/nodes/`
2. Add to the graph in `orchestrator/brain.py`
3. Update state model if needed

### Adding New Tools

1. Add tool mapping in `orchestrator/nodes/executor.py`
2. Test with your Supergateway
3. Update documentation

### Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  orchestrator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPERGATEWAY_URL=http://supergateway:3000
    depends_on:
      - supergateway
```

## Monitoring

The orchestrator provides built-in monitoring:

- **Health checks**: `/health` endpoint
- **Status monitoring**: `/status` endpoint  
- **Error tracking**: Errors logged in conversation state
- **Performance metrics**: Response times and success rates

## Next Steps

1. **Start the orchestrator** and test basic functionality
2. **Integrate with Samantha** for voice orchestration
3. **Add WhatsApp integration** for mobile access
4. **Expand tool mappings** for your specific MCP servers
5. **Deploy to production** with monitoring and scaling

The orchestrator is designed to be the intelligent brain that coordinates all your AI capabilities, making your Personal AI Brain truly unified and powerful! 🧠⚡