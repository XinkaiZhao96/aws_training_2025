# Technology Stack

## Core Framework
- **Strands Agents**: Primary agent framework for LLM-based applications
- **Bedrock AgentCore**: AWS deployment runtime for agent hosting
- **Python 3.12**: Runtime environment with uv package manager

## Key Dependencies
```
bedrock-agentcore
strands-agents
strands-agents-tools
bedrock-agentcore-starter-toolkit
```

## External APIs
- **OpenWeather API**: Weather data (requires `OPENWEATHER_API_KEY`)
- **Eventbrite API**: Event search (requires `EVENTBRITE_API_KEY`)
- **Sunrise-Sunset API**: Sun times (no key required)

## Infrastructure
- **Container Runtime**: Docker with linux/arm64 platform
- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **AWS Region**: us-east-1
- **Network**: PUBLIC mode with HTTP protocol
- **Observability**: CloudWatch logging enabled
- **Memory**: STM_ONLY mode with 30-day event expiry

## Common Commands

### Local Development
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run locally for testing
python weather_agent.py

# Test agent invocation
agentcore invoke '{"prompt": "What is the weather in London?"}'
```

### Docker Operations
```bash
# Build container
docker build -t weather-agent .

# Run container locally
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key weather-agent
```

### AWS Deployment
```bash
# Deploy to AgentCore
agentcore deploy

# Check deployment status
agentcore status

# View logs
agentcore logs
```

## Environment Variables
- `OPENWEATHER_API_KEY`: Required for weather functionality
- `EVENTBRITE_API_KEY`: Optional for event search
- `AWS_REGION`: Set to us-east-1
- `DOCKER_CONTAINER`: Auto-set in containerized environments