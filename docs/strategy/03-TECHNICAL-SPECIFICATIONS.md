# TECHNICAL SPECIFICATIONS
## Personal AI Brain - Detailed Implementation Guide

**Document Version:** 1.0  
**Last Updated:** July 13, 2025  
**Dependencies:** 01-MASTER-ARCHITECTURE-DOCUMENT.md, 02-IMPLEMENTATION-ROADMAP.md  

---

## CORE COMPONENT SPECIFICATIONS

### 1. Multi-Agent LangGraph Orchestrator

#### Technology Stack
```python
# Primary Dependencies
fastapi = "^0.104.0"          # Web framework
uvicorn = "^0.24.0"           # ASGI server
langchain = "^0.1.0"          # LLM orchestration
langgraph = "^0.0.40"         # Graph-based workflows
openai = "^1.0.0"             # OpenAI API client
httpx = "^0.25.0"             # Async HTTP client
pydantic = "^2.5.0"           # Data validation
redis = "^5.0.0"              # Caching and session storage
prometheus-client = "^0.19.0" # Metrics collection
structlog = "^23.2.0"         # Structured logging
```

#### Multi-Agent Directory Structure
```
langgraph-orchestrator/
├── main.py                        # FastAPI application entry point
├── orchestrator/
│   ├── __init__.py
│   ├── brain.py                  # Multi-agent orchestration hub
│   ├── agents/                   # Specialized AI agents
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class with personality framework
│   │   ├── personal_assistant.py # Primary coordinator agent
│   │   ├── data_analyst.py       # Analytics and business intelligence
│   │   ├── hr_director.py        # People management and policies
│   │   ├── dev_lead.py           # Technical leadership and development
│   │   └── ops_manager.py        # Operations and system management
│   ├── coordination/             # Agent communication and workflow
│   │   ├── __init__.py
│   │   ├── agent_router.py       # Route requests to appropriate agents
│   │   ├── workflow_coordinator.py # Multi-agent workflow management
│   │   └── agent_communication.py # Inter-agent messaging protocols
│   └── shared/                   # Shared components
│       ├── __init__.py
│       ├── memory_manager.py     # Shared agent memory
│       ├── tool_mapper.py        # Agent-specific tool access
│       └── personality_engine.py # Agent personality management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py           # Request schemas
│   │   ├── responses.py          # Response schemas
│   │   ├── workflows.py          # Workflow definitions
│   │   └── services.py           # Service definitions
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuration management
│   │   └── logging.py            # Logging configuration
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── errors.py             # Custom exceptions
│   │   └── metrics.py            # Metrics collection
│   └── api/
│       ├── __init__.py
│       ├── chat.py               # Chat endpoints
│       ├── voice.py              # Voice/WebSocket endpoints
│       ├── webhook.py            # Webhook endpoints
│       └── health.py             # Health check endpoints
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   └── strategy/                 # This directory
├── scripts/
│   ├── deploy.sh
│   ├── test-services.sh
│   └── health-check.sh
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

#### Multi-Agent Core Class Definitions

```python
# orchestrator/agents/base_agent.py
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, role: str, personality: str, tools: List[str], authority_level: str):
        self.role = role
        self.personality = personality
        self.available_tools = tools
        self.decision_authority = authority_level
        self.memory = AgentMemory(agent_id=role)
    
    @abstractmethod
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request using agent-specific logic"""
        pass
    
    @abstractmethod
    def format_response(self, content: Any) -> str:
        """Format response with agent personality"""
        pass

# orchestrator/agents/personal_assistant.py
class PersonalAssistantAgent(BaseAgent):
    """Primary coordinator agent - proactive, organized, anticipates needs"""
    
    def __init__(self):
        super().__init__(
            role="personal_assistant",
            personality="proactive_organized",
            tools=["calendar", "email", "whatsapp", "scheduling"],
            authority_level="high"
        )
    
    async def handle_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Determine if simple response or multi-agent coordination needed
        if self.is_complex_request(request):
            return await self.coordinate_multi_agent_workflow(request)
        else:
            return await self.handle_simple_request(request)
    
    def format_response(self, content: Any) -> str:
        # Proactive, organized personality with next steps
        return f"{content}\n\nWhat would you like me to help with next, Mohit?"

# orchestrator/agents/data_analyst.py  
class DataAnalystAgent(BaseAgent):
    """Analytics specialist - analytical, detail-oriented, insight-driven"""
    
    def __init__(self):
        super().__init__(
            role="data_analyst", 
            personality="analytical_precise",
            tools=["bigquery", "tableau", "sheets", "ai_analysis"],
            authority_level="medium"
        )
    
    def format_response(self, analysis_results: Dict) -> str:
        return {
            "executive_summary": "Key insights in 2-3 bullets",
            "detailed_findings": "Full analysis with supporting data", 
            "recommendations": "Actionable next steps",
            "visualizations": "Charts and graphs"
        }
        workflow.add_node("synthesize_response", self.synthesize_response)
        
        # Define edges
        workflow.add_edge(START, "analyze_intent")
        workflow.add_edge("analyze_intent", "plan_workflow")
        workflow.add_edge("plan_workflow", "execute_tools")
        workflow.add_edge("execute_tools", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        
        self.graph = workflow.compile()
    
    async def process_request(self, request: ChatRequest) -> ChatResponse:
        """Process user request through LangGraph workflow"""
        initial_state = ConversationState(
            messages=[HumanMessage(content=request.message)],
            current_step=0,
            plan=[],
            results={},
            user_id=request.user_id,
            session_id=request.session_id,
            context={}
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return ChatResponse(
            message=final_state.results.get("response", ""),
            session_id=final_state.session_id,
            metadata=final_state.context
        )
```

#### Intent Analysis Implementation
```python
# src/orchestrator/intent_analyzer.py
from typing import Dict, List, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class IntentAnalyzer:
    """Analyzes user intent and determines required actions"""
    
    def __init__(self, config: Config):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=config.openai_api_key
        )
        
    async def analyze_intent(self, state: ConversationState) -> ConversationState:
        """Analyze user intent from conversation"""
        
        system_prompt = """You are an intent analyzer for a Personal AI Brain system.
        
        Available MCP Services:
        - filesystem: File operations (list, read, write, search)
        - whatsapp: Send messages, get contacts
        - memory: Store and retrieve information
        - github: Repository operations, issues, PRs
        - bigquery: Data analysis and queries
        - n8n: Workflow automation
        - aws-s3: Cloud storage operations
        - google-sheets: Spreadsheet operations
        - slack: Team communication
        - jenkins: CI/CD operations
        
        Analyze the user's message and return:
        1. Primary intent (what they want to accomplish)
        2. Required services (which MCP services needed)
        3. Complexity level (simple/moderate/complex)
        4. Additional context needed (if any)
        
        Respond in JSON format:
        {
            "intent": "brief description",
            "services": ["service1", "service2"],
            "complexity": "simple|moderate|complex",
            "context_needed": ["any additional info needed"],
            "confidence": 0.95
        }"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state.messages[-1].content)
        ]
        
        response = await self.llm.ainvoke(messages)
        intent_data = json.loads(response.content)
        
        state.context["intent"] = intent_data
        return state
