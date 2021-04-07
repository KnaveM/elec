from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError

from ..models import User

class StoreAddressForm(FlaskForm):
    store = SelectField("配送地址:")

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store.choices = choices