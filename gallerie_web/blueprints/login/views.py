from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from models.user import *

login_blueprint = Blueprint('login', __name__, template_folder='templates')


# login form
@login_blueprint.route("/", methods=["GET"])
def new():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return render_template("login/new.html")


# create session after successful login
# using Flask-login
@login_blueprint.route("/", methods=["POST"])
def create():
    username_to_check = request.form.get("username")
    password_to_check = request.form.get("password")

    # validate if username exists
    valid_user = User.get_or_none(User.username == username_to_check)

    # if username is valid
    if valid_user:
        # validate password
        password_hash = valid_user.password_hash
        result = check_password_hash(password_hash, password_to_check)
        # if password entered correctly
        if result:
            remember = True if request.form.get("remember") else False
            login_user(valid_user, remember=remember)
            flash(
                f"Login successful. Welcome back, {current_user.first_name}!")
            return redirect(url_for("home"))
        else:
            flash("The password you entered is incorrect. Please try again.")
            return render_template("login/new.html",
                                   username=username_to_check)
    else:
        flash("Hmm, we can't seem to find an account with that username.")
        return render_template("login/new.html")


# @login_blueprint.route("/home")
# @login_required
# def home():
#     return render_template("login/home.html",
#                            first_name=current_user.first_name)


#log out / destroy session
@login_blueprint.route("/end", methods=["POST"])
@login_required
def destroy():
    user = User.get_or_none(User.username == current_user.username)

    if user:
        logout_user()
        flash("Logout successful. See you again soon!")
        return redirect(url_for('login.new'))
    else:
        flash("Hmm, an error occured. Please try again.")
        return redirect(url_for('home'))


# create/start session after successful login using manual SESSIONS
# @login_blueprint.route("/", methods=["POST"])
# def create():

#     # check if username and password entered correctly
#     username_to_check = request.form.get("username")
#     password_to_check = request.form.get("password")

#     # validate if username exists
#     valid_user = User.get_or_none(User.username == username_to_check)

#     # if username is valid
#     if valid_user:
#         # validate password
#         password_hash = valid_user.password_hash
#         result = check_password_hash(
#             password_hash, password_to_check
#         )  # this returns a boolean value indicating if there is a match

#         # if password entered correctly

#         if result:
#             print("Logged in successfully!")
#             # add user to session
#             session['username'] = valid_user.username
#             return render_template("login/success.html")

#         else:
#             flash("The password you entered is not correct. Please try again.")
#             return render_template("login/new.html",
#                                    username=username_to_check)

#     # if no username found:
#     else:
#         flash("The username does not exist.")
#         return render_template("login/new.html")

# edit user profile
