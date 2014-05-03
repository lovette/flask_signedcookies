# Flask-SignedCookies

Flask extension that provides easy access to signed cookies.

	from flask_signedcookies import SignedCookies

	app = Flask(__name__)

	signedcookies = SignedCookies()
	signedcookies.init_app(app)

Functions added to ``app``:

* get_cookie
* set_cookie
* delete_cookie
