"""
Workflow Planning Node - Creates execution plan based on intent
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from ..state import ConversationState

class WorkflowPlanner:
    """Plans the workflow execution steps"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.planning_prompt = PromptTemplate.from_template("""
You are planning a workflow for a Personal AI Brain system.

User Intent: {intent}
Required Tools: {tools}
User Message: "{message}"
Context: {context}

Create a step-by-step execution plan. Each step should be:
1. Clear and actionable
2. Use one primary tool
3. Include necessary parameters
4. Consider dependencies between steps

For example:
- If user wants to "check GitHub PRs and send summary to team"
- Step 1: Get GitHub pull requests (github tool)
- Step 2: Analyze PR status (analysis)
- Step 3: Format summary (formatting)
- Step 4: Get team contacts (memory tool)
- Step 5: Send WhatsApp message (whatsapp tool)

Format your response as a numbered list:
1. [Tool]: [Action] - [Parameters/Details]
2. [Tool]: [Action] - [Parameters/Details]
...

Plan:
""")
    
    async def plan(self, state: ConversationState) -> ConversationState:
        """Create execution plan"""
        
        try:
            # Format the prompt
            prompt = self.planning_prompt.format(
                intent=state.intent,
                tools=", ".join(state.tools_to_use),
                message=state.current_message,
                context=str(state.context)
            )
            
            # Get LLM response
            response = await self.llm.apredict(prompt)
            
            # Parse the plan
            plan_steps = self._parse_plan_response(response)
            
            # Update state
            state.plan = plan_steps
            state.current_step = 0
            
        except Exception as e:
            state.add_error(f"Planning failed: {str(e)}")
            # Create a simple fallback plan
            state.plan = [
                "memory: Store conversation context",
                "response: Generate simple response"
            ]
        
        return state
    
    def _parse_plan_response(self, response: str) -> list:
        """Parse the LLM response into plan steps"""
        
        steps = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering and clean up
                step = line.split('.', 1)[-1].strip()
                if step.startswith('-'):
                    step = step[1:].strip()
                if step:
                    steps.append(step)
        
        return steps