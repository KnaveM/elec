from flask import render_template, session, redirect, url_for, request, flash, abort
from flask_login import login_required, login_user, logout_user, current_user

from . import auth 
from .forms import LoginForm, RegistrationForm
from ..decorators import store_required, factory_required
from ..models import User, UserInfo
from ..import db

@auth.before_app_request
def before_app_request():
	"拦截未确认信息的用户"
	pass
	#return render_template('base.html')

@auth.route('/user/<username>')
def user(username):
	"TODO: 每个用户单独的用户介绍界面"
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)  # TODO: 未找到该用户
	return render_template('/auth/user.html', user=user)

@auth.route('/login', methods=['GET', "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for('main.index'))
		flash('用户名或密码错误，请重新输入')
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return render_template('index.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, password=form.password.data)
		db.session.add(user)
		db.session.commit() # commit 获取user.id
		
		userinfo = UserInfo(email=form.email.data, name=form.name.data, address=form.address.data, phone=form.phone.data, user_id=user.id)
		db.session.add(userinfo)
		db.session.commit()

		flash("您已成功注册，请登录")
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)
