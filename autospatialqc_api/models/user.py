from __future__ import annotations

from enum import IntFlag, auto

import pydantic


class Permissions(IntFlag):
    """Integer flag that represents a user permission."""

    NONE = 0

    # Sample permissions
    GET_SAMPLE = auto()
    POST_SAMPLE = auto()
    DELETE_SAMPLE = auto()

    # Authentication permissions
    CREATE_USER = auto()
    CHANGE_PASSWORD = auto()

    # Add all new variants to the `from_str` method

    @classmethod
    def from_str(cls, permission_str: str) -> Permissions:
        """Initalize a Permissions object from a string.

        Arguments:
            permission_str (str): a string that represents the Permissions object. Valid strings are "get_sample",
              "post_sample", "delete_sample", "create_user", and "change_password".

        Returns:
            The Permissions object associated with the string if it is valid, Permissions.NONE otherwise.
        """

        name_map = {
            "get_sample": Permissions.GET_SAMPLE,
            "post_sample": Permissions.POST_SAMPLE,
            "delete_sample": Permissions.DELETE_SAMPLE,
            "create_user": Permissions.CREATE_USER,
            "change_password": Permissions.CHANGE_PASSWORD,
            # Any string added here should also be added to the "permission_str" argument in the docstring
        }

        if permission_str in name_map:
            return name_map[permission_str]

        return Permissions.NONE


class User(pydantic.BaseModel):
    id: int
    email: str
    permissions: Permissions

    authenticated: bool = False
    first_name: str | None = None
    last_name: str | None = None
