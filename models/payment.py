from models.base_model import BaseModel
from models.feed import Feed
from models.user import User
import peewee as pw


class Payment(BaseModel):
    amount = pw.DecimalField(null=False)
    img = pw.ForeignKeyField(Feed, backref="payments")
    sender = pw.ForeignKeyField(User, backref="payments")