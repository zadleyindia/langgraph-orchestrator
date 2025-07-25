"""
ReAct-Enhanced Base Agent - Implements Reasoning and Acting pattern
Provides structured thought-action-observation loops for complex tasks
"""

from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.schema.language_model import BaseLanguageModel
from dataclasses import dataclass
from enum import Enum
import json
import logging
import re

from .base_agent import BaseAgent
from ..llm.config import get_default_llm

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions in ReAct pattern"""
    THINK = "think"
    SEARCH = "search"
    CALCULATE = "calculate"
    COMMUNICATE = "communicate"
    DELEGATE = "delegate"
    CONCLUDE = "conclude"
    USE_TOOL = "use_tool"


@dataclass
class ReActStep:
    """Single step in ReAct reasoning chain"""
    step_number: int
    thought: str
    action_type: ActionType
    action_input: Dict[str, Any]
    observation: Optional[str] = None
    is_final: bool = False


class ReActBaseAgent(ABC):
    """
    Enhanced base agent with ReAct (Reasoning and Acting) pattern
    Provides structured approach to complex problem solving
    """
    
    def __init__(
        self,
        role: str,
        personality: str,
        tools: List[str],
        authority_level: str,
        system_prompt: str,
        max_react_steps: int = 7,
        react_temperature: float = 0.3
    ):
        self.role = role
        self.personality = personality
        self.tools = tools
        self.authority_level = authority_level
        self.system_prompt = system_prompt
        self.max_react_steps = max_react_steps
        self.react_temperature = react_temperature
        
        # Initialize LLM for ReAct reasoning
        self.llm = get_default_llm(temperature=react_temperature)
        
        # Track ReAct chains
        self.react_history: List[ReActStep] = []
        self.current_task_context: Dict[str, Any] = {}
    
    def get_react_prompt(self) -> str:
        """Build ReAct-specific system prompt"""
        return f"""{self.system_prompt}

You use the ReAct (Reasoning and Acting) framework to solve complex problems.

For each step:
1. Thought: Analyze the current situation and plan your next action
2. Action: Choose an action type and specify inputs
3. Observation: Process the result of your action
4. Repeat until you reach a conclusion

Available Actions:
- THINK: Reason about the problem without external action
- SEARCH: Search for information in memory or knowledge base
- CALCULATE: Perform calculations or data analysis
- COMMUNICATE: Send messages or notifications
- DELEGATE: Delegate to another specialist agent
- USE_TOOL: Use a specific tool from your available tools: {', '.join(self.tools)}
- CONCLUDE: Provide final answer or result

Format your response as:
Thought: [Your reasoning about what to do next]
Action: [ACTION_TYPE]
Action Input: {{"key": "value"}}

