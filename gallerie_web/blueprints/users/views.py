from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from flask_login import login_user, login_required, current_user
from app import app
import datetime

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
        return redirect(url_for('users.edit'))
    else:
        # still need to check for errors (validation - e.g., if username or email is not unique)
        flash("Changes could not be saved. Please try again.")
        return render_template("users/edit.html")


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"
