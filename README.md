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

## Install for development

	git clone https://github.com/lovette/flask_signedcookies.git
	cd flask_signedcookies/
	make virtualenv
	source $HOME/.virtualenvs/flask_signedcookies/bin/activate
	make requirements
	make install-dev
