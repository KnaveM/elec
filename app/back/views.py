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

# MARK: 侧边栏链接 START
@back.route('/')
def index():
	return render_template("back/index.html")

@back.route('/purchase')
def purchase():
	return render_template('back/purchase.html')

@back.route('/orders')
def orders():
	return render_template('back/orders.html')

@back.route('/stores')
def stores():
	return render_template('back/stores.html')

@back.route('/products')
def products():
	return render_template('back/products.html')

@back.route('/analysis')
def analysis():
	return render_template('back/analysis.html')

@back.route('/help')
def help_page():
	return render_template('back/help.html')

@back.route('/setting')
def setting():
	return render_template('back/setting.html')

@back.route('/subordinates')
def subordinates():
	return render_template('back/subordinates.html')

# MARK: 侧边栏链接 END

@back.route('/store/<int:id>')
def store_backend(id):
	return "success"


@back.route('/factory/<int:id>')
def factory_backend(id):
	return "success"

@back.route('/addproduct', methods=['GET', 'POST'])
def add_product():
	"添加产品"
	import os
	images_base_path = os.path.join(os.getcwd(), "app/static/assets/db/images")
	current_app.logger.debug(images_base_path)
	form = ProductForm(choices=[(r.factory.id, r.factory.name) for r in current_user.roles if r.factory])
	if form.validate_on_submit():
		f = FactoryInfo.query.filter_by(id=form.factory.data).first()
		p = Product(f)
		current_app.logger.debug("productid"+str(p.id))
		p.name = form.name.data
		# p.version = form.version.data
		p.description = form.description.data
		p.comment = form.comment.data
		db.session.add(p)
		db.session.commit()
		form.img1.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_1"))
		form.img2.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_2"))
		form.img3.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_3"))
		form.img4.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_4"))
		form.img5.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_5"))
		return redirect(url_for('auth.user', id=current_user.id))
	return render_template("/auth/product.html", form=form)

@back.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
	"修改产品"
	fi = Product.query.filter_by(id=id).first()
	form = ProductForm(choices=[(i.factory.id, i.factory.name) for i in current_user.roles if i.factory], name=fi.name, description=fi.description, comment=fi.comment, factory=fi.factory.id)
	if form.validate_on_submit():
		p = fi
		p.name = form.name.data
		# p.version = form.version.data
		p.description = form.description.data
		p.comment = form.comment.data
		p.factory_id = form.factory.data
		db.session.add(fi)
		db.session.commit()
		flash("修改产品信息成功")
	return render_template("/auth/factory_info.html", form=form)

@back.route('/deleteproduct/<int:id>')
def delete_product(id):
	p = Product.query.filter_by(id=id).first()
	if p is None:
		flash("无此项产品")
		return redirect(url_for('auth.user', id=current_user.id))
	p.delete()
	# db.session.delete(p)
	db.session.commit()
	flash('删除产品成功')
	return redirect(url_for('auth.user', id=current_user.id))




# MARK: 订单管理 DROPPED
@back.route('/cart/addproduct/<int:id>')
def cart_add_product(id):
	"向购物车添加产品"
	p = Product.query.filter_by(id=id).first()
	if p is None:
		flash("无法添加到购物车, 无此产品")
		return redirect(url_for('auth.user', id=current_user.id))
	current_user.add_to_cart(p)
	db.session.commit()
	return redirect(url_for('auth.user', id=current_user.id))