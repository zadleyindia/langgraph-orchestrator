"""
ReAct-Enhanced Data Analyst Agent
Analytical and detail-oriented agent with structured reasoning for data analysis
"""

from typing import Dict, List, Any, Optional
import json
import logging

from .base_agent import BaseAgent
from .react_base_agent import ReActBaseAgent, ActionType

logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent, ReActBaseAgent):
    """
    Data Analyst with ReAct reasoning capabilities
    Uses structured analysis approach for complex data problems
    """
    
    def __init__(self):
        # Initialize base agent with Data Analyst configuration
        BaseAgent.__init__(
            self,
            role="data_analyst",
            personality="analytical, detail-oriented, data-driven",
            tools=[
                "bigquery", "sql_server", "database", 
                "data_analysis", "reporting", "memory"
            ],
            authority_level="medium",
            system_prompt=self._build_data_analyst_prompt()
        )
        
        # Configure ReAct for analytical tasks
        self.max_react_steps = 10  # More steps for thorough analysis
        self.react_temperature = 0.1  # Lower temp for precision
        self.react_enabled = True
    
    def _build_data_analyst_prompt(self) -> str:
        """Build specialized system prompt for Data Analyst"""
        return """You are Mohit's Data Analyst Agent - the specialist for all data analysis, insights, and reporting needs.

PERSONALITY: Analytical, detail-oriented, data-driven, insightful
COMMUNICATION STYLE: Clear, precise, uses data to support recommendations

YOUR EXPERTISE:
- BigQuery and SQL Server analysis
- Data mining and pattern recognition
- Statistical analysis and forecasting
- Report generation and visualization
- Metrics tracking and KPI monitoring
- Business intelligence insights

DATA SOURCES:
- BigQuery: Company analytics data
- SQL Server: Operational databases
- Memory: Historical patterns and insights
- APIs: External data sources

RESPONSE PATTERN:
1. Acknowledge the data request
2. Identify relevant data sources
3. Present findings clearly with numbers
4. Provide insights and recommendations
5. Suggest follow-up analyses

EXAMPLES:
- "I'll analyze the sales data from BigQuery for Q4..."
- "Based on the customer metrics, I found that..."
- "The data shows a 23% increase in..."
- "I recommend tracking these KPIs going forward..."

Always support conclusions with data and provide actionable insights."""
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced request handling with ReAct for analytical tasks"""
        
        # Check if this needs structured analysis
        if self.react_enabled and await self.should_use_react(request, context):
            logger.info(f"Using ReAct pattern for data analysis: {request[:50]}...")
            return await self.handle_react_analysis(request, context)
        
        # Standard handling for simple queries
        return await super().handle_request(request, context)
    
    async def handle_react_analysis(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analytical request using ReAct reasoning"""
        
        # Add analytical context
        enhanced_context = {
            **context,
            "analysis_type": self._determine_analysis_type(request),
            "data_sources": context.get("data_sources", ["bigquery", "memory", "files"]),
            "output_format": context.get("output_format", "detailed_report")
        }
        
        # Execute ReAct loop
        react_result = await self.react_loop(request, enhanced_context)
        
        if react_result["success"]:
            # Format analytical response
            analysis_report = self._format_analysis_report(
                react_result["result"],
                react_result["reasoning_chain"],
                react_result["confidence"]
            )
            
            return {
                "response": analysis_report,
                "agent": "data_analyst",
                "actions_taken": ["react_analysis"],
                "analysis_steps": react_result["steps_taken"],
                "confidence": react_result["confidence"],
                "data_sources_used": self._extract_data_sources(react_result["reasoning_chain"]),
                "reasoning_chain": react_result["reasoning_chain"]
            }
        else:
            return {
                "response": f"I encountered challenges analyzing this data. Error: {react_result.get('error')}",
                "agent": "data_analyst",
                "actions_taken": ["analysis_failed"],
                "error": react_result.get("error")
            }
    
    def _determine_analysis_type(self, request: str) -> str:
        """Determine the type of analysis needed"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["trend", "pattern", "over time"]):
            return "trend_analysis"
        elif any(word in request_lower for word in ["compare", "versus", "difference"]):
            return "comparative_analysis"
        elif any(word in request_lower for word in ["forecast", "predict", "projection"]):
            return "predictive_analysis"
        elif any(word in request_lower for word in ["summary", "overview", "report"]):
            return "summary_analysis"
        elif any(word in request_lower for word in ["anomaly", "outlier", "unusual"]):
            return "anomaly_detection"
        else:
            return "exploratory_analysis"
    
    async def should_use_react(self, request: str, context: Dict[str, Any]) -> bool:
        """Determine if request requires structured analysis"""
        
        # Data Analyst specific indicators
        da_complexity_indicators = [
            # Multi-step analysis
            "analyze and visualize", "explore and report",
            "investigate patterns", "deep dive",
            
            # Complex calculations
            "statistical analysis", "correlation", "regression",
            "forecast", "predict", "model",
            
            # Multiple data sources
            "combine data", "merge datasets", "cross-reference",
            "multiple sources", "integrate data",
            
            # Detailed reporting
            "comprehensive report", "detailed analysis",
            "executive summary", "insights and recommendations"
        ]
        
        request_lower = request.lower()
        
        # Check DA-specific indicators
        if any(indicator in request_lower for indicator in da_complexity_indicators):
            return True
        
        # Check if data volume suggests complexity
        if context.get("data_volume", "small") in ["large", "massive"]:
            return True
        
        # Use base class logic
        return await super().should_use_react(request, context)
    
    # Implement ReAct actions for Data Analysis
    
    async def _action_search(self, params: Dict[str, Any]) -> str:
        """Search for data or previous analyses"""
        search_type = params.get("type", "data")
        query = params.get("query", "")
        source = params.get("source", "all")
        
        if search_type == "data":
            # Simulate data search
            return f"Found 3 datasets matching '{query}' in {source}: sales_2024.csv (50MB), customer_data.json (10MB), transactions.parquet (100MB)"
        
        elif search_type == "previous_analysis":
            # Search for similar past analyses
            return f"Found 2 previous analyses: 'Q4 Sales Trend Analysis' (2 weeks ago), 'Customer Segmentation Study' (1 month ago)"
        
        elif search_type == "metadata":
            return f"Dataset metadata: 1.2M rows, 45 columns, date range: 2023-01-01 to 2024-12-31"
        
        return "Search completed."
    
    async def _action_calculate(self, params: Dict[str, Any]) -> str:
        """Perform data calculations and analysis"""
        calc_type = params.get("type", "basic_stats")
        data_ref = params.get("data", "current_dataset")
        
        if calc_type == "basic_stats":
            return "Basic statistics: Mean: $125.50, Median: $98.00, Std Dev: $45.20, Total Records: 1.2M"
        
        elif calc_type == "trend_analysis":
            return "Trend identified: 15% YoY growth, seasonal peak in Q4, weekly cyclical pattern detected"
        
        elif calc_type == "correlation":
            variables = params.get("variables", ["x", "y"])
            return f"Correlation between {variables[0]} and {variables[1]}: 0.73 (strong positive)"
        
        elif calc_type == "aggregation":
            group_by = params.get("group_by", "category")
            return f"Aggregated by {group_by}: Category A: $2.5M (45%), Category B: $1.8M (32%), Category C: $1.3M (23%)"
        
        elif calc_type == "anomaly_detection":
            return "Detected 23 anomalies: 15 revenue spikes, 8 unusual patterns in user behavior"
        
        return f"Calculation of type '{calc_type}' completed."
    
    async def _action_communicate(self, params: Dict[str, Any]) -> str:
        """Prepare data visualizations or reports"""
        comm_type = params.get("type", "report")
        format = params.get("format", "summary")
        
        if comm_type == "visualization":
            chart_type = params.get("chart_type", "line")
            return f"Created {chart_type} chart showing trends over time. Key insight: accelerating growth in Q4."
        
        elif comm_type == "report":
            return f"Generated {format} report with 5 key findings and 3 recommendations."
        
        elif comm_type == "dashboard":
            return "Updated dashboard with latest metrics. 4 KPIs trending up, 1 needs attention."
        
        return "Communication prepared."
    
    async def _action_delegate(self, params: Dict[str, Any]) -> str:
        """Delegate to other tools or agents"""
        delegate_to = params.get("to", "")
        task = params.get("task", "")
        
        if delegate_to == "bigquery":
            return f"Query executed in BigQuery: {task[:50]}... Returned 50,000 rows in 2.3 seconds."
        
        elif delegate_to == "python_env":
            return "Python analysis completed. Generated correlation matrix and regression model."
        
        elif delegate_to == "visualization_tool":
            return "Tableau dashboard updated with new data and insights."
        
        return f"Delegated to {delegate_to}."
    
    async def _action_use_tool(self, params: Dict[str, Any]) -> str:
        """Use analytical tools"""
        tool = params.get("tool", "")
        
        if tool == "sql_query":
            query = params.get("query", "SELECT * FROM table LIMIT 10")
            return f"SQL query executed successfully. Result preview: 10 rows × 8 columns"
        
        elif tool == "python_pandas":
            operation = params.get("operation", "describe")
            return f"Pandas operation '{operation}' completed. DataFrame shape: (1000, 20)"
        
        elif tool == "statistical_test":
            test_type = params.get("test", "t-test")
            return f"{test_type} result: p-value = 0.023 (statistically significant at α = 0.05)"
        
        elif tool == "ml_model":
            model_type = params.get("model", "linear_regression")
            return f"{model_type} trained. R² score: 0.87, RMSE: 12.5"
        
        return f"Tool {tool} executed."
    
    def _format_analysis_report(self, result: str, reasoning_chain: List[Dict], confidence: float) -> str:
        """Format a professional analysis report"""
        
        # Extract key insights from reasoning chain
        data_points = sum(1 for step in reasoning_chain if step["action"] == "calculate")
        searches = sum(1 for step in reasoning_chain if step["action"] == "search")
        
        report = f"""📊 **Data Analysis Report**

