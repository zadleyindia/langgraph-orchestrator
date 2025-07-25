"""
Operations Manager Agent - Specialized in business operations and project management
Part of Mohit's Personal AI Brain multi-agent system
"""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class OperationsManagerAgent(BaseAgent):
    """
    Operations Manager Agent
    
    Specializes in:
    - Business operations management
    - Project planning and coordination
    - Resource allocation and optimization
    - Process improvement and automation
    - Strategic planning and execution
    - Risk management and compliance
    """
    
    def __init__(self, memory_client=None):
        super().__init__(
            role="operations_manager",
            personality="organized, strategic, efficient, results-oriented",
            tools=["project_management", "resource_planning", "budgeting", "analytics", "compliance_tracking", "vendor_systems", "scheduling", "reporting"],
            authority_level="high"
        )
        
        # Specialized skills for operations management
        self.skills = [
            "project_management",
            "resource_allocation",
            "process_optimization",
            "strategic_planning",
            "risk_management",
            "compliance_oversight",
            "vendor_management",
            "budget_planning",
            "operational_analysis"
        ]
        
        # Tools and systems the agent can work with
        self.available_tools = [
            "project_management",
            "resource_planning",
            "budgeting",
            "analytics",
            "compliance_tracking",
            "vendor_systems",
            "scheduling",
            "reporting"
        ]
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request as Operations Manager agent"""
        response = await self.process_request(request, context)
        return {
            "response": response,
            "agent": "operations_manager", 
            "actions_taken": ["operations_response"],
            "context_updated": True
        }
    
    def should_handle_request(self, request: str, context: Dict[str, Any]) -> float:
        """Determine if this agent should handle the request"""
        request_lower = request.lower()
        
        # High confidence for operations keywords
        ops_keywords = ["project", "operations", "process", "planning", "strategy", "resource", "budget", "vendor", "risk", "compliance"]
        if any(keyword in request_lower for keyword in ops_keywords):
            return 0.9
        
        # Medium confidence for management terms
        mgmt_keywords = ["management", "organize", "coordinate", "schedule", "workflow", "efficiency", "optimize"]
        if any(keyword in request_lower for keyword in mgmt_keywords):
            return 0.7
        
        # Low confidence otherwise
        return 0.1

    async def process_request(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process operations-related request
        
        Args:
            message: User message requesting operations assistance
            context: Conversation context
            
        Returns:
            Operations response
        """
        try:
            # Store interaction in memory
            await self.store_interaction(message, context)
            
            # Analyze request for operations domain
            ops_domain = self._identify_operations_domain(message)
            
            # Generate response based on operations domain
            if ops_domain == "project_management":
                response = await self._handle_project_management(message, context)
            elif ops_domain == "resource_allocation":
                response = await self._handle_resource_allocation(message, context)
            elif ops_domain == "process_optimization":
                response = await self._handle_process_optimization(message, context)
            elif ops_domain == "strategic_planning":
                response = await self._handle_strategic_planning(message, context)
            elif ops_domain == "risk_management":
                response = await self._handle_risk_management(message, context)
            elif ops_domain == "compliance":
                response = await self._handle_compliance_request(message, context)
            elif ops_domain == "vendor_management":
                response = await self._handle_vendor_management(message, context)
            elif ops_domain == "budgeting":
                response = await self._handle_budgeting_request(message, context)
            else:
                response = await self._handle_general_operations(message, context)
            
            # Store response in memory
            await self.store_interaction(response, context, is_response=True)
            
            return response
            
        except Exception as e:
            logger.error(f"Operations Manager error: {e}")
            return f"I'm having trouble with that operations request, {context.get('user_id', 'user')}. Could you provide more details about the specific operational challenge you're facing?"
    
    def _identify_operations_domain(self, message: str) -> str:
        """
        Identify the operations domain of the request
        
        Args:
            message: User message
            
        Returns:
            Operations domain
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["project", "timeline", "milestone", "task", "deliverable", "gantt"]):
            return "project_management"
        elif any(word in message_lower for word in ["resource", "allocation", "capacity", "staffing", "workload"]):
            return "resource_allocation"
        elif any(word in message_lower for word in ["process", "workflow", "optimization", "efficiency", "automation"]):
            return "process_optimization"
        elif any(word in message_lower for word in ["strategy", "strategic", "planning", "roadmap", "vision", "goals"]):
            return "strategic_planning"
        elif any(word in message_lower for word in ["risk", "mitigation", "contingency", "threat", "vulnerability"]):
            return "risk_management"
        elif any(word in message_lower for word in ["compliance", "regulation", "audit", "policy", "standard"]):
            return "compliance"
        elif any(word in message_lower for word in ["vendor", "supplier", "contract", "procurement", "outsource"]):
            return "vendor_management"
        elif any(word in message_lower for word in ["budget", "cost", "expense", "financial", "roi", "investment"]):
            return "budgeting"
        else:
            return "general"
    
    async def _handle_project_management(self, message: str, context: Dict[str, Any]) -> str:
        """Handle project management requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with project management and coordination.

