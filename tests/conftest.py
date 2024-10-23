"""Define fixtures accessible to all tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flask_signedcookies import SignedCookies

from .helloworld import create_app

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner


@pytest.fixture
def app() -> Flask:
    app = create_app()

    app.config.update(
        {
            "TESTING": True,
        },
    )

    # `signed_cookies` does not have to be an `app` property,
    # but it makes sense here to keep it in scope for the test.
    app.signed_cookies = SignedCookies()
    app.signed_cookies.init_app(app)

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
