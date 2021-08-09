from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from models.feed import Feed
from flask_login import login_user, login_required, current_user
from app import app
from gallerie_web.util.helpers import upload_file_to_s3, allowed_file
from gallerie_web.util.payment import *
from werkzeug.utils import secure_filename

feed_blueprint = Blueprint('feed', __name__, template_folder='templates')


@feed_blueprint.route('/', methods=["GET"])
@login_required
def index():
    return redirect(url_for('home'))


@feed_blueprint.route("/new", methods=["GET"])
@login_required
def new():
    return redirect(url_for("home"))


# upload image to feed
@feed_blueprint.route("/<username>/create", methods=["POST"])
@login_required
def create(username):

    username = current_user.username

    if "user_file" not in request.files:
        flash("No file selected!")
        return redirect(url_for('users.show', username=username))

    file = request.files["user_file"]
    img_description = request.form["img_description"]

    if file.filename == "":
        flash("Please select an image with valid filename to upload.")
        return redirect(url_for('users.show', username=username))

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        #output is the URL path
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])

        # save the img URL path to new_user_feed in the Feed table, current_user.id as the user_id
        new_user_feed = Feed(user=current_user.id,
                             image_url=str(output),
                             img_description=img_description)

        if new_user_feed.save():
            flash("Your post has been successfully uploaded!")
            return redirect(url_for('users.show', username=username))


# delete image from feed
@feed_blueprint.route("/delete/<id>", methods=["POST"])
@login_required
def delete(id):
    username = current_user.username

    img_to_delete = Feed.get_or_none(Feed.id == id)

    if img_to_delete.delete_instance():
        flash("Image deleted from your feed!")
        return redirect(url_for('users.show', username=username))
    else:
        flash("Something went wrong.")
        return redirect(url_for('users.show', username=username))
