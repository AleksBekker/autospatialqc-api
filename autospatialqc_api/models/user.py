from __future__ import annotations

from enum import IntFlag, auto
from functools import reduce
from operator import or_ as bit_or
from typing import Iterable

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
    def from_str(cls, *permission_strs: str) -> Permissions:
        """Initalize a Permissions object from a string.

        Arguments:
            permission_strs (str): strings that represent the Permissions object. Valid strings are "get_sample",
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

        return reduce(
            bit_or,
            (name_map[permission_str] for permission_str in permission_strs if permission_str in name_map),
            Permissions.NONE,
        )


class User(pydantic.BaseModel):
    "Represents an API user."

    id: int
    email: str
    permissions: Permissions

    authenticated: bool = False
    first_name: str | None = None
    last_name: str | None = None
