from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Union, Optional


@dataclass
class Greeting:
    """Greeting entity."""
    name: str
    greeting: str
    timestamp: datetime


@dataclass
class Calculation:
    """Calculation entity."""
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float
    b: float
    result: Optional[float] = None
