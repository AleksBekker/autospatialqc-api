"""Module containing blueprints for the API routes.

There are two main groupings of routes: authentication and samples. These are represented in the following exported
blueprints:

    * authentication_blueprint: blueprint containing authentication API routes.
    * samples_blueprint: blueprint containing sample data API routes.
"""

from autospatialqc_api.routes.authentication import blueprint as authentication_blueprint
from autospatialqc_api.routes.samples import blueprint as samples_blueprint

__all__ = [
    "authentication_blueprint",
    "samples_blueprint",
]
