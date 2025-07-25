"""
Tool Execution Node - Executes planned steps using MCP servers
"""

from typing import Dict, Any
from ..state import ConversationState
from ..clients.supergateway_client import SupergatewayClient

class ToolExecutor:
    """Executes tools via Supergateway"""
    
    def __init__(self, supergateway: SupergatewayClient):
        self.supergateway = supergateway
        
        # Map of tool names to MCP server configurations
        self.tool_mapping = {
            "whatsapp": {
                "server": "whatsapp-mcp-server",
                "methods": {
                    "send_message": "send_message",
                    "get_contacts": "get_contacts",
                    "get_groups": "get_groups"
                }
            },
            "github": {
                "server": "github",
                "methods": {
                    "list_prs": "list_pull_requests",
                    "create_issue": "create_issue",
                    "get_repo": "get_repository"
                }
            },
            "memory": {
                "server": "conversation-persistence-mcp",
                "methods": {
                    "store": "store_memory",
                    "retrieve": "retrieve_memory",
                    "search": "search_knowledge_graph"
                }
            },
            "terminal": {
                "server": "terminal",
                "methods": {
                    "execute": "execute_command",
                    "list_files": "list_directory"
                }
            },
            "search": {
                "server": "brave-search",
                "methods": {
                    "web_search": "search",
                    "news_search": "news_search"
                }
            },
            "filesystem": {
                "server": "filesystem",
                "methods": {
                    "list_files": "list_directory",
                    "read_file": "read_file",
                    "search_files": "search_files"
                }
            }
        }
    
    async def execute(self, state: ConversationState) -> ConversationState:
        """Execute all planned steps"""
        
        for i, step in enumerate(state.plan):
            if state.current_step > i:
                continue  # Skip already completed steps
            
            try:
                # Parse the step
                tool_info = self._parse_step(step)
                tool_name = tool_info["tool"]
                action = tool_info["action"]
                params = tool_info["params"]
                
                # Execute the tool
                result = await self._execute_tool(tool_name, action, params, state)
                
                # Store result
                state.tool_results[f"step_{i}"] = result
                state.add_action(tool_name, action, result, success=True)
                
                # Update current step
                state.current_step = i + 1
                
            except Exception as e:
                error_msg = f"Step {i} failed: {str(e)}"
                state.add_error(error_msg)
                state.add_action(tool_info.get("tool", "unknown"), 
                               tool_info.get("action", "unknown"), 
                               str(e), success=False)
                
                # Continue with next step for now
                state.current_step = i + 1
        
        return state
    
    def _parse_step(self, step: str) -> Dict[str, Any]:
        """Parse a plan step into tool, action, and parameters"""
        
        # Expected format: "[Tool]: [Action] - [Parameters/Details]"
        try:
            if ':' in step:
                tool_part, action_part = step.split(':', 1)
                tool_name = tool_part.strip().lower()
                
                if ' - ' in action_part:
                    action, params_str = action_part.split(' - ', 1)
                    action = action.strip()
                    params = {"details": params_str.strip()}
                else:
                    action = action_part.strip()
                    params = {}
                
                return {
                    "tool": tool_name,
                    "action": action,
                    "params": params
                }
            else:
                # Fallback parsing
                return {
                    "tool": "memory",
                    "action": "store",
                    "params": {"content": step}
                }
        except Exception:
            return {
                "tool": "memory",
                "action": "store", 
                "params": {"content": step}
            }
    
    async def _execute_tool(self, tool_name: str, action: str, params: Dict[str, Any], 
                          state: ConversationState) -> Any:
        """Execute a specific tool action"""
        
        if tool_name not in self.tool_mapping:
            return f"Tool {tool_name} not available"
        
        tool_config = self.tool_mapping[tool_name]
        server_name = tool_config["server"]
        
        # Map action to method name
        method_name = tool_config["methods"].get(action.lower(), action)
        
        # Prepare parameters based on tool and action
        mcp_params = self._prepare_params(tool_name, action, params, state)
        
        # Execute via Supergateway
        result = await self.supergateway.execute_mcp(server_name, method_name, mcp_params)
        
        return result
    
    def _prepare_params(self, tool_name: str, action: str, params: Dict[str, Any], 
                       state: ConversationState) -> Dict[str, Any]:
        """Prepare parameters for MCP server calls"""
        
        if tool_name == "whatsapp":
            if "send_message" in action.lower():
                return {
                    "to": params.get("to", ""),
                    "message": params.get("message", state.current_message)
                }
            else:
                return params
                
        elif tool_name == "github":
            if "list_prs" in action.lower() or "pull_request" in action.lower():
                return {
                    "owner": params.get("owner", state.context.get("github_owner", "")),
                    "repo": params.get("repo", state.context.get("github_repo", ""))
                }
            else:
                return params
                
        elif tool_name == "memory":
            return {
                "content": params.get("content", state.current_message),
                "user_id": state.user_id,
                "session_id": state.session_id
            }
            
        elif tool_name == "filesystem":
            if "list" in action.lower():
                # Extract path from params or use desktop as default
                path = params.get("path", "/Users/mohit/Desktop")
                if "desktop" in state.current_message.lower():
                    path = "/Users/mohit/Desktop"
                elif "downloads" in state.current_message.lower():
                    path = "/Users/mohit/Downloads"
                elif "documents" in state.current_message.lower():
                    path = "/Users/mohit/Documents"
                return {"path": path}
            elif "read" in action.lower():
                return {"path": params.get("path", "")}
            else:
                return params
            
        else:
            return params