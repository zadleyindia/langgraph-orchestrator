# MCP SSE Integration Learning Guide

## Overview
This document captures key learnings from attempting to integrate MCP (Model Context Protocol) tools with SSE (Server-Sent Events) protocol, specifically for connecting to the AI Brain Memory service.

## Key Resources & URLs

### Official Documentation
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Protocol Docs**: https://modelcontextprotocol.io/docs/concepts/transports
- **MCP Quickstart Client**: https://modelcontextprotocol.io/quickstart/client#python
- **Supergateway**: https://github.com/supercorp-ai/supergateway

### Example Implementations
- **SSE MCP Pattern**: https://github.com/sidharthrajaram/mcp-sse
- **MCP SSE Client Example**: https://github.com/slavashvets/mcp-http-client-example

## Architecture Understanding

### 1. Claude Desktop Configuration
```json
"ai-brain-memory-production": {
  "command": "npx",
  "args": [
    "-y",
    "supergateway",
    "--sse",
    "https://mcp-memory-7z7id4apjq-el.a.run.app/mcp"
  ]
}
```
- Runs Supergateway locally via npx
- Connects to production MCP server at Google Cloud Run
- Converts between stdio (local) and SSE (remote) transports

### 2. MCP Transport Types
- **stdio**: Standard input/output (used by Claude Desktop locally)
- **SSE**: Server-Sent Events (deprecated, being replaced by Streamable HTTP)
- **WebSocket**: Real-time bidirectional communication
- **Streamable HTTP**: New standard replacing SSE

### 3. Supergateway Role
- Acts as a transport bridge/proxy
- Converts stdio ↔ SSE/WebSocket/HTTP
- Enables local clients to connect to remote MCP servers
- Handles session management and protocol translation

## Integration Approaches Attempted

### 1. Direct HTTP (Failed)
- Tried posting to `/mcp` endpoint with custom JSON format
- Result: 404 errors - endpoint doesn't accept direct HTTP

### 2. JSON-RPC with sessionId (Failed)
- Used proper JSON-RPC 2.0 format with sessionId query parameter
- Result: "No active SSE connection" - requires SSE handshake first

### 3. SSE Client Implementation (Incomplete)
- Created custom SSE client to establish connection first
- Challenge: Complex handshake and session management required

### 4. MCP Python SDK (Recommended)
```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client(url) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use session.call_tool()
```

## Key Learnings

### 1. Production Service Architecture
- Production URL is NOT a Supergateway instance
- It's the actual MCP server requiring proper protocol
- Direct HTTP requests won't work without proper MCP handshake

### 2. Session Management
- SSE requires establishing connection before sending messages
- Sessions need unique IDs (sessionId parameter)
- Stateful connections maintained across requests

### 3. Authentication
- Production service may require authentication headers
- OAuth2 bearer tokens can be passed via Supergateway
- Direct connection attempts failed (possibly auth-related)

### 4. Local Development Setup
```bash
# Run Supergateway locally
npx -y supergateway \
  --stdio "command-to-run-mcp-server" \
  --port 5173 \
  --outputTransport sse

# Or connect to remote SSE
npx -y supergateway \
  --sse "https://remote-mcp-server/mcp" \
  --outputTransport stdio
```

## Working Solution (Temporary)
Created `memory_client_direct.py` with simulated responses to allow development to continue while figuring out proper MCP connection.

## Next Steps for Proper Integration

1. **Option 1: Local Supergateway**
   - Run Supergateway locally like Claude Desktop
   - Connect using stdio transport (simpler)
   - Most reliable, matches Claude's approach

2. **Option 2: Direct MCP Connection**
   - Figure out authentication for production
   - Use MCP SDK's SSE client properly
   - More complex but no intermediate proxy

3. **Option 3: Custom MCP Server**
   - Create local MCP server that wraps production
   - Implement proper MCP protocol
   - Most control but most work

## Debugging Commands

```bash
# Test direct connection
curl -X POST https://mcp-memory-7z7id4apjq-el.a.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Run Supergateway with debug logging
npx -y supergateway --logLevel debug --sse URL

# Check MCP SDK components
python -c "import mcp.client.sse; print(dir(mcp.client.sse))"
```

## Important Notes
- SSE transport is being deprecated in favor of Streamable HTTP
- MCP is a stateful protocol requiring persistent connections
- The Memory service already works via Claude's MCP tools (mcp__ai-brain-memory__*)
- For MVP, using simulated client allows progress while solving connection issues