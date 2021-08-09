import peewee as pw
from models.base_model import BaseModel
from models.user import User
from flask_login import UserMixin


class Follow(BaseModel, UserMixin):
    artist = pw.ForeignKeyField(User)
    follower = pw.ForeignKeyField(User)
    approved = pw.BooleanField(default=False)
