from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors

@main.app_context_processor
def add_jinja2_context():
    from ..models import Permission
    return dict(Permission=Permission, list=list)