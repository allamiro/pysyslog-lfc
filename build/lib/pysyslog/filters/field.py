"""
Field filter component for PySyslog LFC
"""

import logging
import re
from typing import Dict, Any, Callable
from .base import FilterComponent

class Filter(FilterComponent):
    """Filter messages based on field value comparisons.
    
    This filter allows comparing message field values against specified values
    using various operators. It supports string, numeric, and boolean comparisons,
    with case-sensitive and case-insensitive options for string comparisons.
    
    Configuration:
        - field: Field to compare (required)
        - operator: Comparison operator (required)
        - value: Value to compare against (required)
        - invert: Whether to invert the match (default: False)
        - case_sensitive: Whether string comparisons are case sensitive (default: True)
    """
    
    # Valid operators and their functions
    OPERATORS = {
        # String operators
        "equals": lambda x, y: str(x) == str(y),
        "not_equals": lambda x, y: str(x) != str(y),
        "contains": lambda x, y: str(y) in str(x),
        "not_contains": lambda x, y: str(y) not in str(x),
        "startswith": lambda x, y: str(x).startswith(str(y)),
        "endswith": lambda x, y: str(x).endswith(str(y)),
        "matches": lambda x, y: bool(re.match(str(y), str(x))),
        
        # Numeric operators
        "gt": lambda x, y: float(x) > float(y),
        "ge": lambda x, y: float(x) >= float(y),
        "lt": lambda x, y: float(x) < float(y),
        "le": lambda x, y: float(x) <= float(y),
        "eq": lambda x, y: float(x) == float(y),
        "ne": lambda x, y: float(x) != float(y),
        
        # Boolean operators
        "is_true": lambda x, y: bool(x) is True,
        "is_false": lambda x, y: bool(x) is False
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize field filter.
        
        Args:
            config: Configuration dictionary containing:
                - field: Field to compare
                - operator: Comparison operator
                - value: Value to compare against
                - invert: Whether to invert the match (default: False)
                - case_sensitive: Whether string comparisons are case sensitive (default: True)
                
        Raises:
            ValueError: If configuration is invalid
        """
        super().__init__(config)
        
        # Get and validate field
        self.field = config.get("field")
        if not self.field:
            raise ValueError("field parameter is required")
        self._validate_string(self.field, "field")
        
        # Get and validate operator
        self.operator = config.get("operator")
        if not self.operator:
            raise ValueError("operator parameter is required")
        if self.operator not in self.OPERATORS:
            raise ValueError(f"Invalid operator: {self.operator}. Must be one of: {', '.join(self.OPERATORS.keys())}")
        
        # Get and validate value
        self.value = config.get("value")
        if self.value is None:
            raise ValueError("value parameter is required")
        
        # Get optional parameters
        self.case_sensitive = bool(config.get("case_sensitive", True))
        
        # Get operator function
        self._operator_func = self.OPERATORS[self.operator]
        
        # Compile regex pattern if needed
        if self.operator == "matches":
            self._validate_string(self.value, "value")
            self.pattern = self._compile_pattern(self.value)
    
    def filter(self, data: Dict[str, Any]) -> bool:
        """Filter messages based on field value comparison.
        
        Args:
            data: Parsed message data
            
        Returns:
            bool: True if message should be kept, False if filtered out
        """
        try:
            # Get field value
            field_value = data.get(self.field)
            if field_value is None:
                return False
            
            # Apply operator
            result = self._operator_func(field_value, self.value)
            
            # Apply invert if specified
            if self.invert:
                result = not result
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error filtering message: {e}", exc_info=True)
            return False
    
    def close(self) -> None:
        """Cleanup resources."""
        pass 