For project management, I can assist with:
📋 Project planning and scope definition
📅 Timeline creation and milestone tracking
👥 Team coordination and task assignment
📊 Progress monitoring and reporting
🔄 Agile and waterfall methodologies
📈 Project performance analysis

I can help you:
• Create comprehensive project plans
• Define project scope and deliverables
• Set up timeline and milestone schedules
• Coordinate team resources and assignments
• Track project progress and identify risks
• Generate project status reports

What specific project management challenge are you working on? I can provide strategic guidance and practical frameworks to help you deliver successful projects on time and within budget."""
    
    async def _handle_resource_allocation(self, message: str, context: Dict[str, Any]) -> str:
        """Handle resource allocation requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with resource allocation and capacity planning.

For resource allocation, I can assist with:
👥 Team capacity planning and workload management
📊 Resource utilization analysis and optimization
🔄 Resource scheduling and conflict resolution
💼 Skill matching and assignment optimization
📈 Demand forecasting and capacity modeling
⚖️ Workload balancing and burnout prevention

I can help you:
• Analyze current resource utilization
• Plan optimal resource allocation
• Identify capacity constraints and bottlenecks
• Balance workloads across teams
• Forecast future resource needs
• Optimize skill-to-task matching

What resource allocation challenge are you facing? I can help you create efficient resource plans that maximize productivity while maintaining team well-being."""
    
    async def _handle_process_optimization(self, message: str, context: Dict[str, Any]) -> str:
        """Handle process optimization requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you optimize processes and improve operational efficiency.

For process optimization, I can assist with:
🔄 Workflow analysis and redesign
⚡ Automation opportunities identification
📊 Process performance measurement
🎯 Bottleneck identification and resolution
📈 Efficiency improvement strategies
🔧 Standard operating procedure development

I can help you:
• Map current processes and identify inefficiencies
• Design optimized workflows
• Implement automation solutions
• Establish performance metrics
• Create standard operating procedures
• Monitor process improvements

What process would you like to optimize? I can help you streamline operations, reduce waste, and improve overall efficiency."""
    
    async def _handle_strategic_planning(self, message: str, context: Dict[str, Any]) -> str:
        """Handle strategic planning requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with strategic planning and long-term vision development.

For strategic planning, I can assist with:
🎯 Vision and mission statement development
📊 SWOT analysis and competitive assessment
🗺️ Strategic roadmap creation
📈 Goal setting and KPI definition
🔮 Scenario planning and forecasting
⚖️ Strategic decision-making frameworks

I can help you:
• Develop comprehensive strategic plans
• Define vision, mission, and core values
• Conduct market and competitive analysis
• Create strategic roadmaps and timelines
• Set measurable goals and objectives
• Build decision-making frameworks

What strategic planning challenge are you working on? I can provide frameworks and guidance to help you create compelling strategic plans that drive long-term success."""
    
    async def _handle_risk_management(self, message: str, context: Dict[str, Any]) -> str:
        """Handle risk management requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with risk management and mitigation strategies.

