"""
shouldpy - AI-driven test assertion decorator

Usage:
    from shouldpy import should
    
    # Configure LLM
    should.use(llm_client)
    
    # Use as decorator
    @should("Expected condition")
    def test_function():
        return some_result()
"""

from .should import should, ShouldDecorator

__version__ = "0.1.0"
__author__ = "zx"
__email__ = "your-email@example.com"
__description__ = "AI-driven test assertion decorator for natural language testing"

__all__ = ["should", "ShouldDecorator"]