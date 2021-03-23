from flask import render_template, session, redirect, url_for, request, flash, abort
from flask_login import login_required, login_user, logout_user, current_user

from . import auth 
from .forms import *
from ..decorators import store_required, factory_required
from ..models import FactoryInfo, Product, User, UserInfo, StoreInfo
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

@auth.route('/editinfo', methods=['GET', 'POST'])
@login_required
def edit_user_info():
	form = EditUserInfoForm(email=current_user.user_info.email, name=current_user.user_info.name, address=current_user.user_info.address, phone=current_user.user_info.phone)
	if form.validate_on_submit():
		ui = current_user.user_info
		ui.email = form.email.data
		ui.name = form.name.data
		ui.address = form.address.data
		ui.phone = form.phone.data
		db.session.add(ui)
		db.session.commit()
		return redirect(url_for('auth.user', username=current_user.username))
	return render_template('/auth/edit_user_info.html', form=form)

@auth.route('/addstore', methods=['GET', 'POST'])
@login_required
def addstore():
	form = StoreInfoForm()
	if form.validate_on_submit():
		si = StoreInfo(user_id=current_user.id)
		si.name=form.name.data
		si.address=form.address.data
		si.contact=form.contact.data
		si.phone=form.phone.data
		db.session.add(si)
		db.session.commit()
		return redirect(url_for('auth.user', username=current_user.username))
	return render_template("/auth/store_info.html", form=form)

@auth.route('/editstore/<int:id>', methods=['GET', 'POST'])
@login_required
def editstore(id):
	si = StoreInfo.query.filter_by(id=id).first()
	form = StoreInfoForm(name=si.name, address=si.address, contact=si.contact, phone=si.phone)
	if form.validate_on_submit():
		si.name=form.name.data
		si.address=form.address.data
		si.contact=form.contact.data
		si.phone=form.phone.data
		db.session.add(si)
		db.session.commit()
	return render_template("/auth/store_info.html", form=form)

@auth.route('/addfactory', methods=['GET', 'POST'])
@login_required
def addfactory():
	form = FactoryInfoForm()
	if form.validate_on_submit():
		fi = FactoryInfo(user_id=current_user.id)
		fi.name=form.name.data
		fi.address=form.address.data
		fi.contact=form.contact.data
		fi.phone=form.phone.data
		fi.complaint_department = form.complaint_department.data
		fi.complaint_method = form.complaint_method.data
		db.session.add(fi)
		db.session.commit()
		return redirect(url_for('auth.user', username=current_user.username))
	return render_template("/auth/factory_info.html", form=form)

@auth.route('/editfactory/<int:id>', methods=['GET', 'POST'])
@login_required
def editfactory(id):
	fi = FactoryInfo.query.filter_by(id=id).first()
	form = FactoryInfoForm(name=fi.name, address=fi.address, contact=fi.contact, phone=fi.phone, complaint_department=fi.complaint_department, complaint_method=fi.complaint_method)
	if form.validate_on_submit():
		fi.name=form.name.data
		fi.address=form.address.data
		fi.contact=form.contact.data
		fi.phone=form.phone.data
		fi.complaint_department = form.complaint_department.data
		fi.complaint_method = form.complaint_method.data
		db.session.add(fi)
		db.session.commit()
	return render_template("/auth/factory_info.html", form=form)

@auth.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
	form = ProductForm(choices=[(i.id, i.name) for i in current_user.factorys])
	if form.validate_on_submit():
		p = Product()
		p.name = form.name.data
		p.version = form.version.data
		p.description = form.description.data
		p.comment = form.comment.data
		p.factory_id = form.factory.data
		print(form.factory.data, type(form.factory.data))
		db.session.add(p)
		db.session.commit()
		return redirect(url_for('auth.user', username=current_user.username))
	return render_template("/auth/product.html", form=form)

@auth.route('/editproduct/<int:id>', methods=['GET', 'POST'])
@login_required
def editproduct(id):
	fi = Product.query.filter_by(id=id).first()
	form = ProductForm(choices=[(i.id, i.name) for i in current_user.factorys], name=fi.name, version=fi.version, description=fi.description, comment=fi.comment, factory=fi.factory.id)
	if form.validate_on_submit():
		p = fi
		p.name = form.name.data
		p.version = form.version.data
		p.description = form.description.data
		p.comment = form.comment.data
		p.factory_id = form.factory.data
		db.session.add(fi)
		db.session.commit()
	return render_template("/auth/factory_info.html", form=form)


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
