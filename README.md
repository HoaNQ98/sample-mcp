# Sample MCP (Model Context Protocol) Microservice

A sample microservice implementing the Model Context Protocol (MCP) with clean architecture principles and LLM integration.

## Project Structure

The project follows a clean architecture pattern with the following structure:

```
services/
└── sample/
    ├── api/              # API layer (controllers)
    ├── domain/           # Domain layer (entities, use cases)
    ├── infrastructure/   # Infrastructure layer
    ├── tests/            # Tests
    ├── config.py         # Configuration
    ├── handler.py        # MCP request handler
    ├── main.py           # Application entry point
    ├── mcp_tool.yaml     # MCP tool configuration
    └── llm_example.py    # Example script for using LLM with MCP tools

shared/
├── config/              # Shared configuration
├── logging/            # Shared logging functionality
├── llms/               # LLM client implementations
│   ├── client.py       # Base LLM client interface
│   ├── openai_client.py # OpenAI implementation
│   ├── mcp_client.py   # MCP tool client with LLM
│   └── factory.py      # Factory for creating LLM clients
└── responses/          # Standardized API and MCP responses
```

## Features

- MCP tools:
  - `get_greeting`: Returns a greeting message
  - `calculate`: Performs basic arithmetic operations (add, subtract, multiply, divide)
- MCP resources:
  - `/health`: Health check endpoint
  - `/info`: Information about the MCP server
- LLM integration:
  - OpenAI client implementation
  - Tool calling capabilities
  - MCP tool client that uses LLM to call tools
  - Command-line example script
  - REST API endpoint for LLM processing
- FastAPI web server with OpenAPI documentation
- Docker support for containerization
- Clean architecture implementation
- Standardized API and MCP responses
- Centralized logging configuration
- Shared configuration system

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/sample-mcp.git
cd sample-mcp
```

2. Install dependencies:

```bash
make install
```

## Running Locally

```bash
make run
```

The service will be available at http://localhost:8000.

- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Info: http://localhost:8000/info

## Running with Docker

1. Build the Docker image:

```bash
make build
```

2. Start the Docker container:

```bash
make up
```

3. View logs:

```bash
make logs
```

4. Stop the Docker container:

```bash
make down
```

## Testing

Run the tests:

```bash
make test
```

## Shared Modules

### Configuration

The project uses a shared configuration system that allows services to extend a base configuration:

- `shared/config/base_settings.py`: Base settings class that all services can extend
- `services/sample/config.py`: Service-specific configuration that extends the base settings

### Logging

Centralized logging configuration is provided through:

- `shared/logging/logger.py`: Setup and configuration for application logging
- Log levels, formats, and output destinations can be configured via environment variables

### Standardized Responses

The project uses standardized response formats for both API and MCP endpoints:

- `shared/responses/api_response.py`: Standard API response models
- `shared/responses/mcp_response.py`: Standard MCP response models

## MCP Integration

This service implements the Model Context Protocol (MCP), which allows it to be used as a tool provider for AI models.

### Tools

#### get_greeting

Returns a greeting message.

**Input:**
```json
{
  "name": "John"
}
```

**Output:**
```json
{
  "greeting": "Hello, John! Welcome to the MCP sample service.",
  "timestamp": "2023-05-06T12:34:56.789012"
}
```

#### calculate

Performs a simple calculation.

**Input:**
```json
{
  "operation": "add",
  "a": 2,
  "b": 3
}
```

**Output:**
```json
{
  "result": 5,
  "operation": "add"
}
```

### Resources

#### /health

Health check endpoint.

**Output:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "message": "Service is running"
  },
  "timestamp": "2023-05-06T12:34:56.789012"
}
```

#### /info

Information about the MCP server.

**Output:**
```json
{
  "success": true,
  "data": {
    "name": "sample-mcp",
    "version": "0.1.0",
    "description": "Sample MCP server with clean architecture"
  },
  "timestamp": "2023-05-06T12:34:56.789012"
}
```

## LLM Integration

This service includes integration with Large Language Models (LLMs) to call MCP tools. The LLM client can be used to process natural language prompts and automatically call the appropriate MCP tools based on the context.

### LLM Client

The LLM client is implemented as an abstract base class with concrete implementations for different providers:

- `LLMClient`: Abstract base class defining the interface for LLM clients
- `OpenAIClient`: Implementation for OpenAI's API

### MCP Tool Client

The `MCPToolClient` class provides a way to use an LLM to call MCP tools:

1. It formats the available MCP tools in a way that the LLM can understand
2. It sends the user's prompt to the LLM along with the tool definitions
3. It processes any tool calls made by the LLM and returns the results

### Usage Examples

#### Command-line Example

You can use the `services/sample/llm_example.py` script to test the LLM integration:

```bash
python -m services.sample.llm_example "Calculate 5 plus 7"
```

This will:
1. Send the prompt to the LLM
2. The LLM will recognize that it should use the `calculate` tool
3. The tool will be called with the appropriate arguments
4. The result will be returned

#### REST API Endpoint

The service also provides a REST API endpoint for LLM processing:

```
POST /llm/process
```

**Request:**
```json
{
  "prompt": "Say hello to John",
  "system_message": "You are a helpful assistant that can use tools to help the user.",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "I'll say hello to John for you!",
    "tool_results": [
      {
        "tool_name": "get_greeting",
        "arguments": {
          "name": "John"
        },
        "result": {
          "greeting": "Hello, John! Welcome to the MCP sample service.",
          "timestamp": "2023-05-06T12:34:56.789012"
        },
        "error": null
      }
    ]
  },
  "timestamp": "2023-05-06T12:34:56.789012"
}
```

## Environment Variables

The application can be configured using the following environment variables:

```
# Application settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# OpenAI settings
OPENAI_API_KEY=your-openai-api-key
OPENAI_ORGANIZATION=your-openai-organization-id
OPENAI_MODEL=gpt-4o

# LLM general settings
LLM_PROVIDER=openai
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# MCP client settings
MCP_BASE_URL=http://localhost:8000
MCP_TIMEOUT=30.0
```

## License

MIT
