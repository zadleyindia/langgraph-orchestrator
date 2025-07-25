"""
Intent Analysis Node - Determines what the user wants to do
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from ..state import ConversationState

class IntentAnalyzer:
    """Analyzes user intent and categorizes requests"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.intent_prompt = PromptTemplate.from_template("""
You are analyzing user intent for a Personal AI Brain system that has access to 35+ tools.

Available tool categories:
- COMMUNICATION: WhatsApp, Slack, Email, Telegram
- DEVELOPMENT: GitHub, Docker, Jenkins, Terminal
- DATA: BigQuery, Shopify, AWS, Google Sheets
- MEMORY: Knowledge graph, context storage
- SEARCH: Web search, document search
- CREATIVE: Content generation, analysis
- FILESYSTEM: List files, read files, search files

User message: "{message}"
Previous context: {context}

Analyze the intent and respond with:
1. Primary intent (one word: communication, development, data, memory, search, creative, complex)
2. Required tools (list the specific tools needed)
3. Complexity level (simple, medium, complex)
4. Brief explanation

Format:
INTENT: [intent]
TOOLS: [tool1, tool2, ...]
COMPLEXITY: [level]
EXPLANATION: [brief explanation]
""")
    
    async def analyze(self, state: ConversationState) -> ConversationState:
        """Analyze user intent"""
        
        try:
            # Format the prompt
            prompt = self.intent_prompt.format(
                message=state.current_message,
                context=str(state.context)
            )
            
            # Get LLM response
            response = await self.llm.apredict(prompt)
            
            # Parse the response
            intent_data = self._parse_intent_response(response)
            
            # Update state
            state.intent = intent_data.get("intent", "unknown")
            state.tools_to_use = intent_data.get("tools", [])
            state.context["complexity"] = intent_data.get("complexity", "medium")
            state.context["explanation"] = intent_data.get("explanation", "")
            
        except Exception as e:
            state.add_error(f"Intent analysis failed: {str(e)}")
            state.intent = "fallback"
            state.tools_to_use = ["memory"]  # Safe fallback
        
        return state
    
    def _parse_intent_response(self, response: str) -> dict:
        """Parse the LLM response into structured data"""
        
        result = {}
        lines = response.strip().split('\n')
        
        for line in lines:
            if line.startswith("INTENT:"):
                result["intent"] = line.split(":", 1)[1].strip()
            elif line.startswith("TOOLS:"):
                tools_str = line.split(":", 1)[1].strip()
                result["tools"] = [tool.strip() for tool in tools_str.split(",") if tool.strip()]
            elif line.startswith("COMPLEXITY:"):
                result["complexity"] = line.split(":", 1)[1].strip()
            elif line.startswith("EXPLANATION:"):
                result["explanation"] = line.split(":", 1)[1].strip()
        
        return result