"""
Custom exceptions for Qwen Image API interactions.
"""

class QwenAPIError(Exception):
    """Base exception for Qwen API errors."""
    pass

class QwenAPIConfigurationError(QwenAPIError):
    """Exception raised when API configuration is invalid."""
    pass

class QwenAPIAuthenticationError(QwenAPIError):
    """Exception raised when API authentication fails."""
    pass

class QwenAPIRequestError(QwenAPIError):
    """Exception raised when API request fails."""
    pass

class QwenAPIResponseError(QwenAPIError):
    """Exception raised when API response cannot be processed."""
    pass