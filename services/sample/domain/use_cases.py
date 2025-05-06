from datetime import datetime
from typing import Dict, Any

from services.sample.domain.entities import Greeting, Calculation


class GreetingUseCase:
    """Use case for generating greetings."""
    
    def generate_greeting(self, name: str) -> Dict[str, Any]:
        """Generate a greeting for the given name."""
        greeting_text = f"Hello, {name}! Welcome to the MCP sample service."
        now = datetime.now()
        
        greeting = Greeting(
            name=name,
            greeting=greeting_text,
            timestamp=now
        )
        
        return {
            "greeting": greeting.greeting,
            "timestamp": greeting.timestamp.isoformat()
        }


class CalculationUseCase:
    """Use case for performing calculations."""
    
    def calculate(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """Perform a calculation based on the given operation and operands."""
        calculation = Calculation(
            operation=operation,
            a=a,
            b=b
        )
        
        if operation == "add":
            calculation.result = a + b
        elif operation == "subtract":
            calculation.result = a - b
        elif operation == "multiply":
            calculation.result = a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            calculation.result = a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            "result": calculation.result,
            "operation": calculation.operation
        }
