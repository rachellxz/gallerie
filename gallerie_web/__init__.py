from app import app
from flask import render_template
from gallerie_web.blueprints.users.views import users_blueprint
from gallerie_web.blueprints.login.views import login_blueprint
from gallerie_web.blueprints.feed.views import feed_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(login_blueprint, url_prefix="/login")
app.register_blueprint(feed_blueprint, url_prefix="/feed")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized_entry(e):
    return render_template('401.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/")
def home():
    return render_template('home.html')
