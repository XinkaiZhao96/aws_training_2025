# Weather Agent API Documentation

## Overview

This document provides infrastructure details and integration information for the Weather Strands Agent deployed on Amazon Bedrock's AgentCore Runtime. The agent provides comprehensive city information including:

- **Weather Information**: Current weather conditions using OpenWeather API
- **Event Search**: Local events via Eventbrite API
- **Sunrise/Sunset Times**: Daily sun times using Sunrise-Sunset API

The agent can handle single or combined queries across all three features.

## Infrastructure Details

### AgentCore Runtime Information

- **Agent ID**: `weather_agent-E87KKC6j1D`
- **Agent ARN**: `arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D`
- **Agent Session ID**: `4ce632ed-dd26-4ab2-aac3-d20071433df5`
- **AWS Region**: `us-east-1`
- **AWS Account**: `318747609494`

### IAM Role Information

- **Execution Role ARN**: `arn:aws:iam::318747609494:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-425e274c35`
- **CodeBuild Execution Role ARN**: `arn:aws:iam::318747609494:role/AmazonBedrockAgentCoreSDKCodeBuild-us-east-1-425e274c35`

### Container Registry Information

- **ECR Repository URI**: `318747609494.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-weather_agent`
- **Platform**: `linux/arm64`
- **Container Runtime**: `docker`

### Memory Configuration

- **Memory ID**: `weather_agent_mem-oNbBPQCNzV`
- **Memory ARN**: `arn:aws:bedrock-agentcore:us-east-1:318747609494:memory/weather_agent_mem-oNbBPQCNzV`
- **Memory Name**: `weather_agent_mem`
- **Event Expiry Days**: `30`

### Network Configuration

- **Network Mode**: `PUBLIC`
- **Protocol**: `HTTP`
- **Observability**: `Enabled`

### CodeBuild Information

- **Project Name**: `bedrock-agentcore-weather_agent-builder`
- **Source Bucket**: `bedrock-agentcore-codebuild-sources-318747609494-us-east-1`

## API Configuration

### Required Environment Variables

The agent uses the following APIs and environment variables:

#### OpenWeather API (Weather Information)
- **Variable**: `OPENWEATHER_API_KEY`
- **Default**: `38a9c7392c1c9a1caf60671941d3d98b` (demo key)
- **Required**: Yes
- **Purpose**: Fetch current weather conditions and coordinates

