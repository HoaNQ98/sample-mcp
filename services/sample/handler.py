import logging
from typing import Dict, Any, Optional

from services.sample.api.controllers import (
    GreetingController,
    CalculationController,
    HealthController,
    InfoController
)

logger = logging.getLogger(__name__)


class MCPHandler:
    """Handler for MCP requests."""
    
    def __init__(self):
        logger.info("Initializing MCP handler")
        self.greeting_controller = GreetingController()
        self.calculation_controller = CalculationController()
        self.health_controller = HealthController()
        self.info_controller = InfoController()
    
    async def handle_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool request."""
        logger.debug(f"Handling tool: {tool_name} with arguments: {arguments}")
        
        try:
            if tool_name == "get_greeting":
                logger.info(f"Processing get_greeting for name: {arguments.get('name')}")
                return self.greeting_controller.get_greeting(name=arguments["name"])
            elif tool_name == "calculate":
                logger.info(f"Processing calculation: {arguments.get('operation')} with operands {arguments.get('a')} and {arguments.get('b')}")
                return self.calculation_controller.calculate(
                    operation=arguments["operation"],
                    a=arguments["a"],
                    b=arguments["b"]
                )
            else:
                logger.warning(f"Unknown tool requested: {tool_name}")
                raise ValueError(f"Unknown tool: {tool_name}")
        except KeyError as e:
            logger.error(f"Missing required argument for {tool_name}: {e}")
            raise ValueError(f"Missing required argument: {e}")
        except Exception as e:
            logger.error(f"Error handling tool {tool_name}: {e}", exc_info=True)
            raise
    
    async def handle_resource(self, uri: str) -> Dict[str, Any]:
        """Handle an MCP resource request."""
        logger.debug(f"Handling resource: {uri}")
        
        try:
            if uri == "/health":
                logger.info("Processing health check")
                return self.health_controller.get_health()
            elif uri == "/info":
                logger.info("Processing info request")
                return self.info_controller.get_info()
            else:
                logger.warning(f"Unknown resource URI requested: {uri}")
                raise ValueError(f"Unknown resource URI: {uri}")
        except Exception as e:
            logger.error(f"Error handling resource {uri}: {e}", exc_info=True)
            raise


# Create a singleton instance
mcp_handler = MCPHandler()
