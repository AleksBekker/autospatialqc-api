class InsufficientPermissions(Exception):
    """Raised when a user is not permitted to perform the action they're attempting."""

    def __init__(self, email: str, action: str):
        super().__init__(f"User with email '{email}' not authorized to perform action '{action}'.")


class UserNotFound(Exception):
    """Raised when a user is not found in a database."""

    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' not found.")


class InvalidCredentials(Exception):
    """Raised when a user's password is invalid."""

    def __init__(self):
        super().__init__("The inputed credentials are not valid.")


class SampleNotFound(Exception):
    """Raised when a sample is not found in the database."""

    def __init__(self, assay: str, tissue: str) -> None:
        super().__init__(f"The sample '{assay} {tissue}' was not found in the database.")


class SampleNameCollision(Exception):
    """Raised when a `sample_name` already exists in the database while it's trying to be inserted."""
