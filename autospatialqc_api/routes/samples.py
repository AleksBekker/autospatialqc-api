import logging
from http import HTTPStatus

import flask
from flask import Blueprint, Response, current_app, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from autospatialqc_api.models import Database, Permissions, Sample, User
from autospatialqc_api.models.errors import SampleNameCollision, SampleNotFound

blueprint = Blueprint("samples", __name__)


@blueprint.route("/sample", methods=["GET", "DELETE", "POST"])
@jwt_required()
def get_sample() -> Response:

    user = User(**get_jwt_identity())
    database: Database = flask.g.database

    if not user.authenticated:
        return make_response("User not authenticated. Please use the login route first.", HTTPStatus.UNAUTHORIZED)

    if request.method == "GET":

        if Permissions.GET_SAMPLE not in user.permissions:
            current_app.logger.info(
                f"User '{user.email}' attempted to access a sample without 'get_sample' permissions."
            )
            return make_response(
                f"User '{user.email}' does not have permission to get samples.", HTTPStatus.UNAUTHORIZED
            )

        if not (assay := request.args.get("assay")):
            return make_response("Assay not detected in query string.", HTTPStatus.BAD_REQUEST)

        if not (tissue := request.args.get("tissue")):
            return make_response("Tissue not detected in query string.", HTTPStatus.BAD_REQUEST)

        try:
            sample = database.get_sample(assay, tissue)
        except SampleNotFound:
            return make_response("Sample not found.", HTTPStatus.NOT_FOUND)

        current_app.logger.info(f"Sample '{assay} {tissue}' successfully returned.")
        return make_response(dict(sample), HTTPStatus.OK)

    if request.method == "DELETE":

        if not user.authenticated:
            return make_response("User not authenticated. Please use the login route first.", HTTPStatus.UNAUTHORIZED)

        if Permissions.DELETE_SAMPLE not in user.permissions:
            return make_response(
                f"User {user.email} does not have permission to delete samples.", HTTPStatus.UNAUTHORIZED
            )

        if not (json := request.get_json()):
            return make_response("Missing JSON in request.", HTTPStatus.BAD_REQUEST)

        if not (assay := request.args.get("assay")):
            return make_response("Assay not detected in query string.", HTTPStatus.BAD_REQUEST)

        if not (tissue := request.args.get("tissue")):
            return make_response("Tissue not detected in query string.", HTTPStatus.BAD_REQUEST)

        try:
            database.delete_sample(assay, tissue)
        except SampleNotFound:
            return make_response("Sample not found.", HTTPStatus.NOT_FOUND)

        current_app.logger.info(f"Sample '{assay} {tissue}' successfully deleted by user '{user.email}'.")
        return make_response("Sample successfully deleted.", HTTPStatus.OK)

    if request.method == "POST":

        if not user.authenticated:
            return make_response("User not authenticated. Please use the login route first.", HTTPStatus.UNAUTHORIZED)

        if Permissions.POST_SAMPLE not in user.permissions:
            return make_response(
                f"User {user.email} does not have permission to post samples.", HTTPStatus.UNAUTHORIZED
            )

        if not (json := request.get_json()):
            return make_response("Missing JSON in request.", HTTPStatus.BAD_REQUEST)

        try:
            database.insert_sample(Sample.model_validate(json))
        except ValidationError:
            return make_response("Sample could not be validated.", HTTPStatus.BAD_REQUEST)
        except SampleNameCollision:
            return make_response("New sample conflicts with another sample.", HTTPStatus.CONFLICT)

        return make_response("New sample pushed.", HTTPStatus.OK)

    flask.abort(HTTPStatus.METHOD_NOT_ALLOWED)
