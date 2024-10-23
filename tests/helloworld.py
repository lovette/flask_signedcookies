"""Simple Flask app for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Flask, make_response

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask import Response


# Based on:
# https://flask.palletsprojects.com/en/3.0.x/testing/
# https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/

# This key is used by SecureCookieSessionInterface:get_signing_serializer to sign cookies
APP_SECRET_KEY = "blah"  # noqa: S105


def create_app(test_config: Mapping | None = None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=APP_SECRET_KEY,
    )

    @app.route("/set-cookie-default")
    def _set_cookie_default() -> Response:
        response = make_response("Default cookie set!")
        response.set_cookie("test_default_cookie", "test_default_value")
        return response

    @app.route("/set-cookie-signed")
    def _set_cookie_signed() -> Response:
        app.set_cookie("test_signed_cookie", "test_signed_value")
        return make_response("Signed cookie set!")

    @app.route("/delete-cookie-signed")
    def _delete_cookie_signed() -> Response:
        app.delete_cookie("test_signed_cookie")
        return make_response("Signed cookie deleted!")

    return app
