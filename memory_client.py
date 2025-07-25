"""
LangGraph Memory Client - Phase 2 Implementation
Connects LangGraph orchestrator to supergateway-memory service
"""

import asyncio
import json
import logging
import os
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryFact:
    entity_name: str
    entity_type: str
    observations: List[str]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "data": {"observations": self.observations},
            "metadata": self.metadata or {}
        }

@dataclass
class Relation:
    from_entity: str
    to_entity: str
    relation_type: str
    properties: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_entity,
            "to": self.to_entity,
            "relationType": self.relation_type,
            "properties": self.properties or {}
        }

class LangGraphMemoryClient:
    """
    Memory client for LangGraph agents to interact with Knowledge Graph MCP Server
    via supergateway HTTP bridge
    """
    
    def __init__(self, supergateway_url: str = "http://localhost:3004"):
        self.supergateway_url = supergateway_url
        self.mcp_endpoint = f"{supergateway_url}/mcp"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=aiohttp.ClientTimeout(total=float(os.getenv("MEMORY_TIMEOUT_MS", "500")) / 1000.0)
            )
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool via supergateway HTTP bridge"""
        await self._ensure_session()
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"langgraph_{datetime.now().timestamp()}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            logger.info(f"Calling MCP tool: {tool_name} with args: {json.dumps(arguments, indent=2)}")
            
            async with self.session.post(self.mcp_endpoint, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                
                # Handle both JSON and text/event-stream responses
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    result = await response.json()
                elif 'text/event-stream' in content_type:
                    # Handle server-sent events from supergateway
                    text_response = await response.text()
                    logger.info(f"SSE Response: {text_response[:200]}...")
                    
                    # Parse SSE format - look for JSON in data: lines
                    lines = text_response.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            json_data = line[6:]  # Remove 'data: ' prefix
                            if json_data and json_data != '[DONE]':
                                try:
                                    result = json.loads(json_data)
                                    break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        # If no valid JSON found, return raw response
                        result = {"content": text_response}
                else:
                    # Fallback: try to parse as JSON anyway
                    try:
                        result = await response.json()
                    except:
                        text_response = await response.text()
                        result = {"content": text_response}
                
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", result)
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            raise
    
    # === Memory Storage Operations ===
    
    async def store_memory(self, agent_id: str, content: str, entity_type: str = "observation") -> Dict[str, Any]:
        """Store a memory/observation for an agent"""
        memory_fact = MemoryFact(
            entity_name=f"{agent_id}_memory_{datetime.now().isoformat()}",
            entity_type=entity_type,
            observations=[content],
            metadata={
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "source": "langgraph_orchestrator"
            }
        )
        
        return await self._call_mcp_tool("smart_memory", {
            "action": "remember",
            "query": content,
            "entities": [memory_fact.entity_name],
            "data": memory_fact.to_dict()
        })
    
    async def store_entity(self, entity_name: str, entity_type: str, observations: List[str], 
                          agent_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store an entity with observations"""
        memory_fact = MemoryFact(
            entity_name=entity_name,
            entity_type=entity_type,
            observations=observations,
            metadata={
                "agent_context": agent_context or {},
                "timestamp": datetime.now().isoformat(),
                "source": "langgraph_orchestrator"
            }
        )
        
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "remember",
            "entities": [entity_name],
            "data": {
                "entityType": entity_type,
                "observations": observations,
                "metadata": {
                    "agent_context": agent_context or {},
                    "timestamp": datetime.now().isoformat(),
                    "source": "langgraph_orchestrator"
                }
            }
        })
    
    async def add_observation(self, entity_name: str, observation: str, 
                            agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Add an observation to an existing entity"""
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "remember",
            "entities": [entity_name],
            "query": observation,
            "data": {
                "metadata": {
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
        })
    
    # === Memory Retrieval Operations ===
    
    async def search_memories(self, query: str, limit: int = 10, 
                            entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search memories using semantic search"""
        # Use smart_memory tool in consolidated mode
        result = await self._call_mcp_tool("smart_memory", {
            "action": "search",
            "query": query,
            "options": {
                "limit": limit,
                "entityType": entity_type
            }
        })
        
        # Extract results from nested JSON response
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict) and "text" in first_content:
                    try:
                        # Parse the nested JSON string
                        import json
                        nested_data = json.loads(first_content["text"])
                        if "data" in nested_data and "content" in nested_data["data"]:
                            data_content = nested_data["data"]["content"]
                            if isinstance(data_content, list) and len(data_content) > 0:
                                inner_text = data_content[0].get("text", "")
                                # Parse the innermost JSON
                                inner_data = json.loads(inner_text)
                                if "results" in inner_data:
                                    return inner_data["results"]
                    except json.JSONDecodeError:
                        pass
        
        # Fallback for other response formats
        if isinstance(result, dict):
            if "entities" in result:
                return result.get("entities", [])
            elif "data" in result and isinstance(result["data"], list):
                return result["data"]
            elif "data" in result and isinstance(result["data"], dict):
                if "entities" in result["data"]:
                    return result["data"]["entities"]
                elif "results" in result["data"]:
                    return result["data"]["results"]
        
        return []
    
    async def get_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific entity by name"""
        # Use smart_memory tool in consolidated mode
        result = await self._call_mcp_tool("smart_memory", {
            "action": "get",
            "entities": [entity_name]
        })
        
        # Extract entity from the smart memory response
        if isinstance(result, dict):
            if "entities" in result:
                entities = result.get("entities", [])
                return entities[0] if entities else None
            elif "data" in result:
                if isinstance(result["data"], list) and len(result["data"]) > 0:
                    return result["data"][0]
                elif isinstance(result["data"], dict):
                    return result["data"]
        
        return None
    
    async def get_agent_memories(self, agent_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent memories for a specific agent"""
        return await self.search_memories(
            query=f"agent_id:{agent_id}",
            limit=limit
        )
    
    # === Relationship Operations ===
    
    async def create_relation(self, from_entity: str, to_entity: str, 
                            relation_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a relationship between entities"""
        relation = Relation(
            from_entity=from_entity,
            to_entity=to_entity,
            relation_type=relation_type,
            properties=properties or {}
        )
        
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "connect",
            "entities": [from_entity, to_entity],
            "data": {
                "relationType": relation_type,
                "properties": properties or {}
            }
        })
    
    async def explore_entity_network(self, entity_name: str, depth: int = 2, 
                                   max_entities: int = 20) -> Dict[str, Any]:
        """Explore the network around an entity"""
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "explore",
            "entities": [entity_name],
            "options": {
                "depth": depth,
                "maxEntities": max_entities
            }
        })
    
    async def find_connection_path(self, from_entity: str, to_entity: str) -> Dict[str, Any]:
        """Find connection path between two entities"""
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "path",
            "entities": [from_entity, to_entity]
        })
    
    # === Analysis Operations ===
    
    async def get_daily_brief(self) -> Dict[str, Any]:
        """Get daily brief of activities and insights"""
        return await self._call_mcp_tool("smart_memory", {
            "action": "daily",
            "query": "today"
        })
    
    async def get_timeline(self, entity_name: str) -> Dict[str, Any]:
        """Get timeline for an entity"""
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "timeline",
            "entities": [entity_name]
        })
    
    async def get_insights(self) -> Dict[str, Any]:
        """Generate insights from stored memories"""
        return await self._call_mcp_tool("smart_memory", {
            "action": "insights",
            "query": "generate patterns and insights"
        })
    
    # === Utility Operations ===
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        # Use smart_memory tool in consolidated mode
        return await self._call_mcp_tool("smart_memory", {
            "action": "stats"
        })
    
    async def health_check(self) -> bool:
        """Check if memory service is healthy"""
        try:
            await self.get_graph_stats()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    # === Context Management ===
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# === Test Functions ===

async def test_memory_client():
    """Test the memory client functionality"""
    async with LangGraphMemoryClient() as client:
        
        # Test health check
        print("Testing health check...")
        is_healthy = await client.health_check()
        print(f"Health check: {'✅ PASS' if is_healthy else '❌ FAIL'}")
        
        if not is_healthy:
            print("Memory service is not healthy. Exiting test.")
            return
        
        # Test storing memory
        print("\nTesting memory storage...")
        try:
            result = await client.store_memory(
                agent_id="test_agent",
                content="This is a test memory from LangGraph",
                entity_type="test_observation"
            )
            print(f"Store memory result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Store memory error: {str(e)}")
        
        # Test searching memories
        print("\nTesting memory search...")
        try:
            memories = await client.search_memories("test memory", limit=5)
            print(f"Found {len(memories)} memories")
            for memory in memories[:2]:  # Show first 2
                print(f"  - {memory.get('entity_name', 'Unknown')}: {memory.get('data', {}).get('observations', ['No observations'])[:1]}")
        except Exception as e:
            print(f"Search memories error: {str(e)}")
        
        # Test graph stats
        print("\nTesting graph stats...")
        try:
            stats = await client.get_graph_stats()
            print(f"Graph stats: {json.dumps(stats, indent=2)}")
        except Exception as e:
            print(f"Graph stats error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_memory_client())