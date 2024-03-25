from http import HTTPStatus
from logging import Logger
from typing import Any

from flask import Request, make_response

from autospatialqc_api.models.errors import ResponseError
from autospatialqc_api.models.user import Permissions, User


def require_permission(user: User, permission: Permissions, logger: Logger | None = None):
    """Require a permission.

    Arguments:
        user (User): the user who needs to have the permission.
        permission (Permissions): the permissions required.
        logger (Logger): optional logger to which messages should be displayed.

    Raises:
        ResponseError: if the user is not authenticated or is missing permissions to use this route.
    """

    if not user.authenticated:

        if logger is not None:
            logger.info(f"User '{user.email}' attempted to access a route without being authenticated.")

        raise ResponseError(
            make_response(
                "The user is not authenticated. Please use the 'login' route to do so.",
                HTTPStatus.UNAUTHORIZED,
            )
        )

    if permission not in user.permissions:

        if logger is not None:
            logger.info(f"User '{user.email}' not authorized to use this route.")

        raise ResponseError(
            make_response(
                f"User '{user.email}' does not have permission to use this API route.",
                HTTPStatus.UNAUTHORIZED,
            )
        )

    return None


def require_data_item(request: Request, key: str, logger: Logger | None = None) -> Any:
    """Require an item in the request JSON.

    Arguments:
        request (Request): the Flask request.
        key (str): the key of the required data.
        logger (Logger): optional logger to which messages should be displayed.

    Returns:
        The value of the required data if it exists.

    Raises:
        ResponseError: if the value is missing from the JSON.
    """

    if (json := request.json) is None:

        if logger is not None:
            logger.info("Missing JSON in request.")

        raise ResponseError(make_response("Missing JSON in request", HTTPStatus.BAD_REQUEST))

    if (value := json.get(key, None)) is None:

        if logger is not None:
            logger.info(f"Missing JSON key '{key}' in request.", HTTPStatus.BAD_REQUEST)

        raise ResponseError(make_response(f"Missing JSON key '{key}' in request.", HTTPStatus.BAD_REQUEST))

    return value


def require_data(request: Request, *keys: str, logger: Logger | None = None, **aliases: str) -> dict[str, Any]:
    """Require data in the request JSON.

    Arguments:
        request (Request): the Flask request.
        *keys (str): the keys of the required data.
        logger (Logger): optional logger to which messages should be displayed.
        **aliases (str): an alias to variable mapping of all variables to rename.

    Returns:
        A dictionary with all required data if it exists.

    Raises:
        ResponseError: if any of the required keys are missing.
    """

    return {key: require_data_item(request, key, logger=logger) for key in keys} \
        | {alias: require_data_item(request, var, logger=logger) for alias, var in aliases.items()}


def require_arg(request: Request, key: str) -> str:
    """Require an argument in the request URL.

    Arguments:
        request (Request): the Flask request.
        key (str): the key of the required argument.

    Raises:
        ResponseError: if the required argument are missing.
    """

    if (value := request.args.get(key, None)) is None:
        raise ResponseError(make_response(f"Missing argument '{key}' from URL.", HTTPStatus.BAD_REQUEST))
    return value
