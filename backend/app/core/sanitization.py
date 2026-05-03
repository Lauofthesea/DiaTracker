"""
Input sanitization utilities to prevent XSS and SQL injection.
"""

import re
import html
from typing import Any, Dict, List, Union


class InputSanitizer:
    """Service for sanitizing user inputs."""
    
    # Patterns for detecting potential attacks
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(--)",
        r"(;.*--)",
        r"(\'\s*OR\s*\'.+\'\s*=\s*\')",
        r"(\'\s*AND\s*\'.+\'\s*=\s*\')",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize a string input by escaping HTML and removing dangerous patterns.
        
        Args:
            value: The string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Truncate to max length
        value = value[:max_length]
        
        # Escape HTML entities
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        return value.strip()
    
    @staticmethod
    def detect_sql_injection(value: str) -> bool:
        """
        Detect potential SQL injection attempts.
        
        Args:
            value: The string to check
            
        Returns:
            True if potential SQL injection detected
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_xss(value: str) -> bool:
        """
        Detect potential XSS attempts.
        
        Args:
            value: The string to check
            
        Returns:
            True if potential XSS detected
        """
        if not isinstance(value, str):
            return False
        
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], string_fields: List[str]) -> Dict[str, Any]:
        """
        Sanitize specific string fields in a dictionary.
        
        Args:
            data: Dictionary containing data to sanitize
            string_fields: List of field names to sanitize
            
        Returns:
            Dictionary with sanitized fields
        """
        sanitized = data.copy()
        for field in string_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = InputSanitizer.sanitize_string(sanitized[field])
        return sanitized
    
    @staticmethod
    def validate_safe_input(value: str) -> bool:
        """
        Validate that input is safe (no SQL injection or XSS).
        
        Args:
            value: The string to validate
            
        Returns:
            True if input is safe
        """
        if InputSanitizer.detect_sql_injection(value):
            return False
        if InputSanitizer.detect_xss(value):
            return False
        return True


# Global sanitizer instance
input_sanitizer = InputSanitizer()
