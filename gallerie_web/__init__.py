from app import app
from flask import render_template, redirect, url_for, flash
from gallerie_web.blueprints.users.views import users_blueprint
from gallerie_web.blueprints.login.views import login_blueprint
from gallerie_web.blueprints.feed.views import feed_blueprint
from gallerie_web.blueprints.payment.views import payment_blueprint
from gallerie_web.blueprints.followers.views import followers_blueprint
from models.user import *
from models.follow import *
from models.feed import *
from peewee import prefetch
from flask_login import current_user, login_required
from flask_assets import Environment, Bundle
from .util.assets import bundles

assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/")
app.register_blueprint(login_blueprint, url_prefix="/login")
app.register_blueprint(feed_blueprint, url_prefix="/feed")
app.register_blueprint(payment_blueprint, url_prefix="/give")
app.register_blueprint(followers_blueprint, url_prefix="/followers")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized_entry(e):
    return render_template('401.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


# homepage: view posts from followed users
@app.route("/home")
def home():
    if current_user.is_authenticated:

        user = User.get_or_none(User.id == current_user.id)
        users = User.select()
        feed = Feed.select().join(User, on=User.id == Feed.user_id).join(
            Follow, on=Follow.artist_id == Feed.user_id).where(
                (Follow.follower == user)
                & (Follow.approved == True)).order_by(
                    Feed.created_at.desc()).prefetch(users)

        return render_template("home.html", feed=feed)

    else:
        return redirect(url_for("login.new"))


# explore page: view posts from public profiles
@app.route("/explore")
def explore():
    users = User.select().where(User.public_profile == True)
    feed = Feed.select().join(User, on=User.id == Feed.user_id).where(
        User.public_profile == True).order_by(
            Feed.created_at.desc()).prefetch(users)

    return render_template("explore.html", feed=feed)


@app.route("/")
def index():
    return redirect(url_for("home"))