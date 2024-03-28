from __future__ import annotations

from http import HTTPStatus
from typing import Union

from flask import Response, make_response


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


class UserCollision(Exception):
    """Raised when a new user has unique information that already exists in the database."""

    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' already exists.")


class ResponseError(Exception):
    """Raised when a Flask response should be returned prematurely.

    Note:
        If this error reaches the main app, it is handled by returning the response to the user. As such, it is
          unneccessary to catch it.
    """

    def __init__(self, response: Response, *args):
        self.response = response
        super().__init__(*args)

    @classmethod
    def make_response(cls, response_message: str, code: Union[int, HTTPStatus], *args) -> ResponseError:
        return cls(make_response(response_message, code), *args)
