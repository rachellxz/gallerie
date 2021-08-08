from models.base_model import BaseModel
import peewee as pw
from collections import defaultdict
import re
from playhouse.postgres_ext import PostgresqlExtDatabase
from werkzeug.security import generate_password_hash
from flask_login import UserMixin


class User(BaseModel, UserMixin):
    first_name = pw.CharField(null=False)
    last_name = pw.CharField(null=False)
    email = pw.CharField(unique=True, null=False)
    username = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)
    password = None

    profile_img_url = pw.TextField(
        default="http://gram0721.s3.amazonaws.com/default_profile_img.png")

    # public_profile = pw.BooleanField(default=True)

    def validate(self):
        # check if email is unique
        email_existing = User.get_or_none(User.email == self.email)
        if email_existing:
            self.errors.append(
                "This email has been used to create an account before. Please use a different email to sign up."
            )

        # validate email type
        valid_email = re.search(r"[\@ \.]", self.email)
        if not valid_email:
            self.errors.append("This is not a valid email.")

        # check if username is unique
        username_existing = User.get_or_none(User.username == self.username)
        if username_existing:
            self.errors.append(
                "This username is taken. Please try a different username.")

        # check if password meets length requirement
        if len(self.password) <= 8:
            self.errors.append("Passwords should be at least 8 characters.")

        # check if password meets char requirements
        has_lowercase = re.search(r"[a-z]", self.password)
        has_uppercase = re.search(r"[A-Z]", self.password)
        has_special_char = re.search(
            r"[\[ \] \{ \} \# \% \$ \@ \! \^ \& \* \( \) \+ \_ \- \= \~ \_]",
            self.password)

        if has_lowercase and has_uppercase and has_special_char:
            self.password_hash = generate_password_hash(self.password)
        else:
            self.errors.append(
                "Passwords must have a lowercase, uppercase, or a special character."
            )