```

#### Workflow Planning Implementation
```python
# src/orchestrator/workflow_planner.py
from typing import Dict, List, Any

class WorkflowPlanner:
    """Creates execution plans based on analyzed intent"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.1)
        
    async def plan_workflow(self, state: ConversationState) -> ConversationState:
        """Create step-by-step execution plan"""
        
        intent_data = state.context["intent"]
        
        if intent_data["complexity"] == "simple":
            plan = await self._create_simple_plan(intent_data, state)
        elif intent_data["complexity"] == "moderate":
            plan = await self._create_moderate_plan(intent_data, state)
        else:
            plan = await self._create_complex_plan(intent_data, state)
            
        state.plan = plan
        return state
    
    async def _create_simple_plan(self, intent_data: Dict, state: ConversationState) -> List[Dict]:
        """Create plan for simple single-service requests"""
        service = intent_data["services"][0]
        
        # Map common patterns to service methods
        service_mappings = {
            "filesystem": {
                "list": "list_directory",
                "read": "read_file",
                "search": "search_files"
            },
            "whatsapp": {
                "send": "send_message",
                "contacts": "get_contacts"
            }
        }
        
        # Determine method based on intent
        method = self._determine_method(intent_data["intent"], service, service_mappings)
        params = self._extract_parameters(state.messages[-1].content, service, method)
        
        return [{
            "step": 1,
            "service": service,
            "method": method,
            "params": params,
            "description": f"Execute {method} on {service}"
        }]
    
    async def _create_complex_plan(self, intent_data: Dict, state: ConversationState) -> List[Dict]:
        """Create plan for complex multi-service workflows"""
        
        planning_prompt = f"""Create a detailed execution plan for this request:
        
        User Message: {state.messages[-1].content}
        Intent: {intent_data["intent"]}
        Required Services: {intent_data["services"]}
        
        Create a step-by-step plan with:
        1. Service to call
        2. Method to execute
        3. Parameters needed
        4. Dependencies on previous steps
        
        Return as JSON array of steps."""
        
        response = await self.llm.ainvoke([HumanMessage(content=planning_prompt)])
        plan = json.loads(response.content)
        
        return plan
```

#### Service Client Implementation
```python
# src/orchestrator/service_client.py
import httpx
from typing import Dict, Any, Optional
from circuit_breaker import CircuitBreaker

class ServiceClient:
    """HTTP client for communicating with MCP services"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
        self.circuit_breakers = {}
        
    async def execute_tools(self, state: ConversationState) -> ConversationState:
        """Execute all planned steps"""
        
        results = {}
        
        for step in state.plan:
            try:
                result = await self._execute_step(step)
                results[f"step_{step['step']}"] = result
                
                # Store result for next steps to use
                state.context[f"step_{step['step']}_result"] = result
                
            except Exception as e:
                logger.error(f"Step {step['step']} failed: {str(e)}")
                results[f"step_{step['step']}"] = {"error": str(e)}
                
                # Decide whether to continue or abort
                if step.get("critical", True):
                    break
        
        state.results = results
        return state
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        service_name = step["service"]
        method = step["method"]
        params = step["params"]
        
        # Get service endpoint
        service_info = await self.service_registry.get_service(service_name)
        if not service_info:
            raise Exception(f"Service {service_name} not available")
        
        endpoint = service_info["url"]
        
        # Use circuit breaker
        circuit_breaker = self._get_circuit_breaker(service_name)
        
        async def make_request():
            response = await self.client.post(
                f"{endpoint}/{method}",
                json=params,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        
        return await circuit_breaker.call(make_request)
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=httpx.HTTPError
            )
        
        return self.circuit_breakers[service_name]
