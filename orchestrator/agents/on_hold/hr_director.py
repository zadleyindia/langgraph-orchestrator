"""
HR Director Agent - Specialized in human resources and people management
Part of Mohit's Personal AI Brain multi-agent system
"""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class HRDirectorAgent(BaseAgent):
    """
    HR Director Agent
    
    Specializes in:
    - Human resources management
    - Talent acquisition and recruitment
    - Employee relations and development
    - Performance management
    - Organizational development
    - HR policy and compliance
    """
    
    def __init__(self, memory_client=None):
        super().__init__(
            role="hr_director",
            personality="empathetic, strategic, people-focused, professional",
            tools=["hrms", "recruiting", "performance_tracking", "employee_database", "learning_management", "compliance_tracking"],
            authority_level="high"
        )
        
        # Specialized skills for HR management
        self.skills = [
            "talent_acquisition",
            "performance_management",
            "employee_relations",
            "organizational_development",
            "training_development",
            "compensation_benefits",
            "hr_policy",
            "compliance",
            "leadership_development"
        ]
        
        # Tools and systems the agent can work with
        self.available_tools = [
            "hrms",
            "recruiting",
            "performance_tracking",
            "employee_database",
            "learning_management",
            "compliance_tracking"
        ]
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request as HR Director agent"""
        response = await self.process_request(request, context)
        return {
            "response": response,
            "agent": "hr_director", 
            "actions_taken": ["hr_response"],
            "context_updated": True
        }
    
    def should_handle_request(self, request: str, context: Dict[str, Any]) -> float:
        """Determine if this agent should handle the request"""
        request_lower = request.lower()
        
        # High confidence for HR keywords
        hr_keywords = ["hire", "hiring", "recruitment", "employee", "performance", "training", "hr", "compensation", "benefits", "policy"]
        if any(keyword in request_lower for keyword in hr_keywords):
            return 0.9
        
        # Medium confidence for people management
        people_keywords = ["team", "staff", "talent", "interview", "review", "feedback", "development"]
        if any(keyword in request_lower for keyword in people_keywords):
            return 0.7
        
        # Low confidence otherwise
        return 0.1

    async def process_request(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process HR-related request
        
        Args:
            message: User message requesting HR assistance
            context: Conversation context
            
        Returns:
            HR response
        """
        try:
            # Store interaction in memory
            await self.store_interaction(message, context)
            
            # Analyze request for HR domain
            hr_domain = self._identify_hr_domain(message)
            
            # Generate response based on HR domain
            if hr_domain == "recruitment":
                response = await self._handle_recruitment_request(message, context)
            elif hr_domain == "performance":
                response = await self._handle_performance_request(message, context)
            elif hr_domain == "employee_relations":
                response = await self._handle_employee_relations(message, context)
            elif hr_domain == "training":
                response = await self._handle_training_request(message, context)
            elif hr_domain == "compensation":
                response = await self._handle_compensation_request(message, context)
            elif hr_domain == "policy":
                response = await self._handle_policy_request(message, context)
            else:
                response = await self._handle_general_hr_request(message, context)
            
            # Store response in memory
            await self.store_interaction(response, context, is_response=True)
            
            return response
            
        except Exception as e:
            logger.error(f"HR Director error: {e}")
            return f"I'm having trouble with that HR request, {context.get('user_id', 'user')}. Could you provide more details about the specific HR challenge you're facing?"
    
    def _identify_hr_domain(self, message: str) -> str:
        """
        Identify the HR domain of the request
        
        Args:
            message: User message
            
        Returns:
            HR domain
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hire", "hiring", "recruit", "recruitment", "candidate", "interview", "job posting"]):
            return "recruitment"
        elif any(word in message_lower for word in ["performance", "review", "evaluation", "goals", "feedback", "appraisal"]):
            return "performance"
        elif any(word in message_lower for word in ["employee", "team", "conflict", "relations", "engagement", "satisfaction"]):
            return "employee_relations"
        elif any(word in message_lower for word in ["training", "development", "learning", "skill", "education", "course"]):
            return "training"
        elif any(word in message_lower for word in ["salary", "compensation", "benefits", "pay", "raise", "bonus"]):
            return "compensation"
        elif any(word in message_lower for word in ["policy", "compliance", "regulation", "law", "legal", "procedure"]):
            return "policy"
        else:
            return "general"
    
    async def _handle_recruitment_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle recruitment and talent acquisition requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with talent acquisition and recruitment.

For recruitment, I can assist with:
👥 Job description development and role definition
🎯 Candidate sourcing strategies and channels
📋 Interview process design and best practices
🔍 Candidate evaluation and assessment methods
📊 Recruitment metrics and pipeline analysis
💼 Employer branding and candidate experience

I can help you:
• Define role requirements and job specifications
• Create compelling job postings
• Develop interview questions and evaluation criteria
• Design recruitment workflows
• Analyze recruitment performance and optimize processes
• Build talent pipelines for future needs

What specific recruitment challenge are you working on? I can provide strategic guidance and practical solutions to help you attract and hire the best talent."""
    
    async def _handle_performance_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle performance management requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with performance management initiatives.

