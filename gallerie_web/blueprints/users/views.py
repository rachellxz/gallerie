from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from flask_login import login_user, login_required, current_user
from app import app
import datetime
from gallerie_web.util.helpers import upload_file_to_s3, allowed_file
from werkzeug.utils import secure_filename

users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


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


@users_blueprint.route("/edit")
@login_required
def edit():
    user = User.get_or_none(User.username == current_user.username)
    if current_user == user:
        return render_template("users/edit.html")
    else:
        flash("Hmm, something went wrong. Please try again")
        return redirect(url_for("users.edit"))


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
        return redirect(url_for("users.edit"))
    else:
        # still need to check for errors (validation - e.g., if username or email is not unique)
        flash("Changes could not be saved. Please try again.")
        return render_template("users/edit.html")


# show user profiles by username
@users_blueprint.route("/<username>", methods=["GET"])
def show(username):
    user = User.get_or_none(User.username == username)
    if user:
        return render_template("users/show.html", user=user)
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
    return "USERS"


# upload profile pic
@users_blueprint.route("/upload", methods=["POST"])
def upload():
    user = User.get_or_none(User.username == current_user.username)
    img_path = user.profile_img_url

    if "user_file" not in request.files:
        flash("No user_file key in request.files")
        return render_template("users/edit.html")

    file = request.files["user_file"]

    if file.filename == "":
        flash("Please select a file.")
        return render_template("users/edit.html")

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        # output is the URL path
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])

        # save the img url path to current user's profile_img_url field in database
        query = User.update(profile_img_url=str(output)).where(
            User.username == current_user.username)

        if query.execute():
            print("Profile Pic Saved!")
            flash("Profile pic updated!")
            return redirect(
                url_for("users.show", username=current_user.username))
        else:
            flash("Hmm, something went wrong. Please try again!")
            return redirect(url_for("users.edit"))

    else:
        flash("Hmm, an error seems to have occurred. Please try again.")
        return redirect(url_for("users.edit"))


# delete profile pic
