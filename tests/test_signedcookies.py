"""SignedCookies tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from werkzeug.test import Cookie


def test_default_setcookie(client: FlaskClient) -> None:
    response = client.get("/set-cookie-default")

    assert response.status_code == 200
    assert "test_default_cookie=" in response.headers["Set-Cookie"]
    assert "=test_default_value" in response.headers["Set-Cookie"]

    cookie: Cookie = client.get_cookie("test_default_cookie")
    assert cookie.value == "test_default_value"


def test_signed_setcookie(client: FlaskClient) -> None:
    s = client.application.signed_cookies

    response = client.get("/set-cookie-signed")
    assert response.status_code == 200

    cookie: Cookie = client.get_cookie("test_signed_cookie")
    assert cookie is None

    cookie: Cookie = client.get_cookie(s.hash_name("test_signed_cookie"))
    assert cookie is not None
    assert cookie.value != "test_signed_value"


def test_signed_deletecookie(client: FlaskClient) -> None:
    s = client.application.signed_cookies

    response = client.get("/set-cookie-signed")
    assert response.status_code == 200

    cookie: Cookie = client.get_cookie(s.hash_name("test_signed_cookie"))
    assert cookie is not None
    assert cookie.value != "test_signed_value"

    response = client.get("/delete-cookie-signed")
    assert response.status_code == 200

    cookie: Cookie = client.get_cookie(s.hash_name("test_signed_cookie"))
    assert cookie is None
