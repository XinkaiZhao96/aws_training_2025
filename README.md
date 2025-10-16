# Weather Strands Agent

A comprehensive city information assistant built with Strands Agents framework and deployed on Amazon Bedrock's AgentCore Runtime.

## Features

- **Weather Information**: Real-time weather conditions using OpenWeather API
- **Event Discovery**: Local events and activities via Eventbrite API
- **Sunrise/Sunset Times**: Daily sun schedules using Sunrise-Sunset API
- **Streamlit Frontend**: Interactive web interface for easy access

## Architecture

- **Backend**: Strands Agent with HTTP request tools
- **Frontend**: Streamlit web application
- **Deployment**: AWS Bedrock AgentCore with Docker containers
- **APIs**: OpenWeather, Eventbrite, Sunrise-Sunset

## Quick Start

### Prerequisites

- Python 3.12+
- uv package manager
- Docker (for deployment)
- API keys for OpenWeather and Eventbrite

### Local Development

1. Install dependencies:
```bash
uv pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENWEATHER_API_KEY="your_openweather_key"
export EVENTBRITE_API_KEY="your_eventbrite_key"
```

3. Run the agent:
```bash
python weather_agent.py
```

4. Run the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```

### Docker Deployment

1. Build the container:
```bash
docker build -t weather-agent .
```

2. Run locally:
```bash
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key weather-agent
```

### AWS Deployment

Deploy to Bedrock AgentCore:
```bash
agentcore deploy
```

## Configuration

### API Keys

Update `.kiro/settings/mcp.json` with your API keys:
- Replace `YOUR_OPENWEATHER_API_KEY_HERE` with your OpenWeather API key
- Replace `YOUR_FIGMA_API_KEY_HERE` with your Figma API key (if using Figma integration)

### MCP Servers

The project includes Model Context Protocol (MCP) server configurations for:
- Strands Agent documentation
- AWS documentation
- Figma integration

## Project Structure

```
├── weather_agent.py              # Main agent implementation
├── streamlit_app.py             # Streamlit frontend
├── requirements.txt             # Python dependencies
├── .bedrock_agentcore.yaml      # AWS deployment config
├── weather-agent-api.md         # API documentation
├── .kiro/
│   ├── specs/                   # Project specifications
│   ├── steering/                # AI assistant guidance
│   └── settings/mcp.json        # MCP server configuration
└── .bedrock_agentcore/
    └── weather_agent/Dockerfile # Container configuration
```

## Usage Examples

Ask the agent natural language questions like:
- "What's the weather in London?"
- "Find events in New York this weekend"
- "When is sunrise in Tokyo tomorrow?"
- "Tell me about weather and events in Paris"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is licensed under the MIT License.