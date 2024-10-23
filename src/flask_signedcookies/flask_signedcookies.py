"""Flask extension that provides easy access to signed cookies.

This module provides:
- SignedCookies
"""

import datetime
import hashlib

from flask.sessions import SessionInterface, total_seconds
from itsdangerous import BadSignature


class SignedCookies:
    """Flask extension to provide easy access to signed cookies."""

    name_hash_method = staticmethod(hashlib.md5)
    """Hash method to encode cookie names. Default is md5. Set to None to disable."""

    def __init__(self):
        """Constructor.
        """
        super().__init__()

        self._app = None
        self._session_interface = None
        self._get_signed_cookies = {}
        self._set_signed_cookies = {}
        self._del_signed_cookies = {}

    def init_app(self, app, session_interface=None, register_funcs=True):
        """Initialize extension and application instance.

        Arguments:
            app (Flask): Flask application instance.

        Keyword Arguments:
            session_interface (SessionInterface, optional): Session interface instance.
                Any interface derived from ``flask.sessions.SessionInterface`` that provides a
                function named ``get_signing_serializer`` can be used (which the standard
                ``SecureCookieSessionInterface`` does). Default is to use ``app.session_interface``.
            register_funcs (bool, optional): Register cookie functions for ``app``. Default is True.
        """
        self._app = app
        self._session_interface = session_interface or app.session_interface

        assert isinstance(self._session_interface, SessionInterface)
        assert hasattr(self._session_interface, 'get_signing_serializer')

        # Hook into request startup and teardown
        app.before_request(self.reset_cookies)
        app.after_request(self.save_cookies)

        # Add functions to application instance
        if register_funcs is True:
            app.get_cookie = self.get_cookie
            app.set_cookie = self.set_cookie
            app.delete_cookie = self.delete_cookie

    def reset_cookies(self):
        """Reset signed cookies.

        This occurs by default during request initialization.
        """
        self._get_signed_cookies = {}
        self._set_signed_cookies = {}
        self._del_signed_cookies = {}

    def save_cookies(self, response):
        """Add set-cookie headers for signed cookies.

        This occurs by default after the request is complete.

        Arguments:
            response (flask.Response): Response instance
        """
        # Set signed cookies
        for cookie_name, cookie in self._set_signed_cookies.iteritems():
            signed_val = self.get_signing_serializer().dumps(cookie['unsigned_val'])
            response.set_cookie(self._hash_name(cookie_name), signed_val,
                                max_age=cookie['max_age'],
                                path=cookie['path'],
                                domain=cookie['domain'],
                                httponly=cookie['httponly'],
                                secure=cookie['secure'])

        # Delete signed cookies
        for cookie_name, cookie in self._del_signed_cookies.iteritems():
            response.delete_cookie(self._hash_name(cookie_name),
                                   path=cookie['path'],
                                   domain=cookie['domain'])

        # Make safe to call save_cookies again, just in case
        self.reset_cookies()

        return response

    def get_cookie(self, request, cookie_name, max_age=None):
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

            signed_val = request.cookies.get(self._hash_name(cookie_name))
            if signed_val is not None:
                try:
                    if isinstance(max_age, datetime.timedelta):
                        max_age = total_seconds(max_age)
                    unsigned_val = self.get_signing_serializer().loads(signed_val, max_age=max_age)
                except BadSignature:
                    pass

            self._get_signed_cookies[cookie_name] = unsigned_val

        return self._get_signed_cookies[cookie_name]

    def set_cookie(self, cookie_name, unsigned_val, max_age=None, path='/', domain=None, secure=None, httponly=None):
        """Set value of a signed cookie.

        Arguments:
            cookie_name (string): Name of cookie.
            unsigned_val (mixed): Value of cookie.

        Keyword Arguments:
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
            'unsigned_val': unsigned_val,
            'max_age': max_age,
            'path': self.get_cookie_path() if path is None else path,
            'domain': self.get_cookie_domain() if domain is None else domain,
            'httponly': self.get_cookie_httponly() if httponly is None else httponly,
            'secure': self.get_cookie_secure() if secure is None else secure,
            }

    def delete_cookie(self, cookie_name, path='/', domain=None):
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
            'path': self.get_cookie_path() if path is None else path,
            'domain': self.get_cookie_domain() if domain is None else domain,
            }

    def get_cookie_path(self):
        """Return default cookie ``path``.
        """
        return self._session_interface.get_cookie_path(self._app)

    def get_cookie_domain(self):
        """Return default cookie ``domain``.
        """
        return self._session_interface.get_cookie_domain(self._app)

    def get_cookie_httponly(self):
        """Return default cookie ``httponly`` setting.
        """
        return self._session_interface.get_cookie_httponly(self._app)

    def get_cookie_secure(self):
        """Return default cookie ``secure`` setting.
        """
        return self._session_interface.get_cookie_secure(self._app)

    def get_signing_serializer(self):
        """Return default signing serializer.
        """
        return self._session_interface.get_signing_serializer(self._app)

    def _hash_name(self, name):
        """Hash cookie name with ``name_hash_method``.
        """
        if self.name_hash_method is not None:
            return self.name_hash_method(self._session_interface.salt + name).hexdigest()
        return name
