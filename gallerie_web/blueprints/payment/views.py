from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, current_user, logout_user
from gallerie_web.util.payment import gateway
from models.user import *
from models.feed import *
from models.payment import *
from decimal import Decimal

payment_blueprint = Blueprint("payment", __name__, template_folder="templates")


# process transaction + save payment data to db
@payment_blueprint.route("/create/<username>/<id>", methods=["POST"])
def create(id, username):
    nonce = request.form["nonce"]
    amount = round(Decimal(request.form["amount"]))

    gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })

    new_payment = Payment(amount=amount, img=id, sender=current_user.id)
    if new_payment.save():
        flash("Thank you for supporting our artists!")
        return redirect(url_for("users.view", username=username, id=id))
    else:
        flash("An error occurred.")
        return redirect(url_for("home"))
