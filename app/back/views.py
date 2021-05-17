from flask import render_template, session, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required
import json

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

@back.route('/addstore', methods=['GET', 'POST'])
def add_store():
	form = StoreInfoForm()
	if form.validate_on_submit():
		si = StoreInfo(current_user, name=form.name.data, address=form.address.data, contact=form.contact.data, phone=form.phone.data)
		db.session.commit()
		return redirect(url_for('back.stores'))
	return render_template("/auth/store_info.html", form=form, isNew=True)

@back.route('/editstore/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_store(id):
	si = StoreInfo.query.filter_by(id=id).first()
	form = StoreInfoForm(address_readonly=True, name=si.name, address=si.address, contact=si.contact, phone=si.phone)
	if form.validate_on_submit():
		si.name=form.name.data
		si.address=form.address.data
		si.contact=form.contact.data
		si.phone=form.phone.data
		db.session.add(si)
		db.session.commit()
		return redirect(url_for('back.stores'))
	return render_template("/auth/store_info.html", form=form)

@back.route('/viewstore/<int:id>')
@login_required
def view_store(id):
	"卖家查看店铺信息=查看快递信息"
	si = StoreInfo.query.filter_by(id=id).first()
	form = StoreInfoForm(address_readonly=True, view_only=True, name=si.name, address=si.address, contact=si.contact, phone=si.phone)
	return render_template("/back/view_store_info.html", form=form)


@back.route('/purchases')
def purchases():
	return render_template('back/purchases.html')

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




# MARK: 产品管理
@back.route('/addproduct', methods=['GET', 'POST'])
def add_product():
	"添加产品"
	import os
	images_base_path = os.path.join(os.getcwd(), "app/static/assets/db/images")
	# current_app.logger.debug(images_base_path)
	# form = ProductForm(choices=[(r.factory.id, r.factory.name) for r in current_user.roles if r.factory])  # 多工厂版本
	form = ProductForm()
	if form.validate_on_submit():
		f = current_user.factory # FactoryInfo.query.filter_by(id=form.factory.data).first()
		p = Product(f)
		current_app.logger.debug("productid"+str(p.id))
		p.name = form.name.data
		p.subtitle = form.subtitle.data
		# p.version = form.version.data
		# p.description = form.description.data
		p.price = form.price.data
		p.specification = form.specification.data
		# p.comment = form.comment.data
		db.session.add(p)
		db.session.commit()
		form.img1.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_1"))
		form.img2.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_2"))
		form.img3.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_3"))
		form.img4.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_4"))
		form.img5.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_5"))
		return redirect(url_for('back.products'))
	return render_template("/back/product.html", form=form, isNew=True)

@back.route('/editproduct/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
	"修改产品"
	p = Product.query.filter_by(id=id).first()
	if p is None:
		abort(404)
	form = ProductForm(p, name=p.name, subtitle=p.subtitle, price=p.price, specification=str(p.specification_json).replace("'", '"'))
	if form.validate_on_submit():
		import os
		images_base_path = os.path.join(os.getcwd(), "app/static/assets/db/images")
		current_app.logger.debug("###修改产品")
		current_app.logger.debug(p.name)
		current_app.logger.debug(form.name.data)
		p.name = form.name.data
		
		p.subtitle = form.subtitle.data
		p.price = form.price.data
		p.specification = form.specification.data
		db.session.add(p)
		db.session.commit()
		if form.img1.data.filename != "":
			form.img1.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_1"))
		if form.img2.data.filename != "":
			form.img2.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_2"))
		if form.img3.data.filename != "":
			form.img3.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_3"))
		if form.img4.data.filename != "":
			form.img4.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_4"))
		if form.img5.data.filename != "":
			form.img5.data.save(os.path.join(images_base_path, "p"+str(p.id)+"_5"))
		flash("保存成功")
	return render_template("/back/product.html", form=form, isNew=False)
	

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


# setting
@back.route('/updateUserInfo', methods=['GET', 'POST'])
def update_user_info():
	current_app.logger.debug(request.data)
	return "success"