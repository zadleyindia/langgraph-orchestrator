#!/usr/bin/env python3
"""Quick test to verify search functionality is fixed"""

import asyncio
from memory_client import LangGraphMemoryClient

async def test_search():
    print("Testing memory search fix...")
    
    async with LangGraphMemoryClient() as client:
        # Test 1: Store a memory
        print("\n1. Storing test memory...")
        success = await client.store_memory(
            agent_id="test_search_fix",
            content="Mohit's birthday is December 15th",
            entity_type="personal_info"
        )
        print(f"   Storage: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Wait a moment for processing
        await asyncio.sleep(1)
        
        # Test 2: Search for the memory
        print("\n2. Searching for 'mohit birthday'...")
        results = await client.search_memories("mohit birthday", limit=5)
        print(f"   Search Results: Found {len(results)} results")
        
        if results:
            print("   ✅ SEARCH FIXED!")
            for i, result in enumerate(results[:3]):
                print(f"   Result {i+1}: {result.get('entity_name', 'Unknown')}")
        else:
            print("   ❌ SEARCH STILL BROKEN")
            
        return len(results) > 0

if __name__ == "__main__":
    success = asyncio.run(test_search())
    exit(0 if success else 1)