"""
Supergateway Client - Interface to your existing Supergateway
"""

import httpx
import os
from typing import Dict, Any, Optional

class SupergatewayClient:
    """Client for communicating with Supergateway"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("SUPERGATEWAY_URL", "http://localhost:3000")
        self.timeout = 30.0
    
    async def execute_mcp(self, server: str, method: str, params: Dict[str, Any]) -> Any:
        """Execute an MCP server method via Supergateway"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/execute",
                    json={
                        "server": server,
                        "method": method,
                        "params": params
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "success": False
                    }
                    
        except httpx.TimeoutException:
            return {
                "error": f"Timeout executing {server}.{method}",
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Failed to execute {server}.{method}: {str(e)}",
                "success": False
            }
    
    async def list_servers(self) -> Dict[str, Any]:
        """List available MCP servers"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/servers")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}", "servers": []}
                    
        except Exception as e:
            return {"error": str(e), "servers": []}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Supergateway health"""
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "url": self.base_url,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "url": self.base_url,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "status": "unreachable",
                "url": self.base_url,
                "error": str(e)
            }
    
    async def get_server_info(self, server: str) -> Dict[str, Any]:
        """Get information about a specific MCP server"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/servers/{server}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}", "info": {}}
                    
        except Exception as e:
            return {"error": str(e), "info": {}}