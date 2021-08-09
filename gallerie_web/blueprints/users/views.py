from app import app
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from models.user import User
from models.feed import Feed
from gallerie_web.util.helpers import upload_file_to_s3, allowed_file
from gallerie_web.util.google_oauth import *
from werkzeug.utils import secure_filename
import datetime
import string
import random

users_blueprint = Blueprint('users', __name__, template_folder='templates')

chars = string.ascii_letters + string.punctuation


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


# create new account
@users_blueprint.route('/new', methods=['POST'])
def create():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    retype_password = request.form.get("retype_password")

    ## FORM VALIDATION
    # check if passwords match
    if password != retype_password:
        flash("Passwords do not match.")
        return render_template("users/new.html",
                               first_name=first_name,
                               last_name=last_name,
                               username=username,
                               email=email)

    # if data is valid, save user to database
    new_user = User(first_name=first_name.title(),
                    last_name=last_name.title(),
                    email=email,
                    username=username,
                    password=password)

    if new_user.save():
        valid_user = User.get_or_none(User.username == username)
        remember = True if request.form.get("remember") else False
        login_user(valid_user, remember=remember)
        flash(
            f"Account created successfully. Thanks for signing up, {current_user.first_name}!"
        )
        return redirect(url_for("home"))

    else:
        for errors in new_user.errors:
            flash(errors)
        return render_template("users/new.html",
                               first_name=first_name,
                               last_name=last_name,
                               username=username,
                               email=email,
                               errors=new_user.errors)


# edit user profile
@users_blueprint.route("/<username>/edit", methods=["GET"])
@login_required
def edit(username):
    user = User.get_or_none(User.username == username)

    if current_user == user:
        return render_template("users/edit.html")
    else:
        return redirect(url_for("users.edit", username=current_user.username))


# save changed user details
@users_blueprint.route("/update", methods=["POST"])
@login_required
def update():

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    username = request.form.get("username")
    updated_at = datetime.datetime.now()

    update_query = User.update(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        updated_at=updated_at).where(User.username == current_user.username)

    if update_query.execute():
        flash("User details successfully saved.")
        return redirect(url_for("users.edit", username=current_user.username))
    else:
        # still need to check for errors (validation - e.g., if username or email is not unique)
        flash("Changes could not be saved. Please try again.")
        return render_template("users/edit.html")


# show user profiles by username
@users_blueprint.route("/<username>", methods=["GET"])
def show(username):
    user = User.get_or_none(User.username == username)
    feed = Feed.select(Feed, User).join(User).where(
        User.username == username).order_by(Feed.created_at.desc())

    if user:
        return render_template("users/show.html", user=user, feed=feed)

    else:
        flash("This account doesn't exist.")
        return redirect(url_for("home"))


# search profile by username
@users_blueprint.route("/search", methods=["POST"])
def search():

    username = request.form["username"].lower()

    if username:
        return redirect(url_for('users.show', username=username))
    else:
        flash("Hmm, an error occured. Please try again.")
        return redirect(url_for("home"))


@users_blueprint.route("/", methods=["GET"])
def index():
    return redirect(url_for("home"))


# upload profile pic
@users_blueprint.route("/upload", methods=["POST"])
@login_required
def upload():
    if "user_file" not in request.files:
        flash("No user_file key in request.files")
        return render_template("users/edit.html")

    file = request.files["user_file"]

    if file.filename == "":
        flash("Please select a file.")
        return render_template("users/edit.html")

    if file and allowed_file(file.filename):
        # random_string = ''.join(random.choice(chars) for i in range(15))
        file.filename = secure_filename(file.filename)

        # output is the URL path
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])

        # save the img url path to current user's profile_img_url field in database
        query = User.update(profile_img_url=str(output)).where(
            User.username == current_user.username)

        if query.execute():
            flash("Profile pic updated!")
            return redirect(
                url_for("users.edit", username=current_user.username))
        else:
            flash("Hmm, something went wrong. Please try again!")
            return redirect(
                url_for("users.edit", username=current_user.username))

    else:
        flash("Hmm, an error seems to have occurred. Please try again.")
        return redirect(url_for("users.edit", username=current_user.username))


# delete profile pic
@users_blueprint.route("/delete", methods=["POST"])
@login_required
def delete():
    default_img_path = app.config["DEFAULT_IMG_PATH"]

    query = User.update(profile_img_url=default_img_path).where(
        User.username == current_user.username)
    if query.execute():
        flash("Profile pic removed!")
        return redirect(url_for("users.edit", username=current_user.username))
    else:
        flash("An error seems to have occured. Please try again.")
        return render_template("users/edit.html")


# toggle privacy settings
@users_blueprint.route("/<username>/privacy", methods=["POST"])
@login_required
def toggle(username):
    username = current_user.username
    user = User.get_or_none(User.username == username)

    if user.public_profile == True:
        update_privacy = User.update(public_profile=False).where(
            User.username == username)
    else:
        update_privacy = User.update(public_profile=True).where(
            User.username == username)

    if update_privacy.execute():
        flash("Privacy settings have been updated!")
        return redirect(url_for("users.edit", username=username))
    else:
        flash("Hmm, something went wrong. Please try again!")
        return redirect(url_for("users.edit", username=username))


# sign in with a Google account
@users_blueprint.route("/new/google")
def new_google_account():
    redirect_uri = url_for("users.create_google_account", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@users_blueprint.route("/authorize/google-account")
def create_google_account():
    oauth.google.authorize_access_token()
    google_data = oauth.google.get(
        "htt[s://www.googleapis.com/oauth2/v2/userinfo").json()

    random_string = ''.join(random.choice(chars) for i in range(8))

    username = google_data["given_name"].lower() + random_string
    first_name = ''.join(random.choice(chars) for i in range(5))
    last_name = ''.join(random.choice(chars) for i in range(5))
    email = google_data["email"]
    password = ''.join(random.choice(chars) for i in range(10))

    user = User(username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password)

    if user.save():
        login_user(user)
        flash("Login successful.")
        return redirect(url_for("home"))
    else:
        flash("An error occurred. Please try again!")
        return redirect(url_for("users.new"))


# view user's individual post
@users_blueprint.route("/<username>/<id>", methods=["GET"])
def view(username, id):
    user = User.get_or_none(User.username == username)
    image = Feed.get_or_none(Feed.id == id)

    if image:
        return render_template("users/view.html", user=user, image=image)
    else:
        flash("Hmm, an error occurred. Please try again.")
        return redirect(url_for("home"))