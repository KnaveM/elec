from flask import render_template, session, redirect, url_for, request, flash
from flask_login import current_user, login_required
from . import back
from .forms import *
from ..models import *
from .. import db
@back.before_request
def before_request():
	if current_user.is_authenticated is False: #需要登陆后才能进入后台 统一验证
		flash("请先登陆")
		return redirect(url_for('auth.login'))

@back.route('/')
def index():
	return "back"

@back.route('/store/<int:id>')
def store_backend(id):
	return "success"


@back.route('/factory/<int:id>')
def factory_backend(id):
	return "success"

@back.route('/addproduct', methods=['GET', 'POST'])
def add_product():
	"添加产品"
	form = ProductForm(choices=[(r.factory.id, r.factory.name) for r in current_user.roles if r.factory])
	if form.validate_on_submit():
		f = FactoryInfo.query.filter_by(id=form.factory.data).first()
		p = Product(f)
		p.name = form.name.data
		p.version = form.version.data
		p.description = form.description.data
		p.comment = form.comment.data
		db.session.add(p)
		db.session.commit()
		return redirect(url_for('auth.user', id=current_user.id))
	return render_template("/auth/product.html", form=form)

@back.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
	"修改产品"
	fi = Product.query.filter_by(id=id).first()
	form = ProductForm(choices=[(i.factory.id, i.factory.name) for i in current_user.roles if i.factory], name=fi.name, version=fi.version, description=fi.description, comment=fi.comment, factory=fi.factory.id)
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

@back.route('/deleteproduct/<int:id>')
def delete_product(id):
	p = Product.query.filter_by(id=id).first()
	if p is None:
		flash("无此项产品")
		return redirect(url_for('auth.user', id=current_user.id))
	db.session.delete(p)
	db.session.commit()
	return redirect(url_for('auth.user', id=current_user.id))




# MARK: 订单管理
@back.route('/cart/addproduct')
def cart_add_product():
	"向购物车添加产品"
	pass