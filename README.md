# Flask-SignedCookies

Flask extension that simplifies setting cookies with obscure names and signed values.

Cookie names and values are typically accessible as plain text.
This class manages cookies where the cookie name is set to a salted hash (`md5` by default)
and uses Flask's default session serializer `SecureCookieSessionInterface` to serialize and sign each cookie value.
Cookies will be rejected if their signature is invalid.


## How to use

Create and init a `SignedCookies` instance.

	from flask_signedcookies import SignedCookies

	app = Flask(__name__)

	signedcookies = SignedCookies()
	signedcookies.init_app(app)

Then use these `app` functions to manage signed cookies:

* `get_cookie`
* `set_cookie`
* `delete_cookie`

Use the traditional `response` cookie functions to manage non-signed cookies.


## Install for development

	git clone https://github.com/lovette/flask_signedcookies.git
	cd flask_signedcookies/
	make virtualenv
	source $HOME/.virtualenvs/flask_signedcookies/bin/activate
	make requirements
	make install-dev
