"""The app's main file.

This script provides the main app script for the Flask API application within the `create_app` method.

Additionally, it directly exports the following objects:

    * models: module that provides the fundamental models necessary to represent this app's data.
    * Database: class that abstracts common database functionality.
    * Permissions: integer flag that represents all permissions granted to the user
    * Sample: class that represents the data for a sample.
    * User: class that represents a user.
"""

import logging
from http import HTTPStatus
from typing import Any, Mapping

import flask
import pymysql
from flask_jwt_extended import JWTManager

from autospatialqc_api import models
from autospatialqc_api.environment import require_env, require_envs
from autospatialqc_api.models import Database, Permissions, Sample, User
from autospatialqc_api.models.errors import ResponseError
from autospatialqc_api.routes import authentication_blueprint, samples_blueprint

__all__ = [
    # Sub-Modules
    "models",
    # Classes
    "Database",
    "Permissions",
    "Sample",
    "User",
]


def create_app(test_config: Mapping[str, Any] | None = None) -> flask.Flask:
    """Create main Flask app.

    Arguments:
        test_config (Mapping[str, Any] | None): test configuration.

    Returns:
        The Flask app for the API.
    """

    app = flask.Flask(__name__, instance_relative_config=True)

    # Configure logging
    if app.debug:
        file_handler = logging.FileHandler("logs/debug.log", mode="w")
    else:
        file_handler = logging.FileHandler("logs/app.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    app.config.from_mapping(
        JWT_SECRET_KEY=require_env("JWT_SECRET_KEY"),
    )

    JWTManager(app)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.before_request
    def _():
        if "database" not in flask.g:
            flask.g.database = Database(
                **require_envs(
                    host="DB_HOST",
                    database="DB_NAME",
                    username="DB_USERNAME",
                    password="DB_PASSWORD",
                )
            )

    @app.errorhandler(ResponseError)
    def _(error: ResponseError) -> flask.Response:
        return error.response

    @app.errorhandler(pymysql.Error)
    def _(error: pymysql.Error) -> flask.Response:
        logging.error(f"Unhandled PyMySQL error raised: {str(error)}.")
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    app.register_blueprint(authentication_blueprint)
    app.register_blueprint(samples_blueprint)

    return app
