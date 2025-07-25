# MCP Server Connection Methods

✅ **Yes, Docker can absolutely be used to connect to the MCP server!**

You now have **TWO working connection methods** for the Memory MCP Server:

## Method 1: Direct stdio (Claude Desktop)
- **How**: Direct Node.js process communication via stdin/stdout
- **Used by**: Claude Desktop, Claude Code
- **Configuration**: `/Users/mohit/Library/Application Support/Claude/claude_desktop_config.json`
- **Status**: ✅ **WORKING** - Successfully handles all memory operations
- **Logs**: `/Users/mohit/Library/Logs/Claude/mcp-server-memory.log`

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/Users/mohit/claude/conversation-persistence-mcp/dist/src/index.js"],
      "env": {
        "SUPABASE_URL": "https://lohggakrufbclcccamaj.supabase.co",
        "SUPABASE_SCHEMA": "kg",
        "SUPABASE_DB_PASSWORD": "mP*t^xfEr2o*@!F",
        "OPENAI_API_KEY": "sk-proj-...",
        "USE_CONSOLIDATED_TOOLS": "true"
      }
    }
  }
}
```

## Method 2: Docker HTTP/SSE (LangGraph Agents)
- **How**: HTTP/Server-Sent Events via Supergateway bridge
- **Used by**: LangGraph agents, external applications, web interfaces
- **Endpoint**: `http://localhost:3003/mcp`
- **Status**: ✅ **WORKING** - Container running and responding to requests
- **Container**: `supergateway-memory-running`

```bash
# Container Status
$ docker ps | grep supergateway-memory
656b342b690c   supergateway-memory:latest   "./entrypoint.sh"   Up 10 minutes   0.0.0.0:3003->3003/tcp

# Test Initialize
$ curl -X POST http://localhost:3003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {...}, "id": 1}'

# Response:
event: message
data: {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"knowledge-graph-memory-mcp","version":"1.0.0"}},"jsonrpc":"2.0","id":1}
```

## Key Differences

| Aspect | Direct stdio (Claude Desktop) | Docker HTTP/SSE (LangGraph) |
|--------|------------------------------|----------------------------|
| **Protocol** | JSON-RPC over stdin/stdout | JSON-RPC over HTTP with SSE |
| **Concurrency** | Single connection | Multiple concurrent connections |
| **Use Case** | Interactive AI conversations | Programmatic agent access |
| **Setup** | Claude Desktop config | Docker container + HTTP client |
| **Performance** | Faster (direct process) | Slightly slower (network overhead) |
| **Scalability** | Limited to one client | Multiple clients supported |

## Same Memory Database
Both methods access the **same Supabase knowledge graph database**:
- **798 entities** and **731 relations** stored
- **Semantic search** with embeddings
- **6 consolidated smart tools**: memory, intelligence, session, maintenance, orchestration, natural_query

## Usage Examples

### LangGraph Memory Client
```python
# /Users/mohit/claude/claude-code/langgraph-orchestrator/memory_client.py
async def search_memories(self, query: str, limit: int = 10, entity_type: str = None):
    result = await self._call_mcp_tool("smart_memory", {
        "action": "search",
        "query": query,
        "options": {"limit": limit, "entityType": entity_type}
    })
    return result
```

### Personal Assistant Agent
```python
# Uses Docker HTTP connection for memory operations
memory_result = await self.memory_client.search_memories(
    query="François Müller insurance AI/ML",
    limit=5
)
```

## Next Steps

You can now:
1. **Connect voice interfaces** to the LangGraph agents (which use Docker method)
2. **Scale to multiple concurrent users** via the HTTP endpoint
3. **Deploy to production** using the Docker container approach
4. **Keep Claude Desktop working** simultaneously via the direct connection

Both connection methods give you full access to the same powerful memory capabilities! 🧠✨