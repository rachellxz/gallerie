from flask import Flask, render_template
import braintree
from app import app

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=app.config["MERCHANT_ID"],
        private_key=app.config["PRIVATE_KEY"],
        public_key=app.config["PUBLIC_KEY"],
    ))
