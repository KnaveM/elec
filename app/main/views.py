from app.models import Product
from flask import render_template, session, redirect, url_for, request, current_app
from flask_login import login_required
from flask_socketio import emit, join_room, leave_room
import json

from . import main
from .. import socketio
from ..models import *

@main.route('/', methods=['GET', 'POST'])
def index():
	"主页 显示不同的厂商" # TODO: main page
	return render_template('index.html')

@main.route('/detail/<int:id>')
def detail(id):
	p = Product.query.filter_by(id=id).first()
	return render_template('detail.html', product=p)


# MARK: 临时 测试用
@main.route('/test')
def test():
	"临时主页"
	return render_template('front_base.html')

@main.route('/testlogin')
def testlogin():
	return render_template('auth/front_login.html')

@main.route('/cart')
@login_required
def cart():
	"TODO: 临时使用的购物车, 用于测试功能"
	return render_template('cart.html')

@main.route('/search')
def search():
	keyword = request.args['text']
	ps = []
	if keyword:
		for k in keyword.split():
			ps.extend(Product.query.filter(Product.name.like("%{}%".format(k))).all())
	return render_template('search.html', search_keyword=keyword, search_results=ps)

@main.route('/product/<int:id>')
def product(id):
	p = Product.query.filter_by(id=id).first()
	return render_template('product.html', product=p)


@main.route('/cartlist')
def cart_list():
	return render_template('cart_list.html')

# MARK: for testing socketio
@socketio.on('connect')
def test_connect():
	current_app.logger.debug('server is connected, this is a debug message')

@socketio.on('message')
def handle_message(data):
	current_app.logger.debug('get message envent')

@socketio.on("cart")
def handle_cart(json_data):
	"向购物车添加产品"
	current_app.logger.debug("get message" + str(json_data))
	# json_data = json.loads(data)
	u = User.query.filter_by(id=json_data['user_id']).first()
	if u is None:
		emit('error', data="TODO:")
	p = Product.query.filter_by(id=json_data['product_id']).first()
	if p is None:
		emit('error', data="TODO:")
	action = json_data['action']
	count = json_data.setdefault('count', 1)
	if action == 1:
		current_app.logger.debug("添加到购物车")
		u.add_to_cart(p, count)
		db.session.commit()
		emit('cart', {"product_id": p.id, "cart_product_count": u.get_cart_product_count(p)})
		
	elif action == 2:
		current_app.logger.debug("从购物车删除")
		u.reduce_from_cart(p, count)
		db.session.commit()
		emit('cart', {"product_id": p.id, "cart_product_count": u.get_cart_product_count(p)})
	else:
		current_app.logger.debug("购物车 错误")
		emit('error', data="TODO:")