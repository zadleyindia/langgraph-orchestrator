# ReAct Integration Guide

## Overview

The LangGraph Orchestrator now supports ReAct (Reasoning and Acting) pattern for enhanced agent decision-making. This allows agents to break down complex tasks into structured thought-action-observation loops.

## Architecture

### ReAct Base Agent (`orchestrator/agents/react_base_agent.py`)

The `ReActBaseAgent` class provides:
- Structured reasoning framework
- Action types: THINK, SEARCH, CALCULATE, COMMUNICATE, DELEGATE, USE_TOOL, CONCLUDE
- Configurable max steps and temperature
- Automatic reasoning chain tracking

### How ReAct Works

The ReAct pattern helps agents break down complex problems by:
1. **Reasoning** - Analyzing the situation and planning next steps
2. **Acting** - Taking specific actions based on the reasoning
3. **Observing** - Processing results and adjusting approach

This creates a loop that continues until the agent reaches a satisfactory conclusion.

## Usage Examples

### Personal Assistant with ReAct

```python
# Complex coordination request
request = "Analyze last month's sales data and schedule a meeting with the team to discuss the findings"

# The Personal Assistant will:
# 1. THINK: Break down into data analysis + scheduling tasks
# 2. DELEGATE: Send data analysis to Data Analyst agent
# 3. SEARCH: Check calendar availability
# 4. COMMUNICATE: Draft meeting invite
# 5. CONCLUDE: Provide coordinated response
```

### Data Analyst with ReAct

```python
# Complex analysis request
request = "Compare Q1 and Q2 performance, identify trends, and forecast Q3"

# The Data Analyst will:
# 1. THINK: Plan analysis approach
# 2. SEARCH: Find Q1 and Q2 datasets
# 3. CALCULATE: Compute performance metrics
# 4. CALCULATE: Identify trends
# 5. CALCULATE: Generate Q3 forecast
# 6. COMMUNICATE: Create visualization
# 7. CONCLUDE: Present insights and recommendations
```

## Configuration

### Enable/Disable ReAct

Agents automatically use ReAct for complex requests. To manually control:

```python
# In agent initialization
agent.react_enabled = True  # or False

# Adjust complexity detection
agent.max_react_steps = 10  # More steps for thorough analysis
agent.react_temperature = 0.1  # Lower for more deterministic reasoning
```

### Complexity Detection

Each agent has custom complexity indicators:

**Personal Assistant:**
- Multi-agent coordination keywords
- Complex planning requests
- Decision-making scenarios

**Data Analyst:**
- Multi-step analysis
- Multiple data sources
- Statistical modeling
- Comprehensive reporting

## Best Practices

1. **Use ReAct for Complex Tasks**: Let agents automatically detect when to use structured reasoning
2. **Monitor Step Count**: Adjust max_react_steps based on task complexity
3. **Review Reasoning Chains**: Use reasoning_chain in responses for debugging
4. **Fallback Gracefully**: Standard processing remains available if ReAct fails

## Integration with LangGraph

ReAct enhances but doesn't replace LangGraph:
- LangGraph: Overall orchestration and state management
- ReAct: Individual agent reasoning for complex tasks
- Both work together for optimal performance

## Learning Resources

### Understanding ReAct Pattern
- ReAct combines reasoning and acting for better AI decision-making
- Each step builds on previous observations
- Agents can adjust their approach mid-task based on results

### When to Use ReAct
- Complex multi-step problems
- Tasks requiring exploration and adjustment
- Situations where the full solution path isn't clear upfront
- Coordination between multiple systems or agents

### Key Concepts
- **Action Types**: Different categories of actions agents can take
- **Reasoning Chain**: The documented thought process
- **Complexity Detection**: Automatic triggers for ReAct mode
- **Fallback Handling**: Graceful degradation to standard processing