"""Environmental variable and dotenv file parsing.

This file contains functions that handle environmental variables in shell script environmental variables, '.env.shared',
and '.env.secret', in order of increasing priority.

This file's main use is as an imported module, which contains the following objects:

    * get_env: method for getting an environmental variable that may not exist.
    * require_env: method for getting an environmental variable that must exist.
    * RequiredEnvironmentalUnprovided: exception for when a required environmental can't be found.
"""

import os
from typing import Dict, Optional

from dotenv import dotenv_values

_dotenv_variables = {**dotenv_values(".env.shared"), **dotenv_values(".env.secret")}


def get_env(identifier: str) -> Optional[str]:
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


def require_envs(*identifiers: str, **aliases: str) -> Dict[str, str]:
    """Require some environmental variables.

    Arguments:
        identifiers (str): list of environmental variable identifiers.
        aliases (str): alias to variable mappings.

    Returns:
        An identifier -> value mapping of all of the environmental variables.

    Raises:
        RequiredEnvironmentalUnprovided: if any environmental variable is not provided.
    """

    return {
        **{var: require_env(var) for var in identifiers},
        **{alias: require_env(var) for alias, var in aliases.items()},
    }
