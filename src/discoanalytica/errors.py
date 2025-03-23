class DataDefinitionError(Exception):
    """Custom exception for data source errors."""

    pass


class BadHashError(Exception):
    """Custom exception for failed hash match."""

    pass

class FileValidationError(Exception):
    """Custom exception raised when file validation fails."""
    pass
