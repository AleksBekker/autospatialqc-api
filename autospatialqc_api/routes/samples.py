from http import HTTPStatus

import flask
from flask import Blueprint, Request, Response, current_app, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from autospatialqc_api.models import Database, Permissions, Sample, User
from autospatialqc_api.models.errors import ResponseError, SampleNameCollision, SampleNotFound
from autospatialqc_api.routes.route_utils import require_arg, require_data, require_permission

blueprint = Blueprint("samples", __name__)


def delete_sample(request: Request, user: User, database: Database) -> Response:
    require_permission(user, Permissions.DELETE_SAMPLE)

    assay = require_arg(request, "assay")
    tissue = require_arg(request, "tissue")

    try:
        database.delete_sample(assay, tissue)
    except SampleNotFound as e:
        raise ResponseError.make_response("Sample not found.", HTTPStatus.NOT_FOUND, str(e))

    current_app.logger.info(f"Sample '{assay} {tissue}' successfully deleted by user '{user.email}'.")
    return make_response("Sample successfully deleted.", HTTPStatus.OK)


def get_sample(request: Request, user: User, database: Database) -> Response:

    require_permission(user, Permissions.GET_SAMPLE)

    assay = require_arg(request, "assay")
    tissue = require_arg(request, "tissue")

    try:
        sample = database.get_sample(assay, tissue)
    except SampleNotFound as e:
        raise ResponseError.make_response("Sample not found.", HTTPStatus.NOT_FOUND, str(e))

    current_app.logger.info(f"Sample '{assay} {tissue}' successfully returned.")
    return make_response(dict(sample), HTTPStatus.OK)


def post_sample(request: Request, user: User, database: Database) -> Response:

    require_permission(user, Permissions.POST_SAMPLE)
    data = require_data(request, *Sample.data_fields())

    try:
        database.add_sample(Sample.model_validate(data))
    except ValidationError as e:
        raise ResponseError.make_response("Sample could not be validated.", HTTPStatus.BAD_REQUEST, str(e))
    except SampleNameCollision as e:
        raise ResponseError.make_response("New sample conflicts with another sample.", HTTPStatus.CONFLICT, str(e))

    return make_response("New sample pushed.", HTTPStatus.OK)


@blueprint.route("/sample", methods=["GET", "DELETE", "POST"])
@jwt_required()
def sample() -> Response:

    user = User(**get_jwt_identity())
    database: Database = flask.g.database

    methods = {
        "DELETE": delete_sample,
        "GET": get_sample,
        "POST": post_sample,
    }

    if request.method in methods:
        return methods[request.method](request, user, database)

    raise ResponseError.make_response("The method is not allowed for the requested URL.", HTTPStatus.METHOD_NOT_ALLOWED)
