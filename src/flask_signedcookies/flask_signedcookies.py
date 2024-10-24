"""Flask extension that provides easy access to signed cookies.

This module provides:
- SignedCookies
"""

from __future__ import annotations

import datetime
import hashlib
from typing import TYPE_CHECKING

from flask.sessions import SessionInterface
from itsdangerous import BadSignature

if TYPE_CHECKING:
    from datetime import timedelta

    from flask import Flask, Request, Response
    from itsdangerous.url_safe import Serializer


class SignedCookies:
    """Flask extension to provide easy access to signed cookies."""

    name_hash_method = staticmethod(hashlib.md5)
    """Hash method to encode cookie names. Default is md5. Set to None to disable."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__()

        self._app = None
        self._session_interface = None
        self._get_signed_cookies = {}
        self._set_signed_cookies = {}
        self._del_signed_cookies = {}

    def init_app(self, app: Flask, session_interface: SessionInterface | None = None, register_funcs: bool = True) -> None:
        """Initialize extension and application instance.

        Arguments:
            app (Flask): Flask application instance.

        Keyword Arguments:
            session_interface (SessionInterface, optional): Session interface instance.
                Any interface derived from ``flask.sessions.SessionInterface`` that provides a
                function named ``get_signing_serializer`` can be used (which the standard
                ``SecureCookieSessionInterface`` does). Default is to use ``app.session_interface``.
            register_funcs (bool, optional): Register cookie functions for ``app``. Default is True.

        Raises:
            ValueError: Session or Redis instance has not been set.
            TypeError: Session or Redis instance is not of correct type.
        """
        self._app = app
        self._session_interface = session_interface or app.session_interface

        if not isinstance(self._session_interface, SessionInterface):
            errmsg = f"{self!r} session_interface instance is type <{self._session_interface.__class__.__name__}> expected type <SessionInterface>"
            raise TypeError(errmsg)

        if not hasattr(self._session_interface, "get_signing_serializer"):
            errmsg = f"{self!r} session_interface instance does not have a 'get_signing_serializer' method"
            raise ValueError(errmsg)

        # Hook into request startup and teardown
        app.before_request(self.reset_cookies)
        app.after_request(self.save_cookies)

        # Add functions to application instance
        if register_funcs is True:
            app.get_cookie = self.get_cookie
            app.set_cookie = self.set_cookie
            app.delete_cookie = self.delete_cookie

    def reset_cookies(self) -> None:
        """Reset signed cookies.

        This occurs by default during request initialization.
        """
        self._get_signed_cookies = {}
        self._set_signed_cookies = {}
        self._del_signed_cookies = {}

    def save_cookies(self, response: Response) -> Response:
        """Add set-cookie headers for signed cookies.

        This occurs by default after the request is complete.

        Arguments:
            response (flask.Response): Response instance

        Returns:
            Response
        """
        # Set signed cookies
        for cookie_name, cookie in self._set_signed_cookies.items():
            signed_val = self.get_signing_serializer().dumps(cookie["unsigned_val"])
            response.set_cookie(
                self.hash_name(cookie_name),
                signed_val,
                max_age=cookie["max_age"],
                path=cookie["path"],
                domain=cookie["domain"],
                httponly=cookie["httponly"],
                secure=cookie["secure"],
            )

        # Delete signed cookies
        for cookie_name, cookie in self._del_signed_cookies.items():
            response.delete_cookie(self.hash_name(cookie_name), path=cookie["path"], domain=cookie["domain"])

        # Make safe to call save_cookies again, just in case
        self.reset_cookies()

        return response

    def get_cookie(self, request: Request, cookie_name: str, max_age: int | timedelta | None = None) -> str:
        """Get value of a signed cookie.

        Arguments:
            request (flask.Request): Request instance.
            cookie_name (string): Name of cookie.

        Keyword Arguments:
            max_age (int, datetime.timedelta, optional): Maximum age of value to accept, or None if value does not expire.

        Returns:
            mixed: Cookie value
        """
        if cookie_name not in self._get_signed_cookies:
            unsigned_val = None

            signed_val = request.cookies.get(self.hash_name(cookie_name))
            if signed_val is not None:
                try:
                    if isinstance(max_age, datetime.timedelta):
                        max_age = int(max_age.total_seconds()) or None
                    unsigned_val = self.get_signing_serializer().loads(signed_val, max_age=max_age)
                except BadSignature:
                    pass

            self._get_signed_cookies[cookie_name] = unsigned_val

        return self._get_signed_cookies[cookie_name]

    def set_cookie(  # noqa: PLR0913
        self,
        cookie_name: str,
        unsigned_val: str,
        max_age: int | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
    ) -> None:
        """Set value of a signed cookie.

        Arguments:
            cookie_name (string): Name of cookie.
            unsigned_val (mixed): Value of cookie.

        Keyword Arguments:
            max_age (int, optional): Cookie TTL in seconds. Default is no expiration.
            path (string, optional): Limit cookie to a given path. Default is '/'.
                Specify None to use value of app config variable ``SESSION_COOKIE_PATH`` or ``APPLICATION_ROOT``.
            domain (string, optional): Specify if you want to set a cross-domain cookie.
                Default is to use value of app config variable ``SESSION_COOKIE_DOMAIN`` or ``SERVER_NAME``.
            secure (bool, optional): True if the cookie will only be available via HTTPS.
                Default is value of app config variable ``SESSION_COOKIE_SECURE``.
            httponly (bool, optional): True to disallow JavaScript to access the cookie.
                Default is value of app config variable ``SESSION_COOKIE_HTTPONLY``.
        """
        self._get_signed_cookies[cookie_name] = unsigned_val
        self._del_signed_cookies.pop(cookie_name, None)
        self._set_signed_cookies[cookie_name] = {
            "unsigned_val": unsigned_val,
            "max_age": max_age,
            "path": self.get_cookie_path() if path is None else path,
            "domain": self.get_cookie_domain() if domain is None else domain,
            "httponly": self.get_cookie_httponly() if httponly is None else httponly,
            "secure": self.get_cookie_secure() if secure is None else secure,
        }

    def delete_cookie(self, cookie_name: str, path: str = "/", domain: str | None = None) -> None:
        """Delete a signed cookie.

        Arguments:
            cookie_name (string): Name of cookie.

        Keyword Arguments:
            path (string, optional): If the cookie was limited to a path when set, the path has to be defined here.
                Default is '/'. Specify None to use value of app config variable ``SESSION_COOKIE_PATH`` or ``APPLICATION_ROOT``.
            domain (string, optional): If the cookie was limited to a domain when set, that domain has to be defined here.
                Default is to use value of app config variable ``SESSION_COOKIE_DOMAIN`` or ``SERVER_NAME``.
        """
        self._get_signed_cookies[cookie_name] = None
        self._set_signed_cookies.pop(cookie_name, None)
        self._del_signed_cookies[cookie_name] = {
            "path": self.get_cookie_path() if path is None else path,
            "domain": self.get_cookie_domain() if domain is None else domain,
        }

    def get_cookie_path(self) -> str:
        """Return default cookie ``path``.

        Returns:
            str
        """
        return self._session_interface.get_cookie_path(self._app)

    def get_cookie_domain(self) -> str | None:
        """Return default cookie ``domain``.

        Returns:
            str | None
        """
        return self._session_interface.get_cookie_domain(self._app)

    def get_cookie_httponly(self) -> bool:
        """Return default cookie ``httponly`` setting.

        Returns:
            bool
        """
        return self._session_interface.get_cookie_httponly(self._app)

    def get_cookie_secure(self) -> bool:
        """Return default cookie ``secure`` setting.

        Returns:
            bool
        """
        return self._session_interface.get_cookie_secure(self._app)

    def get_signing_serializer(self) -> Serializer:
        """Return default signing serializer.

        Returns:
            Serializer
        """
        return self._session_interface.get_signing_serializer(self._app)

    def hash_name(self, name: str) -> str:
        """Hash cookie name with ``name_hash_method``.

        Args:
            name (str): Name to hash.

        Returns:
            str
        """
        if self.name_hash_method is not None:
            salty_name = (self._session_interface.salt + name).encode()  # bytes
            return self.name_hash_method(salty_name).hexdigest()
        return name
