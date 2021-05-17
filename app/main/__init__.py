from app.models import OrderStatus, Permission, Product, Order
from flask import Blueprint
from wtforms import StringField, SubmitField, PasswordField, SubmitField, BooleanField, SelectField, FileField

main = Blueprint('main', __name__)

from . import views, errors

@main.app_context_processor
def add_jinja2_context():
    return dict(Permission=Permission, list=list, Product=Product, Order=Order, OrderStatus=OrderStatus, str=str, range=range, StringField=StringField, FileField=FileField)


