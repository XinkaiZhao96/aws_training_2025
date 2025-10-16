# Project Structure

## Root Files
- `weather_agent.py`: Main agent implementation with system prompt and API integrations
- `requirements.txt`: Python dependencies for the project
- `.bedrock_agentcore.yaml`: AWS AgentCore deployment configuration
- `weather-agent-api.md`: Comprehensive API documentation and integration guide
- `.dockerignore`: Docker build exclusions

## Configuration Directories

### `.bedrock_agentcore/`
- `weather_agent/Dockerfile`: Container build configuration
- Contains AWS-specific deployment artifacts

### `.kiro/`
- `steering/`: AI assistant guidance documents (this directory)
- `settings/mcp.json`: Model Context Protocol server configurations
- `specs/`: Project specifications and design documents

### `.vscode/`
- IDE-specific settings and configurations

## Code Organization Patterns

### Agent Structure
- Single-file agent implementation in `weather_agent.py`
- BedrockAgentCoreApp as the main application wrapper
- Strands Agent with http_request tool integration
- Comprehensive system prompt with API endpoint configurations

### API Integration Pattern
```python
# Environment-based API key configuration
API_KEY = os.getenv("API_KEY_NAME", "default_value")
BASE_URL = "https://api.example.com/endpoint"

# Tool usage in system prompt
agent = Agent(
    tools=[http_request],
    system_prompt=f"""Instructions with {BASE_URL} references"""
)
```

### Deployment Structure
- Container-first deployment model
- AWS AgentCore runtime integration
- Environment variable configuration for API keys
- Multi-port exposure (8000, 8080, 9000) for flexibility

## File Naming Conventions
- Snake_case for Python files (`weather_agent.py`)
- Kebab-case for documentation (`weather-agent-api.md`)
- Lowercase for configuration files (`.bedrock_agentcore.yaml`)
- Standard dotfile conventions (`.dockerignore`, `.vscode/`)

## Development Workflow
1. Modify `weather_agent.py` for core functionality changes
2. Update `requirements.txt` for new dependencies
3. Test locally with `python weather_agent.py`
4. Deploy via AgentCore CLI commands
5. Update documentation in `weather-agent-api.md` as needed