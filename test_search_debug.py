#!/usr/bin/env python3
"""Debug test to see actual search response"""

import asyncio
import json
from memory_client import LangGraphMemoryClient

async def test_search_debug():
    print("Testing memory search with debug output...")
    
    async with LangGraphMemoryClient() as client:
        # Direct call to see raw response
        result = await client._call_mcp_tool("smart_memory", {
            "action": "search",
            "query": "mohit birthday",
            "options": {
                "limit": 5
            }
        })
        
        print("\nRaw search response:")
        print(json.dumps(result, indent=2))
        
        # Try different search query
        result2 = await client._call_mcp_tool("smart_memory", {
            "action": "find",
            "query": "mohit",
            "options": {
                "limit": 5
            }
        })
        
        print("\nAlternative search response:")
        print(json.dumps(result2, indent=2))

if __name__ == "__main__":
    asyncio.run(test_search_debug())