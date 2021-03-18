from flask import render_template, session, redirect, url_for, request

from . import back


@back.route('/store/<int:id>')
def store_backend(id):
	return "success"

@back.route('/factory/<int:id>')
def factory_backend(id):
	return "success"