#### Eventbrite API (Event Search)
- **Variable**: `EVENTBRITE_API_KEY`
- **Default**: None (must be configured)
- **Required**: Optional (events feature disabled without key)
- **Purpose**: Search for local events
- **Setup**: Get your API key from [Eventbrite Developer Portal](https://www.eventbrite.com/platform/api)

#### Sunrise-Sunset API
- **Variable**: None required
- **Purpose**: Get sunrise/sunset times (free API, no key needed)
- **Endpoint**: `https://api.sunrise-sunset.org/json`

### API Key Configuration

To enable all features, configure environment variables in your deployment:

```bash
export OPENWEATHER_API_KEY="your_openweather_api_key"
export EVENTBRITE_API_KEY="your_eventbrite_api_key"
```

## Invocation Methods

### Method 1: AgentCore CLI

```bash
agentcore invoke '{"prompt": "What is the weather in London?"}'
```

### Method 2: AWS SDK (Programmatic)

Use the AWS SDK to invoke the agent programmatically via the `InvokeAgentRuntime` API.

## Payload Formats

### Request Payload

```json
{
    "prompt": "What is the weather in New York?"
}
```

**Parameters:**
- `prompt` (string, required): The user's query in natural language (weather, events, sunrise/sunset, or combined)

### Response Format

#### Weather Response
```json
{
    "result": "The current weather in New York is 22°C with clear skies. It feels like 21°C with 60% humidity."
}
```

#### Events Response
```json
{
    "result": "Here are upcoming events in London:\n\n1. Tech Conference 2024 - Oct 25, 2024 at ExCeL London\n2. Art Exhibition - Oct 28, 2024 at Tate Modern\n3. Music Festival - Nov 2, 2024 at Hyde Park"
}
```

#### Sunrise/Sunset Response
```json
{
    "result": "In Tokyo today:\n- Sunrise: 6:15 AM JST\n- Sunset: 5:30 PM JST"
}
```

#### Combined Response
```json
{
    "result": "London Information:\n\nWeather: Currently 15°C with light rain, feels like 13°C\n\nUpcoming Events:\n1. Winter Market - Dec 15 at Covent Garden\n2. Holiday Concert - Dec 20 at Royal Albert Hall\n\nSun Times:\n- Sunrise: 7:45 AM GMT\n- Sunset: 3:52 PM GMT"
}
```

**Response Fields:**
- `result` (string): Formatted information response based on query type

### Example Queries

#### Weather Queries
- `"What's the weather in London?"`
- `"Tell me about the weather in Tokyo"`
- `"How's the weather in San Francisco today?"`

#### Event Queries
- `"What events are happening in New York?"`
- `"Find events in London"`
- `"Show me events in Paris"`

#### Sunrise/Sunset Queries
- `"What time is sunrise in Tokyo?"`
- `"When does the sun set in London today?"`
- `"Sunrise and sunset times for Sydney"`

#### Combined Queries
- `"Tell me about weather and events in London"`
- `"Weather, events, and sunrise time for New York"`
- `"What's happening in Paris today? Weather and events"`

## Error Handling

The agent handles various error scenarios gracefully:

### Weather API Errors
- **Invalid City Names**: Returns user-friendly message for unrecognized cities
- **API Unavailability**: Provides fallback response when OpenWeather API is unreachable
- **Invalid API Key**: Notifies user of authentication issues

### Event API Errors
- **Missing API Key**: Informs user that Eventbrite API key is required for event search
- **No Events Found**: Returns message when no events are available for the location
- **API Rate Limits**: Handles Eventbrite API rate limiting gracefully

### Sunrise/Sunset API Errors
- **Invalid Coordinates**: Handles cases where city coordinates cannot be determined
- **API Unavailability**: Provides fallback when sunrise-sunset API is unreachable

### General Error Handling
- **Network Issues**: Handles connection timeouts with appropriate error messages
- **Malformed Responses**: Gracefully handles unexpected API response formats
- **Multiple API Failures**: Provides partial information when some APIs fail

## Monitoring and Logging

- **CloudWatch Logs**: All agent interactions are logged to CloudWatch
- **Observability**: Built-in monitoring is enabled for performance tracking
- **Memory Management**: Conversation context is maintained with 30-day expiry
## Integ
ration Examples for Frontend Development

### Python Integration with boto3

#### Basic Setup

```python
import boto3
import json
from botocore.exceptions import ClientError

# Initialize the AgentCore Runtime client
client = boto3.client(
    'bedrock-agentcore',
    region_name='us-east-1'
)

# Agent configuration
AGENT_ARN = 'arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D'
```

#### Simple Weather Query Function

```python
def get_weather(city_name):
    """
    Query weather information for a specific city
    
    Args:
        city_name (str): Name of the city to get weather for
        
    Returns:
        dict: Weather information response
    """
    try:
        payload = {"prompt": f"What is the weather in {city_name}?"}
        response = client.invoke_agent_runtime(
            agentArn=AGENT_ARN,
            payload=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return {
            'success': True,
            'data': result.get('result', 'No weather data available'),
            'city': city_name
        }
    except ClientError as e:
        return {
            'success': False,
            'error': f"AWS Client Error: {e.response['Error']['Message']}",
            'error_code': e.response['Error']['Code']
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }

def get_events(city_name):
    """
    Query events for a specific city
    
    Args:
        city_name (str): Name of the city to get events for
        
    Returns:
        dict: Events information response
    """
    try:
        payload = {"prompt": f"What events are happening in {city_name}?"}
        response = client.invoke_agent_runtime(
            agentArn=AGENT_ARN,
            payload=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return {
            'success': True,
            'data': result.get('result', 'No events data available'),
            'city': city_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error: {str(e)}"
        }

def get_sunrise_sunset(city_name):
    """
    Query sunrise/sunset times for a specific city
    
    Args:
        city_name (str): Name of the city to get sun times for
        
    Returns:
        dict: Sunrise/sunset information response
    """
    try:
        payload = {"prompt": f"What time is sunrise and sunset in {city_name}?"}
        response = client.invoke_agent_runtime(
            agentArn=AGENT_ARN,
            payload=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return {
            'success': True,
            'data': result.get('result', 'No sun times data available'),
            'city': city_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error: {str(e)}"
        }

def get_comprehensive_info(city_name):
    """
    Query comprehensive city information (weather, events, sun times)
    
    Args:
        city_name (str): Name of the city to get information for
        
    Returns:
        dict: Comprehensive city information response
    """
    try:
        payload = {"prompt": f"Tell me about weather, events, and sunrise/sunset times in {city_name}"}
        response = client.invoke_agent_runtime(
            agentArn=AGENT_ARN,
            payload=json.dumps(payload)
        )
        result = json.loads(response['body'].read())
        return {
            'success': True,
            'data': result.get('result', 'No comprehensive data available'),
            'city': city_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error: {str(e)}"
        }
```

#### Advanced Integration with Error Handling

```python
import logging
from typing import Dict, Optional

class WeatherAgentClient:
    """
    Weather Agent client with comprehensive error handling
    """
    
    def __init__(self, region_name='us-east-1'):
        self.client = boto3.client('bedrock-agentcore', region_name=region_name)
        self.agent_arn = 'arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D'
        self.logger = logging.getLogger(__name__)
    
    def query_weather(self, prompt: str, timeout: int = 30) -> Dict:
        """
        Query weather information with comprehensive error handling
        
        Args:
            prompt (str): Natural language weather query
            timeout (int): Request timeout in seconds
            
        Returns:
            Dict: Standardized response with success/error information
        """
        try:
            payload = {"prompt": prompt}
            
            response = self.client.invoke_agent_runtime(
                agentArn=self.agent_arn,
                payload=json.dumps(payload)
            )
            
            # Parse response body
            response_body = json.loads(response['body'].read())
            
            return {
                'success': True,
                'data': response_body.get('result'),
                'metadata': {
                    'request_id': response.get('ResponseMetadata', {}).get('RequestId'),
                    'http_status': response.get('ResponseMetadata', {}).get('HTTPStatusCode')
                }
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            self.logger.error(f"AWS Client Error: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error': {
                    'type': 'aws_client_error',
                    'code': error_code,
                    'message': error_message,
                    'retryable': error_code in ['ThrottlingException', 'ServiceUnavailableException']
                }
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'json_decode_error',
                    'message': 'Failed to parse agent response',
                    'retryable': False
                }
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': {
                    'type': 'unexpected_error',
                    'message': str(e),
                    'retryable': False
                }
            }
    
    def get_weather_for_city(self, city: str) -> Dict:
        """Convenience method for city weather queries"""
        return self.query_weather(f"What is the weather in {city}?")
    
    def get_events_for_city(self, city: str) -> Dict:
        """Convenience method for city events queries"""
        return self.query_weather(f"What events are happening in {city}?")
    
    def get_sunrise_sunset_for_city(self, city: str) -> Dict:
        """Convenience method for sunrise/sunset queries"""
        return self.query_weather(f"What time is sunrise and sunset in {city}?")
    
    def get_comprehensive_city_info(self, city: str) -> Dict:
        """Get comprehensive city information (weather, events, sun times)"""
        return self.query_weather(f"Tell me about weather, events, and sunrise/sunset times in {city}")
    
    def get_weather_comparison(self, cities: list) -> Dict:
        """Get weather comparison for multiple cities"""
        cities_str = ", ".join(cities)
        return self.query_weather(f"Compare the weather in {cities_str}")
```

#### Usage Examples

```python
# Initialize the client
weather_client = WeatherAgentClient()

# Weather query
weather_result = weather_client.get_weather_for_city("London")
if weather_result['success']:
    print(f"Weather info: {weather_result['data']}")

# Events query
events_result = weather_client.get_events_for_city("London")
if events_result['success']:
    print(f"Events info: {events_result['data']}")

# Sunrise/sunset query
sun_result = weather_client.get_sunrise_sunset_for_city("London")
if sun_result['success']:
    print(f"Sun times: {sun_result['data']}")

# Comprehensive city information
comprehensive_result = weather_client.get_comprehensive_city_info("London")
if comprehensive_result['success']:
    print(f"Complete info: {comprehensive_result['data']}")

# Multiple city weather comparison
cities = ["New York", "London", "Tokyo"]
comparison = weather_client.get_weather_comparison(cities)

# Custom natural language queries
custom_queries = [
    "Is it raining in Seattle right now?",
    "What events are happening in Paris this weekend?",
    "When does the sun rise in Tokyo tomorrow?",
    "Tell me everything about Berlin today"
]

for query in custom_queries:
    result = weather_client.query_weather(query)
    if result['success']:
        print(f"Query: {query}")
        print(f"Response: {result['data']}\n")
```

### JavaScript/Node.js Integration

```javascript
const { BedrockAgentCoreClient, InvokeAgentRuntimeCommand } = require("@aws-sdk/client-bedrock-agentcore");

class WeatherAgentClient {
    constructor(region = 'us-east-1') {
        this.client = new BedrockAgentCoreClient({ region });
        this.agentArn = 'arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D';
    }
    
    async queryWeather(prompt) {
        try {
            const command = new InvokeAgentRuntimeCommand({
                agentArn: this.agentArn,
                payload: JSON.stringify({ prompt })
            });
            
            const response = await this.client.send(command);
            const result = JSON.parse(response.body);
            
            return {
                success: true,
                data: result.result,
                requestId: response.$metadata.requestId
            };
            
        } catch (error) {
            return {
                success: false,
                error: {
                    message: error.message,
                    code: error.name
                }
            };
        }
    }
    
    async getWeatherForCity(city) {
        return this.queryWeather(`What is the weather in ${city}?`);
    }
    
    async getEventsForCity(city) {
        return this.queryWeather(`What events are happening in ${city}?`);
    }
    
    async getSunriseSunsetForCity(city) {
        return this.queryWeather(`What time is sunrise and sunset in ${city}?`);
    }
    
    async getComprehensiveCityInfo(city) {
        return this.queryWeather(`Tell me about weather, events, and sunrise/sunset times in ${city}`);
    }
}

// Usage Examples
const weatherClient = new WeatherAgentClient();

// Weather information
weatherClient.getWeatherForCity('Paris')
    .then(result => {
        if (result.success) {
            console.log('Weather:', result.data);
        } else {
            console.error('Error:', result.error.message);
        }
    });

// Events information
weatherClient.getEventsForCity('London')
    .then(result => {
        if (result.success) {
            console.log('Events:', result.data);
        }
    });

// Sunrise/sunset information
weatherClient.getSunriseSunsetForCity('Tokyo')
    .then(result => {
        if (result.success) {
            console.log('Sun Times:', result.data);
        }
    });

// Comprehensive city information
weatherClient.getComprehensiveCityInfo('New York')
    .then(result => {
        if (result.success) {
            console.log('Complete Info:', result.data);
        }
    });
```

## Authentication and Authorization Requirements

### AWS Credentials Configuration

The application must have valid AWS credentials configured with appropriate permissions to invoke the AgentCore Runtime.

#### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:InvokeAgentRuntime"
            ],
            "Resource": "arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D"
        }
    ]
}
```

#### Credential Configuration Methods

1. **AWS CLI Profile**:
   ```bash
   aws configure --profile weather-agent-profile
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **IAM Roles** (recommended for EC2/Lambda):
   - Attach the required IAM policy to your EC2 instance role or Lambda execution role

