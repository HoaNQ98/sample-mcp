import os
import yaml
from typing import Dict, Any

from services.sample.domain.use_cases import GreetingUseCase, CalculationUseCase


class GreetingController:
    """Controller for greeting-related endpoints."""
    
    def __init__(self):
        self.use_case = GreetingUseCase()
    
    def get_greeting(self, name: str) -> Dict[str, Any]:
        """Get a greeting for the given name."""
        return self.use_case.generate_greeting(name)


class CalculationController:
    """Controller for calculation-related endpoints."""
    
    def __init__(self):
        self.use_case = CalculationUseCase()
    
    def calculate(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """Perform a calculation."""
        return self.use_case.calculate(operation, a, b)


class HealthController:
    """Controller for health-related endpoints."""
    
    def get_health(self) -> Dict[str, Any]:
        """Get the health status of the service."""
        return {
            "status": "healthy",
            "message": "Service is running"
        }


class InfoController:
    """Controller for info-related endpoints."""
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the service."""
        # Load MCP configuration to include tools
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_tool.yaml")
        with open(config_path, "r") as f:
            mcp_config = yaml.safe_load(f)
        
        return {
            "name": mcp_config.get("name", "sample-mcp"),
            "version": mcp_config.get("version", "0.1.0"),
            "description": mcp_config.get("description", "Sample MCP server with clean architecture"),
            "tools": mcp_config.get("tools", []),
            "resources": mcp_config.get("resources", [])
        }
