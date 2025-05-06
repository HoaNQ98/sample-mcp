import os
import yaml
import logging
from fastapi import FastAPI, Request, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import uvicorn

from services.sample.config import get_settings, setup_app_logging
from services.sample.handler import mcp_handler
from shared.responses.api_response import APIResponse, ErrorResponse, ErrorDetail
from shared.responses.mcp_response import MCPResponse
from shared.llms import create_mcp_tool_client

# Set up logging
setup_app_logging()
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title=get_settings().APP_NAME,
    description=get_settings().APP_DESCRIPTION,
    version=get_settings().APP_VERSION,
)

# Add exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    details = []
    for error in exc.errors():
        details.append(
            ErrorDetail(
                loc=error.get("loc", []),
                msg=error.get("msg", ""),
                type=error.get("type", ""),
            )
        )
    return JSONResponse(
        status_code=422,
        content=APIResponse.error(
            message="Validation Error",
            code=422,
            details=details,
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="Internal Server Error",
            code=500,
        ).model_dump(),
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load MCP configuration
def load_mcp_config():
    """Load MCP configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "mcp_tool.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


mcp_config = load_mcp_config()


# MCP endpoints
@app.post("/mcp/tool/{tool_name}")
async def mcp_tool(tool_name: str, request: Request):
    """Handle MCP tool requests."""
    logger.info(f"Received MCP tool request: {tool_name}")
    
    # Check if tool exists in configuration
    tool_exists = False
    for tool in mcp_config.get("tools", []):
        if tool["name"] == tool_name:
            tool_exists = True
            break
    
    if not tool_exists:
        logger.warning(f"Tool not found: {tool_name}")
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    # Parse request body
    try:
        arguments = await request.json()
        logger.debug(f"Tool arguments: {arguments}")
    except Exception as e:
        logger.error(f"Invalid JSON body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    # Handle tool request
    try:
        result = await mcp_handler.handle_tool(tool_name, arguments)
        logger.info(f"Tool {tool_name} executed successfully")
        return JSONResponse(content=MCPResponse.success_response(result))
    except ValueError as e:
        logger.error(f"Value error in tool {tool_name}: {e}")
        return JSONResponse(
            status_code=400,
            content=MCPResponse.error_response(str(e)),
        )
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=MCPResponse.error_response("Internal Server Error"),
        )


@app.get("/mcp/resource{uri:path}")
async def mcp_resource(uri: str):
    """Handle MCP resource requests."""
    logger.info(f"Received MCP resource request: {uri}")
    
    # Check if resource exists in configuration
    resource_exists = False
    for resource in mcp_config.get("resources", []):
        if resource["uri"] == uri:
            resource_exists = True
            break
    
    if not resource_exists:
        logger.warning(f"Resource not found: {uri}")
        raise HTTPException(status_code=404, detail=f"Resource '{uri}' not found")
    
    # Handle resource request
    try:
        result = await mcp_handler.handle_resource(uri)
        logger.info(f"Resource {uri} accessed successfully")
        return JSONResponse(content=MCPResponse.success_response(result))
    except ValueError as e:
        logger.error(f"Value error in resource {uri}: {e}")
        return JSONResponse(
            status_code=400,
            content=MCPResponse.error_response(str(e)),
        )
    except Exception as e:
        logger.error(f"Error accessing resource {uri}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=MCPResponse.error_response("Internal Server Error"),
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    result = await mcp_handler.handle_resource("/health")
    return APIResponse.success(data=result)


# Info endpoint
@app.get("/info")
async def info():
    """Info endpoint."""
    logger.info("Info requested")
    result = await mcp_handler.handle_resource("/info")
    # Return raw result for MCP client compatibility
    return result


# LLM request model
class LLMRequest(BaseModel):
    """LLM request model."""
    
    prompt: str
    system_message: str = None
    temperature: float = 0.7
    max_tokens: int = None


# LLM endpoint
@app.post("/llm/process")
async def process_with_llm(request: LLMRequest):
    """Process a prompt with the LLM and call MCP tools as needed."""
    logger.info(f"Received LLM request with prompt: {request.prompt}")
    
    try:
        # Create the MCP tool client
        mcp_client = await create_mcp_tool_client()
        
        try:
            # Process the prompt with the LLM
            result = await mcp_client.process_with_llm(
                prompt=request.prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            logger.info("LLM request processed successfully")
            return APIResponse.success(data=result)
        finally:
            # Close the MCP tool client
            await mcp_client.close()
    except Exception as e:
        logger.error(f"Error processing LLM request: {e}", exc_info=True)
        return APIResponse.error(
            message=f"Error processing LLM request: {str(e)}",
            code=500,
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return APIResponse.success(
        data={
            "message": "Welcome to the MCP sample service",
            "docs_url": "/docs",
            "health_check_url": "/health",
            "info_url": "/info",
            "llm_url": "/llm/process",
        }
    )


# Run the application
if __name__ == "__main__":
    logger.info(f"Starting application on {get_settings().HOST}:{get_settings().PORT}")
    uvicorn.run(
        "services.sample.main:app",
        host=get_settings().HOST,
        port=get_settings().PORT,
        reload=get_settings().DEBUG,
    )