4. **AWS SDK Configuration**:
   ```python
   # Python
   client = boto3.client(
       'bedrock-agentcore',
       region_name='us-east-1',
       aws_access_key_id='your_access_key',
       aws_secret_access_key='your_secret_key'
   )
   ```

### Security Best Practices

1. **Least Privilege**: Only grant the minimum required permissions
2. **Credential Rotation**: Regularly rotate access keys
3. **Environment Separation**: Use different credentials for development, staging, and production
4. **Logging**: Monitor API usage through CloudWatch logs
5. **Rate Limiting**: Implement client-side rate limiting to avoid throttling

### Error Codes and Handling

| Error Code | Description | Recommended Action |
|------------|-------------|-------------------|
| `AccessDeniedException` | Insufficient permissions | Check IAM policy and credentials |
| `ThrottlingException` | Rate limit exceeded | Implement exponential backoff |
| `ValidationException` | Invalid request format | Validate payload structure |
| `ServiceUnavailableException` | Service temporarily unavailable | Retry with exponential backoff |
| `InternalServerException` | Internal service error | Retry after delay |

### Rate Limiting Guidelines

- **Recommended Rate**: Maximum 10 requests per second
- **Burst Capacity**: Up to 20 requests in short bursts
- **Retry Strategy**: Exponential backoff with jitter
- **Timeout**: Set reasonable timeouts (30-60 seconds)

