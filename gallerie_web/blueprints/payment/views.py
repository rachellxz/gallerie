from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, current_user, logout_user
from gallerie_web.util.payment import gateway
from models.user import *
from models.feed import *

payment_blueprint = Blueprint("payment", __name__, template_folder="templates")



@payment_blueprint.route("/create", methods=["POST"])
@login_required
def create():
    return "payments page"