```

### 2. Service Registry & Health Monitoring

```python
# src/services/service_registry.py
import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class ServiceRegistry:
    """Registry and health monitoring for MCP services"""
    
    def __init__(self, config: Config):
        self.config = config
        self.services = {}
        self.health_check_interval = 30  # seconds
        self.client = httpx.AsyncClient(timeout=5.0)
        
        # Initialize service definitions
        self._initialize_services()
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor_loop())
    
    def _initialize_services(self):
        """Initialize all MCP service definitions"""
        
        service_definitions = {
            "whatsapp": {
                "url": "http://supergateway-whatsapp:3001",
                "port": 3001,
                "methods": ["send_message", "get_contacts", "get_groups"],
                "health_endpoint": "/health",
                "critical": True
            },
            "filesystem": {
                "url": "http://supergateway-filesystem:3002", 
                "port": 3002,
                "methods": ["list_directory", "read_file", "search_files"],
                "health_endpoint": "/health",
                "critical": True
            },
            "memory": {
                "url": "http://supergateway-memory:3003",
                "port": 3003, 
                "methods": ["store_memory", "retrieve_memory", "search_knowledge"],
                "health_endpoint": "/health",
                "critical": True
            },
            # ... continue for all 35+ services
        }
        
        for name, definition in service_definitions.items():
            self.services[name] = {
                **definition,
                "status": "unknown",
                "last_check": None,
                "error_count": 0,
                "response_time": None
            }
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring loop"""
        
        while True:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_all_services(self):
        """Check health of all services"""
        
        tasks = []
        for service_name in self.services:
            task = asyncio.create_task(self._check_service_health(service_name))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, service_name: str):
        """Check health of a specific service"""
        
        service = self.services[service_name]
        start_time = datetime.now()
        
        try:
            health_url = f"{service['url']}{service['health_endpoint']}"
            response = await self.client.get(health_url)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                service["status"] = "healthy"
                service["error_count"] = 0
                service["response_time"] = response_time
            else:
                service["status"] = "unhealthy"
                service["error_count"] += 1
                
        except Exception as e:
            service["status"] = "unhealthy"
            service["error_count"] += 1
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
        
        service["last_check"] = datetime.now()
    
    async def get_healthy_services(self) -> List[str]:
        """Get list of healthy service names"""
        return [
            name for name, service in self.services.items()
            if service["status"] == "healthy"
        ]
    
    async def is_service_healthy(self, service_name: str) -> bool:
        """Check if specific service is healthy"""
        service = self.services.get(service_name)
        return service and service["status"] == "healthy"
```

### 3. API Endpoints

```python
# src/api/chat.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    brain: PersonalAIBrain = Depends(get_brain_instance)
) -> ChatResponse:
    """Main chat endpoint for text-based interactions"""
    
    try:
        # Validate request
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process through orchestrator
        response = await brain.process_request(request)
        
        # Log interaction
        logger.info(
            "Chat interaction completed",
            user_id=request.user_id,
            session_id=request.session_id,
            message_length=len(request.message),
            response_length=len(response.message)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# src/api/voice.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/api/v1", tags=["voice"])

@router.websocket("/voice")
async def voice_websocket(
    websocket: WebSocket,
    brain: PersonalAIBrain = Depends(get_brain_instance)
):
    """WebSocket endpoint for real-time voice interactions"""
    
    await websocket.accept()
    
    try:
        while True:
            # Receive voice data
            data = await websocket.receive_json()
            
            # Convert to chat request
            chat_request = ChatRequest(
                message=data["message"],
                user_id=data.get("user_id", "anonymous"),
                session_id=data.get("session_id", generate_session_id())
            )
            
            # Process request
            response = await brain.process_request(chat_request)
            
            # Send response
            await websocket.send_json({
                "type": "response",
                "message": response.message,
                "session_id": response.session_id,
                "metadata": response.metadata
            })
            
    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Internal error")
```

### 4. Docker Configuration

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker/docker-compose.yml
version: '3.8'

networks:
  personal-ai-brain:
    driver: bridge

volumes:
  redis-data:
  prometheus-data:
  grafana-data:

services:
  # Core orchestrator
  langgraph-orchestrator:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=info
    depends_on:
      - redis
    networks:
      - personal-ai-brain
    restart: unless-stopped
    
  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - personal-ai-brain
    restart: unless-stopped
    
  # Priority MCP Services
  supergateway-filesystem:
    image: ghcr.io/supercorp-ai/supergateway:latest
    command: >
      --stdio "npx @modelcontextprotocol/server-filesystem /workspace"
      --port 3002
    ports:
      - "3002:3002"
    volumes:
      - /Users/mohit/Desktop:/workspace/desktop:ro
      - /Users/mohit/Documents:/workspace/documents:ro
    networks:
      - personal-ai-brain
    restart: unless-stopped
    
  supergateway-whatsapp:
    image: ghcr.io/supercorp-ai/supergateway:latest
    command: >
      --stdio "node /app/whatsapp-mcp/index.js"
      --port 3001
    ports:
      - "3001:3001"
    environment:
      - WHATSAPP_USERNAME=${WHATSAPP_USERNAME}
      - WHATSAPP_PASSWORD=${WHATSAPP_PASSWORD}
      - WHATSAPP_API_URL=${WHATSAPP_API_URL}
    networks:
      - personal-ai-brain
    restart: unless-stopped
    
  # Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - personal-ai-brain
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - personal-ai-brain
    restart: unless-stopped
```

This technical specification provides the complete foundation for implementing the Personal AI Brain system with all the architectural decisions we've discussed.