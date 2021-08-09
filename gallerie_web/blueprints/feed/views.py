from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
from flask_login import login_user, login_required, current_user
from app import app
import datetime
from gallerie_web.util.helpers import upload_file_to_s3, allowed_file
from werkzeug.utils import secure_filename

feed_blueprint = Blueprint('feed', __name__, template_folder='templates')


@feed_blueprint.route('/', methods=["GET"])
def index():
    return redirect(url_for('home'))


# upload image to feed
@feed_blueprint.route('/new', methods=["GET", "POST"])
def new():
    if request.method == "GET":
        return redirect(url_for("home"))

    if request.method == "POST":
        return "Uploading post!"
