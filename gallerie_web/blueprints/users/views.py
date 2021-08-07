from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User

users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    retype_password = request.form.get("retype_password")

    ## FORM VALIDATION
    # check if all fields are filled
    if not first_name or not last_name or not email or not password or not retype_password or not username:
        flash("Please ensure all fields are filled.")
        return redirect(url_for("users.new"))

    # check if passwords match
    if password != retype_password:
        flash("Passwords do not match.")
        return redirect(url_for("users.new"))

    new_user = User(first_name=first_name.title(),
                    last_name=last_name.title(),
                    email=email,
                    username=username,
                    password=password)

    if new_user.save():
        flash("Your gallerie account has been created! Thanks for signing up!")
        return redirect(url_for("users.new"))
    else:
        for errors in new_user.errors:
            flash(errors)
        return redirect(url_for("users.new"))


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
