class NotFoundException(Exception):
    """Exception raised when a resource is not found."""
    pass

class ValidationException(Exception):
    """Exception raised for validation errors."""
    pass

class UnauthorizedException(Exception):
    """Exception raised for authorization errors."""
    pass

class BusinessRuleException(Exception):
    """Exception raised for business rule violations."""
    pass