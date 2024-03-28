from http import HTTPStatus

import flask
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from autospatialqc_api.models import Database, Permissions, User
from autospatialqc_api.models.errors import InvalidCredentials, ResponseError, UserCollision, UserNotFound
from autospatialqc_api.routes.route_utils import require_data, require_data_item, require_permission

blueprint = Blueprint("authentication", __name__)


@blueprint.route("/login", methods=["POST"])
def login():

    database: Database = flask.g.database  # type: ignore[annotation-unchecked]

    data = require_data(request, "email", "password")

    try:
        user = database.get_user(**data)
    except (UserNotFound, InvalidCredentials) as e:
        raise ResponseError.make_response("Invalid credentials", HTTPStatus.UNAUTHORIZED, str(e))

    access_token = create_access_token(identity=dict(user))

    return jsonify(access_token=access_token), HTTPStatus.OK


@blueprint.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():

    user = User(**get_jwt_identity())
    database: Database = flask.g.database  # type: ignore[annotation-unchecked]

    new_password = require_data_item(request, "new-password")

    try:
        database.change_password(user.email, new_password)
    except UserNotFound as e:
        raise ResponseError.make_response("The user associated with this JWT does not exist.", HTTPStatus.UNAUTHORIZED,
                                          str(e))

    return make_response("Password successfully changed.", HTTPStatus.OK)


@blueprint.route("/create-user", methods=["POST"])
@jwt_required()
def create_user():
    """Route to create a new user."""

    user = User(**get_jwt_identity())
    database: Database = flask.g.database  # type: ignore[annotation-unchecked]

    require_permission(user, Permissions.CREATE_USER)

    data = require_data(request, "email", "password", "permissions", "first_name", "last_name")

    try:
        database.add_user(**data)
    except UserCollision as e:
        raise ResponseError.make_response(f"User '{data['email']}' already exists.", HTTPStatus.CONFLICT, str(e))

    return make_response("User created successfully.", HTTPStatus.OK)
