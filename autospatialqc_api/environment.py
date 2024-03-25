"""Environmental variable and dotenv file parsing.

This file contains functions that handle environmental variables in shell script environmental variables, '.env.shared',
and '.env.secret', in order of increasing priority.

This file's main use is as an imported module, which contains the following objects:

    * get_env: method for getting an environmental variable that may not exist.
    * require_env: method for getting an environmental variable that must exist.
    * RequiredEnvironmentalUnprovided: exception for when a required environmental can't be found.
"""

import os

from dotenv import dotenv_values

_dotenv_variables = {**dotenv_values(".env.shared"), **dotenv_values(".env.secret")}


def get_env(identifier: str) -> str | None:
    """Get an environmental variable.

    Arguments:
        identifier (str): the name of the environmental variable.

    Returns:
        A string containing the data in the identified variable in the `.env`s or shell environment, or `None` if they
          don't exist.
    """

    if identifier in _dotenv_variables:
        return _dotenv_variables[identifier]

    return os.getenv(identifier)


class RequiredEnvironmentalUnprovided(Exception):
    """Raised when a required environmental variable is not provided."""

    def __init__(self, identifier: str):
        """Raised when a required environmental variable is not provided.

        Arguments:
            identifier (str): the name of the environmental variable.
        """

        super().__init__(f"Environmental variable '{identifier}' required, but not provided.")


def require_env(identifier: str) -> str:
    """Require an environmental variable.

    Arguments:
        identifier (str): the name of the environmental variable.

    Returns:
        A string containing the data in the identified variable.

    Raises:
        RequiredEnvironmentalUnprovided: if this environmental variable is not provided.
    """

    if (env_var := get_env(identifier)) is None:
        raise RequiredEnvironmentalUnprovided(identifier)

    return env_var
