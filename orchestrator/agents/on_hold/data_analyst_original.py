"""
Data Analyst Agent - Specialized in data analysis, insights, and reporting
Part of Mohit's Personal AI Brain multi-agent system
"""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent
    
    Specializes in:
    - Data analysis and interpretation
    - Statistical insights and reporting
    - Business intelligence
    - Trend analysis and forecasting
    - Data visualization recommendations
    """
    
    def __init__(self, memory_client=None):
        super().__init__(
            role="data_analyst",
            personality="analytical, detail-oriented, data-driven, methodical",
            tools=["bigquery", "excel", "database", "analytics", "visualization", "reporting"],
            authority_level="medium"
        )
        
        # Specialized skills for data analysis
        self.skills = [
            "statistical_analysis",
            "data_interpretation",
            "trend_analysis",
            "business_intelligence",
            "data_visualization",
            "forecasting",
            "reporting",
            "metric_analysis"
        ]
        
        # Tools and data sources the agent can work with
        self.available_tools = [
            "bigquery",
            "excel",
            "database",
            "analytics",
            "visualization",
            "reporting"
        ]
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request as Data Analyst agent"""
        response = await self.process_request(request, context)
        return {
            "response": response,
            "agent": "data_analyst", 
            "actions_taken": ["data_analysis_response"],
            "context_updated": True
        }
    
    def should_handle_request(self, request: str, context: Dict[str, Any]) -> float:
        """Determine if this agent should handle the request"""
        request_lower = request.lower()
        
        # High confidence for data analysis keywords
        data_keywords = ["analyze", "data", "statistics", "report", "chart", "graph", "trend", "metric", "dashboard", "visualize"]
        if any(keyword in request_lower for keyword in data_keywords):
            return 0.9
        
        # Medium confidence for business intelligence
        bi_keywords = ["business", "intelligence", "insights", "performance", "forecast", "prediction"]
        if any(keyword in request_lower for keyword in bi_keywords):
            return 0.7
        
        # Low confidence otherwise
        return 0.1

    async def process_request(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process data analysis request
        
        Args:
            message: User message requesting data analysis
            context: Conversation context
            
        Returns:
            Data analysis response
        """
        try:
            # Store interaction in memory
            await self.store_interaction(message, context)
            
            # Analyze request for data analysis keywords
            analysis_type = self._identify_analysis_type(message)
            
            # Generate response based on analysis type
            if analysis_type == "statistical":
                response = await self._handle_statistical_analysis(message, context)
            elif analysis_type == "trend":
                response = await self._handle_trend_analysis(message, context)
            elif analysis_type == "reporting":
                response = await self._handle_reporting_request(message, context)
            elif analysis_type == "visualization":
                response = await self._handle_visualization_request(message, context)
            elif analysis_type == "forecasting":
                response = await self._handle_forecasting_request(message, context)
            else:
                response = await self._handle_general_analysis(message, context)
            
            # Store response in memory
            await self.store_interaction(response, context, is_response=True)
            
            return response
            
        except Exception as e:
            logger.error(f"Data Analyst error: {e}")
            return f"I'm having trouble with that data analysis request, {context.get('user_id', 'user')}. Could you provide more specific details about the data you'd like me to analyze?"
    
    def _identify_analysis_type(self, message: str) -> str:
        """
        Identify the type of data analysis requested
        
        Args:
            message: User message
            
        Returns:
            Analysis type
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["statistics", "statistical", "mean", "median", "correlation", "regression"]):
            return "statistical"
        elif any(word in message_lower for word in ["trend", "trending", "pattern", "over time", "growth", "decline"]):
            return "trend"
        elif any(word in message_lower for word in ["report", "reporting", "dashboard", "summary", "overview"]):
            return "reporting"
        elif any(word in message_lower for word in ["chart", "graph", "visualization", "plot", "visualize"]):
            return "visualization"
        elif any(word in message_lower for word in ["forecast", "predict", "prediction", "future", "projection"]):
            return "forecasting"
        else:
            return "general"
    
    async def _handle_statistical_analysis(self, message: str, context: Dict[str, Any]) -> str:
        """Handle statistical analysis requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with statistical analysis. 

For comprehensive statistical analysis, I can:
📊 Calculate descriptive statistics (mean, median, mode, standard deviation)
📈 Perform correlation analysis between variables
📉 Run regression analysis to identify relationships
🔍 Conduct hypothesis testing
📋 Generate statistical summaries and insights

To provide the most accurate analysis, I'll need:
• The specific dataset or data source
• What variables you want to analyze
• The type of statistical test or analysis you need
• Any specific hypotheses you want to test

Would you like me to connect to your data source (BigQuery, Excel, database) to perform this analysis?"""
    
    async def _handle_trend_analysis(self, message: str, context: Dict[str, Any]) -> str:
        """Handle trend analysis requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll analyze trends in your data.

For trend analysis, I can:
📈 Identify growth patterns and seasonal trends
📊 Track KPI performance over time
🔍 Detect anomalies and outliers
📉 Analyze market trends and business metrics
⚡ Provide trend forecasting insights

To deliver valuable trend insights, I'll need:
• Time series data or historical datasets
• The specific metrics you want to track
• Time period for analysis (daily, weekly, monthly)
• Any business context or external factors to consider

I can work with data from BigQuery, Excel files, or other data sources. What specific trends would you like me to analyze?"""
    
    async def _handle_reporting_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle reporting and dashboard requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll create comprehensive reports and dashboards for you.

