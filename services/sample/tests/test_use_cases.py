import unittest
from datetime import datetime

from services.sample.domain.use_cases import GreetingUseCase, CalculationUseCase


class TestGreetingUseCase(unittest.TestCase):
    """Test cases for GreetingUseCase."""
    
    def setUp(self):
        self.use_case = GreetingUseCase()
    
    def test_generate_greeting(self):
        """Test generate_greeting method."""
        name = "John"
        result = self.use_case.generate_greeting(name)
        
        self.assertIn("greeting", result)
        self.assertIn("timestamp", result)
        self.assertIn(name, result["greeting"])
        
        # Try to parse the timestamp
        try:
            datetime.fromisoformat(result["timestamp"])
        except ValueError:
            self.fail("Timestamp is not in ISO format")


class TestCalculationUseCase(unittest.TestCase):
    """Test cases for CalculationUseCase."""
    
    def setUp(self):
        self.use_case = CalculationUseCase()
    
    def test_add(self):
        """Test add operation."""
        result = self.use_case.calculate("add", 2, 3)
        self.assertEqual(result["result"], 5)
        self.assertEqual(result["operation"], "add")
    
    def test_subtract(self):
        """Test subtract operation."""
        result = self.use_case.calculate("subtract", 5, 3)
        self.assertEqual(result["result"], 2)
        self.assertEqual(result["operation"], "subtract")
    
    def test_multiply(self):
        """Test multiply operation."""
        result = self.use_case.calculate("multiply", 2, 3)
        self.assertEqual(result["result"], 6)
        self.assertEqual(result["operation"], "multiply")
    
    def test_divide(self):
        """Test divide operation."""
        result = self.use_case.calculate("divide", 6, 3)
        self.assertEqual(result["result"], 2)
        self.assertEqual(result["operation"], "divide")
    
    def test_divide_by_zero(self):
        """Test divide by zero."""
        with self.assertRaises(ValueError):
            self.use_case.calculate("divide", 6, 0)
    
    def test_unknown_operation(self):
        """Test unknown operation."""
        with self.assertRaises(ValueError):
            self.use_case.calculate("unknown", 2, 3)


if __name__ == "__main__":
    unittest.main()
