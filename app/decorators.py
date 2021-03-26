from functools import wraps
from flask import abort, render_template
from flask_login import current_user

from .models import User

def permission_required(role, error_page=None):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not current_user.can(role):
				if error_page is None:
					abort(403)
				else:
					return render_template(error_page)
			return f(*args, **kwargs)
		return decorated_function
	return decorator

# def store_required(f):
# 	return permission_required(User.ORDINARY_USER|User.STORE_OWNER)(f)

# def factory_required(f):
# 	return permission_required(User.ORDINARY_USER|User.FACTORY_OWNER)(f)