For reporting, I can:
📋 Generate executive summaries and KPI reports
📊 Create automated dashboard layouts
📈 Build performance tracking reports
💼 Develop business intelligence insights
🔍 Provide data-driven recommendations

I can create reports for:
• Business performance metrics
• Sales and revenue analysis
• Customer analytics
• Operational efficiency
• Project progress tracking

What type of report would you like me to create? I can pull data from your existing sources and format it into actionable insights."""
    
    async def _handle_visualization_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle data visualization requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you visualize your data effectively.

For data visualization, I can recommend:
📊 Charts and graphs (bar, line, pie, scatter)
📈 Interactive dashboards
🗺️ Geographic visualizations
🔥 Heatmaps and correlation matrices
📉 Time series visualizations

I can suggest the best visualization type based on:
• Your data structure and type
• The story you want to tell
• Your audience and use case
• Interactive vs. static requirements

What data would you like to visualize? I can help you choose the most effective visualization approach and create specifications for your charts."""
    
    async def _handle_forecasting_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle forecasting and prediction requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with forecasting and predictive analysis.

For forecasting, I can:
📈 Predict future trends based on historical data
🔮 Build time series forecasting models
📊 Analyze seasonal patterns and cycles
⚡ Provide confidence intervals and accuracy metrics
🎯 Create scenario-based projections

I can forecast:
• Sales and revenue projections
• Customer growth trends
• Market demand patterns
• Business performance metrics
• Resource planning requirements

What would you like me to forecast? I'll need historical data and can help you understand the accuracy and limitations of the predictions."""
    
    async def _handle_general_analysis(self, message: str, context: Dict[str, Any]) -> str:
        """Handle general data analysis requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'm your Data Analyst, ready to help with any data analysis needs.

I specialize in:
📊 Statistical analysis and hypothesis testing
📈 Trend analysis and pattern recognition
📋 Business intelligence and reporting
📉 Data visualization and dashboard creation
🔮 Forecasting and predictive modeling
💼 Performance metrics and KPI tracking

I can work with data from:
• BigQuery databases
• Excel and CSV files
• Business applications
• APIs and data feeds
• Real-time data streams

What specific data analysis challenge are you working on? I'm here to help you turn your data into actionable insights!"""
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            Agent capabilities and skills
        """
        return {
            "agent_type": "data_analyst",
            "skills": self.skills,
            "available_tools": self.available_tools,
            "specializations": [
                "Statistical Analysis",
                "Trend Analysis", 
                "Business Intelligence",
                "Data Visualization",
                "Forecasting",
                "Performance Reporting"
            ]
        }