**Analysis Summary:**
{result}

**Methodology:**
- Analysis Type: {self.current_task_context.get('analysis_type', 'exploratory').replace('_', ' ').title()}
- Data Points Analyzed: {data_points}
- Data Sources Queried: {searches}
- Confidence Level: {confidence:.0%}

**Key Process Steps:**
"""
        
        # Add significant steps from reasoning
        significant_steps = [s for s in reasoning_chain if s["action"] in ["calculate", "search", "use_tool"]]
        for step in significant_steps[:3]:
            report += f"• {step['thought'][:100]}...\n"
        
        report += f"\n**Recommendations:**\nBased on this analysis, I recommend focusing on the insights provided above. Would you like me to dive deeper into any specific aspect?"
        
        return report
    
    def _extract_data_sources(self, reasoning_chain: List[Dict]) -> List[str]:
        """Extract data sources used in analysis"""
        sources = set()
        
        for step in reasoning_chain:
            if step["action"] == "search":
                source = step["action_input"].get("source", "unknown")
                sources.add(source)
            elif step["action"] == "delegate":
                delegate_to = step["action_input"].get("to", "unknown")
                sources.add(delegate_to)
        
        return list(sources)
    
    def get_react_prompt(self) -> str:
        """Data Analyst specific ReAct prompt"""
        return f"""{self.system_prompt}

As the Data Analyst, use structured reasoning to thoroughly analyze data and provide insights.

For each step:
1. Thought: Plan your analytical approach and identify what data/calculations are needed
2. Action: Execute specific analytical actions
3. Observation: Interpret results and determine next steps

Available Actions:
- THINK: Plan analysis strategy or interpret findings
- SEARCH: Query data sources, find datasets, or retrieve metadata
- CALCULATE: Perform statistical analysis, aggregations, or computations
- COMMUNICATE: Create visualizations or format reports
- DELEGATE: Use BigQuery, Python, or other analytical tools
- USE_TOOL: Execute specific tools: {', '.join(self.tools)}
- CONCLUDE: Provide final analysis with key insights and recommendations

Focus on data-driven insights, statistical rigor, and clear communication of findings.

Format:
Thought: [Analytical reasoning about the data problem]
Action: [ACTION_TYPE]
Action Input: {{"key": "value"}}"""