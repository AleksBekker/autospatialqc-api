from http import HTTPStatus

import flask
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from autospatialqc_api.models import Database, Permissions, User
from autospatialqc_api.models.errors import InvalidCredentials, UserNotFound

blueprint = Blueprint("authentication", __name__)


@blueprint.route("/login", methods=["POST"])
def login():

    database: Database = flask.g.database  # type: ignore[annotation-unchecked]

    if not (json := request.json):
        return make_response("Missing JSON in request", HTTPStatus.BAD_REQUEST)

    if not (email := json.get("email", None)):
        return make_response("Missing email in request", HTTPStatus.BAD_REQUEST)

    if not (password := json.get("password", None)):
        return make_response("Missing password in request", HTTPStatus.BAD_REQUEST)

    try:
        user = database.get_validated_user(email, password)
    except (UserNotFound, InvalidCredentials):
        return make_response("Invalid credentials", HTTPStatus.UNAUTHORIZED)

    access_token = create_access_token(identity=dict(user))

    return jsonify(access_token=access_token), HTTPStatus.OK


@blueprint.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():

    user = User(**get_jwt_identity())
    database: Database = flask.g.database  # type: ignore[annotation-unchecked]

    if not user.authenticated:
        return make_response("User not authenticated. Please use the login node.", HTTPStatus.UNAUTHORIZED)

    if Permissions.CHANGE_PASSWORD not in user.permissions:
        return make_response(
            f"User {user.email} does not have permission to change their password.", HTTPStatus.UNAUTHORIZED
        )

    if not (json := request.json):
        return make_response("Missing JSON in request", HTTPStatus.BAD_REQUEST)

    if not (new_password := json.get("new-password", None)):
        return make_response("Missing new password in request", HTTPStatus.BAD_REQUEST)

    try:
        database.change_password(user, new_password.encode("utf-8"))
    except UserNotFound:
        return make_response("The user associated with this JWT does not exist.", HTTPStatus.UNAUTHORIZED)

    return make_response("Password successfully changed.", HTTPStatus.OK)
