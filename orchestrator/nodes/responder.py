"""
Response Generation Node - Creates user-friendly responses
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from ..state import ConversationState

class ResponseGenerator:
    """Generates appropriate responses based on execution results"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.response_prompt = PromptTemplate.from_template("""
You are generating a response for a Personal AI Brain system.

Original user message: "{message}"
User interface: {interface}
Intent: {intent}
Actions taken: {actions}
Tool results: {results}
Errors (if any): {errors}

Generate an appropriate response that:
1. Acknowledges what the user asked for
2. Summarizes what was done
3. Provides relevant results or information
4. Is appropriate for the interface ({interface})
5. Is friendly and conversational

If there were errors, acknowledge them but focus on what was accomplished.

Response format guidelines:
- Voice interface: Keep it concise and speakable
- WhatsApp: Use emojis and informal tone
- Web/API: More detailed and structured
- All interfaces: Be helpful and clear

Response:
""")
    
    async def generate(self, state: ConversationState) -> ConversationState:
        """Generate appropriate response"""
        
        try:
            # Prepare response data
            actions_summary = self._summarize_actions(state.actions_taken)
            results_summary = self._summarize_results(state.tool_results)
            errors_summary = self._summarize_errors(state.errors)
            
            # Format the prompt
            prompt = self.response_prompt.format(
                message=state.current_message,
                interface=state.interface,
                intent=state.intent,
                actions=actions_summary,
                results=results_summary,
                errors=errors_summary
            )
            
            # Generate response
            response = await self.llm.apredict(prompt)
            
            # Clean up the response
            state.response = response.strip()
            
            # Set response type based on interface
            if state.interface in ["voice", "phone"]:
                state.response_type = "voice"
            elif state.interface == "whatsapp":
                state.response_type = "chat"
            else:
                state.response_type = "text"
                
        except Exception as e:
            state.add_error(f"Response generation failed: {str(e)}")
            state.response = self._generate_fallback_response(state)
        
        return state
    
    def _summarize_actions(self, actions: list) -> str:
        """Summarize actions taken"""
        if not actions:
            return "No actions taken"
        
        summary_parts = []
        for action in actions:
            tool = action.get("tool", "unknown")
            action_name = action.get("action", "unknown")
            success = action.get("success", False)
            status = "✓" if success else "✗"
            summary_parts.append(f"{status} {tool}: {action_name}")
        
        return "; ".join(summary_parts)
    
    def _summarize_results(self, results: dict) -> str:
        """Summarize tool results"""
        if not results:
            return "No results"
        
        summary_parts = []
        for key, result in results.items():
            if isinstance(result, dict):
                if "error" in result:
                    summary_parts.append(f"{key}: Error - {result['error']}")
                else:
                    summary_parts.append(f"{key}: Success with data")
            else:
                summary_parts.append(f"{key}: {str(result)[:100]}...")
        
        return "; ".join(summary_parts)
    
    def _summarize_errors(self, errors: list) -> str:
        """Summarize errors"""
        if not errors:
            return "No errors"
        return "; ".join(errors)
    
    def _generate_fallback_response(self, state: ConversationState) -> str:
        """Generate a fallback response when AI generation fails"""
        
        if state.actions_taken:
            successful_actions = [a for a in state.actions_taken if a.get("success")]
            if successful_actions:
                return f"I completed {len(successful_actions)} actions for you, though I had trouble generating a detailed response."
            else:
                return "I tried to help but encountered some issues. Let me know if you'd like me to try again."
        else:
            return "I received your message but wasn't sure how to help. Could you try rephrasing your request?"