For performance management, I can assist with:
📊 Goal setting and OKR frameworks
📈 Performance review processes and cycles
🎯 360-degree feedback systems
📋 Performance improvement plans
🏆 Recognition and rewards programs
📝 Performance documentation and tracking

I can help you:
• Design performance evaluation systems
• Create goal-setting frameworks
• Develop feedback mechanisms
• Build performance improvement processes
• Implement recognition programs
• Address performance issues effectively

What specific performance management area would you like to focus on? I can help you create systems that drive employee engagement and organizational success."""
    
    async def _handle_employee_relations(self, message: str, context: Dict[str, Any]) -> str:
        """Handle employee relations and engagement requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with employee relations and engagement.

For employee relations, I can assist with:
🤝 Conflict resolution and mediation
📊 Employee engagement surveys and analysis
💬 Communication strategies and feedback channels
🎯 Team building and collaboration initiatives
🔍 Exit interview processes and retention strategies
📈 Employee satisfaction and wellness programs

I can help you:
• Address workplace conflicts and issues
• Improve communication and transparency
• Design engagement initiatives
• Build positive workplace culture
• Develop retention strategies
• Create employee feedback systems

What employee relations challenge are you facing? I can provide strategies to build a positive, productive workplace environment."""
    
    async def _handle_training_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle training and development requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with training and development programs.

For training and development, I can assist with:
📚 Learning needs analysis and skill assessments
🎓 Training program design and curriculum development
💼 Leadership development and succession planning
🔧 Skills training and professional development
📊 Training effectiveness measurement and ROI
🚀 Career development pathways and mentoring

I can help you:
• Identify training needs and skill gaps
• Design comprehensive learning programs
• Create development pathways for employees
• Build mentoring and coaching systems
• Measure training effectiveness
• Develop leadership capabilities

What training or development initiative would you like to implement? I can help you create programs that enhance employee capabilities and drive organizational growth."""
    
    async def _handle_compensation_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle compensation and benefits requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with compensation and benefits strategy.

For compensation and benefits, I can assist with:
💰 Salary benchmarking and market analysis
📊 Compensation structure design and pay scales
🎁 Benefits program development and optimization
🏆 Incentive and bonus program design
📈 Total rewards strategy and communication
⚖️ Pay equity analysis and compliance

I can help you:
• Analyze market compensation data
• Design competitive pay structures
• Develop comprehensive benefits packages
• Create performance-based incentive programs
• Ensure pay equity and compliance
• Communicate total rewards effectively

What compensation or benefits challenge are you addressing? I can provide strategic guidance to create competitive and equitable reward systems."""
    
    async def _handle_policy_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle HR policy and compliance requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'll help you with HR policy and compliance matters.

For HR policy and compliance, I can assist with:
📋 Policy development and documentation
⚖️ Employment law compliance and updates
🔍 Workplace investigations and procedures
📊 Compliance tracking and reporting
🛡️ Risk management and mitigation strategies
📝 Employee handbook and guideline creation

I can help you:
• Develop comprehensive HR policies
• Ensure compliance with employment laws
• Create investigation procedures
• Build risk management frameworks
• Design employee handbooks
• Stay updated on regulatory changes

What policy or compliance area needs attention? I can help you create clear, compliant policies that protect both employees and the organization."""
    
    async def _handle_general_hr_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle general HR requests"""
        user_id = context.get('user_id', 'Mohit')
        
        return f"""Hi {user_id}! I'm your HR Director, ready to help with all aspects of human resources.

I specialize in:
👥 Talent Acquisition & Recruitment
📊 Performance Management
🤝 Employee Relations & Engagement
📚 Training & Development
💰 Compensation & Benefits
📋 HR Policy & Compliance
🚀 Organizational Development

I can help you with:
• Strategic HR planning and initiatives
• People management challenges
• Organizational culture development
• Employee lifecycle management
• HR technology and systems
• Change management and communication

What HR challenge or opportunity are you working on? I'm here to provide strategic guidance and practical solutions to help you build a thriving workplace."""
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            Agent capabilities and skills
        """
        return {
            "agent_type": "hr_director",
            "skills": self.skills,
            "available_tools": self.available_tools,
            "specializations": [
                "Talent Acquisition",
                "Performance Management",
                "Employee Relations",
                "Training & Development",
                "Compensation & Benefits",
                "HR Policy & Compliance",
                "Organizational Development"
            ]
        }