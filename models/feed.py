import peewee as pw
from models.base_model import BaseModel
from models.user import *
from flask_login import UserMixin


class Feed(BaseModel, UserMixin):
    user = pw.ForeignKeyField(User, backref="feed")
    image_url = pw.CharField(null=True)
    img_description = pw.TextField(null=True)