For risk management, I can assist with:
🔍 Risk identification and assessment
📊 Risk analysis and impact evaluation
🛡️ Risk mitigation strategy development
📋 Risk monitoring and reporting
🚨 Crisis management planning
⚖️ Risk-reward analysis and decision making

I can help you:
• Identify potential risks and threats
• Assess risk probability and impact
• Develop mitigation and contingency plans
• Create risk monitoring systems
• Build crisis response procedures
• Establish risk governance frameworks

What risk management area needs attention? I can help you proactively identify, assess, and mitigate risks to protect your operations and achieve your objectives."""
    
    async def _handle_compliance_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle compliance and regulatory requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with compliance and regulatory management.

For compliance, I can assist with:
📋 Regulatory requirement analysis
🔍 Compliance audit and assessment
📊 Compliance monitoring and reporting
📝 Policy and procedure development
🛡️ Compliance training and awareness
⚖️ Regulatory change management

I can help you:
• Identify applicable regulations and standards
• Conduct compliance gap analysis
• Develop compliance policies and procedures
• Create monitoring and reporting systems
• Plan compliance training programs
• Manage regulatory change impacts

What compliance area requires attention? I can help you build robust compliance frameworks that meet regulatory requirements while supporting business objectives."""
    
    async def _handle_vendor_management(self, message: str, context: Dict[str, Any]) -> str:
        """Handle vendor management requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with vendor management and supplier relationships.

For vendor management, I can assist with:
🤝 Vendor selection and evaluation
📋 Contract negotiation and management
📊 Vendor performance monitoring
💰 Cost optimization and procurement
🔍 Vendor risk assessment
📈 Supplier relationship management

I can help you:
• Develop vendor selection criteria
• Create RFP processes and evaluation frameworks
• Negotiate contracts and service agreements
• Monitor vendor performance and SLAs
• Manage vendor relationships and communications
• Optimize procurement processes

What vendor management challenge are you facing? I can help you build strong supplier relationships that deliver value while managing costs and risks."""
    
    async def _handle_budgeting_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle budgeting and financial planning requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with budgeting and financial planning.

For budgeting, I can assist with:
💰 Budget planning and forecasting
📊 Cost analysis and optimization
📈 Financial performance tracking
🎯 Budget variance analysis
💼 Capital expenditure planning
⚖️ ROI analysis and investment decisions

I can help you:
• Create comprehensive budgets and forecasts
• Analyze costs and identify savings opportunities
• Track financial performance against budgets
• Conduct variance analysis and reporting
• Plan capital investments and expenditures
• Evaluate ROI and financial impacts

What budgeting challenge are you working on? I can help you create effective budgets that support your strategic objectives while optimizing financial performance."""
    
    async def _handle_general_operations(self, message: str, context: Dict[str, Any]) -> str:
        """Handle general operations requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'm your Operations Manager, ready to help with all aspects of business operations.

I specialize in:
📋 Project Management & Coordination
👥 Resource Allocation & Capacity Planning
🔄 Process Optimization & Automation
🎯 Strategic Planning & Execution
🛡️ Risk Management & Compliance
💰 Budgeting & Financial Planning
🤝 Vendor Management & Procurement

I can help you with:
• Operational strategy and planning
• Business process improvement
• Resource optimization and allocation
• Project coordination and delivery
• Risk assessment and mitigation
• Compliance and regulatory management
• Vendor relationships and procurement
• Budget planning and cost optimization

What operational challenge or opportunity are you working on? I'm here to provide strategic guidance and practical solutions to help you run efficient, effective operations."""
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            Agent capabilities and skills
        """
        return {
            "agent_type": "operations_manager",
            "skills": self.skills,
            "available_tools": self.available_tools,
            "specializations": [
                "Project Management",
                "Resource Allocation",
                "Process Optimization", 
                "Strategic Planning",
                "Risk Management",
                "Compliance Management",
                "Vendor Management",
                "Budget Planning"
            ]
        }