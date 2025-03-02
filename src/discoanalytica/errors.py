class DataDefinitionError(Exception):
    """Custom exception for data source errors."""

    pass


class BadHashError(Exception):
    """Custom exception for failed hash match."""

    pass


class UnknownOperation(Exception):
    """Custom Exception for unrecognized operation in a data pipeline."""

    pass