## Frontend Integration Patterns

### React Hook Example

```javascript
import { useState, useCallback } from 'react';
import { WeatherAgentClient } from './weather-client';

export const useWeatherAgent = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [weatherData, setWeatherData] = useState(null);
    
    const client = new WeatherAgentClient();
    
    const getWeather = useCallback(async (city) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await client.getWeatherForCity(city);
            
            if (result.success) {
                setWeatherData(result.data);
            } else {
                setError(result.error.message);
            }
        } catch (err) {
            setError('Failed to fetch weather data');
        } finally {
            setLoading(false);
        }
    }, []);
    
    return { getWeather, loading, error, weatherData };
};
```

### Vue.js Composition API Example

```javascript
import { ref, reactive } from 'vue';
import { WeatherAgentClient } from './weather-client';

export function useWeatherAgent() {
    const loading = ref(false);
    const error = ref(null);
    const weatherData = ref(null);
    
    const client = new WeatherAgentClient();
    
    const getWeather = async (city) => {
        loading.value = true;
        error.value = null;
        
        try {
            const result = await client.getWeatherForCity(city);
            
            if (result.success) {
                weatherData.value = result.data;
            } else {
                error.value = result.error.message;
            }
        } catch (err) {
            error.value = 'Failed to fetch weather data';
        } finally {
            loading.value = false;
        }
    };
    
    return {
        getWeather,
        loading: readonly(loading),
        error: readonly(error),
        weatherData: readonly(weatherData)
    };
}
```

This documentation provides comprehensive integration guidance for frontend developers to successfully integrate with the Weather Strands Agent deployed on Amazon Bedrock's AgentCore Runtime.