When you have enough information, use:
Thought: [Summary of findings]
Action: CONCLUDE
Action Input: {{"result": "your final answer", "confidence": 0.95}}"""
    
    async def react_loop(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ReAct reasoning loop for complex tasks
        
        Args:
            task: The task to accomplish
            context: Additional context for the task
            
        Returns:
            Result dictionary with reasoning chain and final answer
        """
        self.react_history = []
        self.current_task_context = context
        
        # Initial task setup
        current_prompt = f"""Task: {task}
Context: {json.dumps(context, indent=2)}

Begin your reasoning to accomplish this task."""
        
        for step in range(self.max_react_steps):
            try:
                # Get next thought and action
                react_step = await self._get_next_react_step(
                    current_prompt, 
                    step + 1
                )
                
                # Execute action and get observation
                observation = await self._execute_react_action(react_step)
                react_step.observation = observation
                
                # Add to history
                self.react_history.append(react_step)
                
                # Check if we've reached a conclusion
                if react_step.is_final or react_step.action_type == ActionType.CONCLUDE:
                    return self._format_react_result(task)
                
                # Update prompt for next iteration
                current_prompt = self._build_continuation_prompt(react_step)
                
            except Exception as e:
                logger.error(f"Error in ReAct step {step + 1}: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "reasoning_chain": [self._step_to_dict(s) for s in self.react_history],
                    "steps_taken": len(self.react_history)
                }
        
        # Max steps reached without conclusion
        return {
            "success": False,
            "error": "Maximum reasoning steps reached without conclusion",
            "reasoning_chain": [self._step_to_dict(s) for s in self.react_history],
            "steps_taken": len(self.react_history)
        }
    
    async def _get_next_react_step(self, prompt: str, step_number: int) -> ReActStep:
        """Get next thought and action from LLM"""
        
        messages = [
            SystemMessage(content=self.get_react_prompt()),
            HumanMessage(content=prompt)
        ]
        
        # Add history context if exists
        if self.react_history:
            history_prompt = "\n\nPrevious steps:\n"
            for step in self.react_history[-3:]:  # Last 3 steps for context
                history_prompt += f"\nStep {step.step_number}:\n"
                history_prompt += f"Thought: {step.thought}\n"
                history_prompt += f"Action: {step.action_type.value}\n"
                history_prompt += f"Observation: {step.observation}\n"
            
            messages.append(HumanMessage(content=history_prompt))
        
        response = await self.llm.ainvoke(messages)
        
        # Parse response into ReActStep
        return self._parse_react_response(response.content, step_number)
    
    def _parse_react_response(self, response: str, step_number: int) -> ReActStep:
        """Parse LLM response into structured ReActStep"""
        
        # Extract thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else "No thought provided"
        
        # Extract action type
        action_match = re.search(r'Action:\s*(\w+)', response)
        action_type_str = action_match.group(1).upper() if action_match else "THINK"
        
        try:
            action_type = ActionType[action_type_str]
        except KeyError:
            action_type = ActionType.THINK
        
        # Extract action input
        input_match = re.search(r'Action Input:\s*({.+?})', response, re.DOTALL)
        if input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                action_input = {"raw_input": input_match.group(1)}
        else:
            action_input = {}
        
        # Check if final
        is_final = action_type == ActionType.CONCLUDE
        
        return ReActStep(
            step_number=step_number,
            thought=thought,
            action_type=action_type,
            action_input=action_input,
            is_final=is_final
        )
    
    async def _execute_react_action(self, step: ReActStep) -> str:
        """Execute the action and return observation"""
        
        try:
            if step.action_type == ActionType.THINK:
                return "Thought recorded. Continue reasoning."
            
            elif step.action_type == ActionType.SEARCH:
                return await self._action_search(step.action_input)
            
            elif step.action_type == ActionType.CALCULATE:
                return await self._action_calculate(step.action_input)
            
            elif step.action_type == ActionType.COMMUNICATE:
                return await self._action_communicate(step.action_input)
            
            elif step.action_type == ActionType.DELEGATE:
                return await self._action_delegate(step.action_input)
            
            elif step.action_type == ActionType.USE_TOOL:
                return await self._action_use_tool(step.action_input)
            
            elif step.action_type == ActionType.CONCLUDE:
                return "Conclusion reached."
            
            else:
                return f"Unknown action type: {step.action_type}"
                
        except Exception as e:
            return f"Error executing action: {str(e)}"
    
    # Abstract methods for specific agent implementations
    @abstractmethod
    async def _action_search(self, params: Dict[str, Any]) -> str:
        """Search for information - implement in subclass"""
        pass
    
    @abstractmethod
    async def _action_calculate(self, params: Dict[str, Any]) -> str:
        """Perform calculations - implement in subclass"""
        pass
    
    @abstractmethod
    async def _action_communicate(self, params: Dict[str, Any]) -> str:
        """Send communication - implement in subclass"""
        pass
    
    @abstractmethod
    async def _action_delegate(self, params: Dict[str, Any]) -> str:
        """Delegate to another agent - implement in subclass"""
        pass
    
    @abstractmethod
    async def _action_use_tool(self, params: Dict[str, Any]) -> str:
        """Use specific tool - implement in subclass"""
        pass
    
    def _build_continuation_prompt(self, last_step: ReActStep) -> str:
        """Build prompt for next step based on observation"""
        return f"""Previous thought: {last_step.thought}
Previous action: {last_step.action_type.value}
Observation: {last_step.observation}

Based on this observation, what should be the next step? Continue reasoning."""
    
    def _format_react_result(self, original_task: str) -> Dict[str, Any]:
        """Format final result with reasoning chain"""
        
        # Get final conclusion from last step
        final_step = self.react_history[-1]
        final_result = final_step.action_input.get("result", "No conclusion provided")
        confidence = final_step.action_input.get("confidence", 0.5)
        
        return {
            "success": True,
            "task": original_task,
            "result": final_result,
            "confidence": confidence,
            "reasoning_chain": [self._step_to_dict(s) for s in self.react_history],
            "steps_taken": len(self.react_history),
            "agent": self.role
        }
    
    def _step_to_dict(self, step: ReActStep) -> Dict[str, Any]:
        """Convert ReActStep to dictionary for serialization"""
        return {
            "step": step.step_number,
            "thought": step.thought,
            "action": step.action_type.value,
            "action_input": step.action_input,
            "observation": step.observation,
            "is_final": step.is_final
        }
    
    async def should_use_react(self, request: str, context: Dict[str, Any]) -> bool:
        """
        Determine if request requires ReAct pattern
        Override in subclass for agent-specific logic
        """
        # Default heuristics for complexity
        complexity_indicators = [
            "analyze", "calculate", "compare", "investigate",
            "research", "find out", "determine", "figure out",
            "multiple", "steps", "complex", "detailed"
        ]
        
        request_lower = request.lower()
        
        # Check for complexity indicators
        if any(indicator in request_lower for indicator in complexity_indicators):
            return True
        
        # Check if context suggests complexity
        if context.get("requires_analysis", False):
            return True
        
        # Check request length (longer requests often more complex)
        if len(request.split()) > 20:
            return True
        
        return False