from app.main.forms import StoreAddressForm
from app.models import Product
from flask import render_template, session, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
import json

from . import main
from .. import socketio
from ..models import *

@main.route('/', methods=['GET', 'POST'])
def index():
	"主页 显示不同的厂商" # TODO: main page
	new_products = Product.query.limit(4).all()
	hot_products = Product.query.limit(4).all()
	return render_template('index.html', new_products=new_products, hot_products=hot_products)

@main.route('/order/<int:id>')
@login_required
def order(id):
	"买家查看订单的详情"
	o = Order.query.filter_by(id=id).first()
	if o is None:
		abort(404)
	return render_template('order.html', order=o)

@main.route('/error/<int:code>')
def test_error(code):
	return render_template(str(code)+'.html')

@main.route('/search')
def search():
	"搜索页面"
	keyword = request.args['text']
	ps = []
	if keyword:
		for k in keyword.split():
			ps.extend(Product.query.filter(Product.name.like("%{}%".format(k))).all())
	return render_template('search.html', search_keyword=keyword, search_results=ps)

@main.route('/product/<int:id>')
def product(id):
	"查看指定产品的详细信息"
	p = Product.query.filter_by(id=id).first()
	return render_template('product.html', product=p)


@main.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
	"购物车页面, 查看当前购物车详情"
	f = StoreAddressForm(choices=[(store.id, store.name) for store in current_user.stores])
	if f.validate_on_submit():
		s = StoreInfo.query.filter_by(id=f.store.data).first()
		orders = [order[1] for order in current_user.create_orders(s)]
		return render_template('orders.html', orders=orders)
	return render_template('cart.html', form=f)

@main.route('/purchases')
@login_required
def purchases():
	"买家查看全部采购单"
	orders = current_user.purchases
	return render_template('orders.html', orders=orders)


# MARK: for testing socketio
@socketio.on('connect')
def test_connect():
	pass
	# current_app.logger.debug('server is connected, this is a debug message')

@socketio.on('message')
@login_required
def handle_message():
	current_app.logger.debug('get message envent test login required')

@socketio.on("cart")
@login_required
def handle_cart(json_data):
	current_app.logger.debug("客户端的购物车事件")
	current_app.logger.debug("get message" + str(json_data))
	# json_data = json.loads(data)
	u = User.query.filter_by(id=json_data['user_id']).first()
	if u is None:
		emit('error', data="TODO:")
	p = Product.query.filter_by(id=json_data.setdefault('product_id', 0)).first()

	action = json_data['action']
	count = json_data.setdefault('count', 1)

	json_data["cart_count"] = u.cart_products.count()
	if action == 1:
		if p is None:
			emit('error', data="TODO:")
			return
		current_app.logger.debug("添加到购物车")
		u.add_to_cart(p, count)
		db.session.commit()
		json_data["cart_product_count"] = u.get_cart_product_count(p)
		emit('cart', json_data)
		
	elif action == 2:
		if p is None:
			emit('error', data="TODO:")
			return
		current_app.logger.debug("从购物车删除")
		u.reduce_from_cart(p, count)
		db.session.commit()
		json_data["cart_product_count"] = u.get_cart_product_count(p)
		emit('cart', json_data)
	elif action == 3:
		current_app.logger.debug("查询购物车产品数量")
		json_data["cart_count"] = u.cart_products.count()
		emit("cart", {"cart_count": u.cart_products.count()})
	else:
		current_app.logger.debug("购物车 错误")
		emit('error', data="TODO:")