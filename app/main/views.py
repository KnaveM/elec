from app.main.forms import StoreAddressForm
from app.models import Product
from flask import render_template, session, redirect, url_for, request, current_app, abort, flash
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
# from datetime import datetime, timedelta
import datetime
import json

from . import main
from .. import socketio
from ..models import *

# 全局错误处理
@main.app_errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 主页路由
@main.route('/')
def index():
	"主页 显示不同的厂商" # TODO: main page
	new_products = Product.query.order_by(Product.id.desc()).limit(8).all()
	hot_products = Product.query.filter(Product.id.in_(OrderProduct.query.with_entities(OrderProduct.product_id),)).order_by(Product.price.desc()).limit(8).all()
	if len(hot_products) < 8:
		hot_products.extend(Product.query.limit(8-len(hot_products)).all())
	return render_template('index.html', new_products=new_products, hot_products=hot_products)

@main.route('/factory/<int:id>')
def factory(id):
	f = FactoryInfo.query.filter_by(id=id).first()
	if f is None:
		abort(404)
	return render_template("factory.html", factory=f)

# MARK: 卖家订单事件
@main.route('/order/<int:id>')
@login_required
def order(id):
	"卖家查看订单的详情"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.factory.owner.id:
		abort(403)
	return render_template('order.html', order=o)

@main.route('/comfirmOrder/<int:id>')
@login_required
def comfirm_order(id):
	"卖家 确认订单"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.factory.owner.id:
		abort(403)
	if current_user.comfirm_order(o):
		return redirect(url_for('main.order', id=id))
	else:
		abort(403)
# MARK: 卖家订单事件 END


# MARK: 买家采购单事件
@main.route('/purchase/<int:id>')
@login_required
def purchase(id):
	"买家查看订单的详情"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.store.owner.id:
		abort(403)
	return render_template('order.html', order=o)

@main.route('/payPurchase/<int:id>')
@login_required
def pay_purchase(id):
	"买家 支付订单"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.store.owner.id:
		abort(403)
	# 支付系统
	current_user.pay_order(o)
	return redirect(url_for('main.purchase', id=id))

@main.route('/finishPurchase/<int:id>')
@login_required
def finish_purchase(id):
	"买家 确认收货"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.store.owner.id:
		abort(403)
	current_user.finish_order(o)
	return redirect(url_for('main.purchase', id=id))

@main.route('/commentPurchase/<int:id>')
@login_required
def comment_purchase(id):
	"买家 评价订单"
	o = Order.query.filter_by(id=id).first()
	if o is None or current_user.id is not o.store.owner.id:
		abort(403)
	# current_user.finish_order(o)
	return redirect(url_for('main.purchase', id=id))

# MARK: 买家采购单事件 END

@main.route('/error/<int:code>')
def test_error(code):
	return render_template(str(code)+'.html')

@main.route('/search')
def search():
	"搜索页面"
	keyword = request.args['text']
	highPriceFirst = int(request.args.get('highPriceFirst', True)) # 从大到小
	page = int(request.args.get('page', 1)) # 第几页
	isBlock = int(request.args.get('isBlock', 0))
	ps = []
	if keyword:
		for k in keyword.split():
			ps.extend(Product.query.filter(Product.name.like("%{}%".format(k))).all())
	ps.sort(key=lambda p: p.price, reverse=highPriceFirst)
	item_limit = 16
	max_page = len(ps) // item_limit + bool(len(ps) % item_limit)  # 最多页数
	ps = ps[item_limit*(page-1):item_limit*page]
	return render_template('search.html', search_keyword=keyword, search_results=ps, max_page=max_page, current_page=page, highPriceFirst=highPriceFirst, isBlock=isBlock)

@main.route('/product/<int:id>')
def product(id):
	"查看指定产品的详细信息"
	p = Product.query.filter_by(id=id).first()
	if not p:
		abort(404)
	return render_template('product.html', product=p)


@main.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
	"购物车页面, 查看当前购物车详情"
	f = StoreAddressForm(choices=[(store.id, store.name) for store in current_user.stores])
	if f.validate_on_submit():  # 验证form是否正确填写
		s = StoreInfo.query.filter_by(id=f.store.data).first()
		orders = [order[1] for order in current_user.create_orders(s)]
		# for order in orders:
		# 	current_user.comfirm_order(order)
		return redirect(url_for('back.purchases'))
	elif f.is_submitted():
		flash("请先添加门店")
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
	# pass
	current_app.logger.debug('server is connected, this is a debug message')

@socketio.on('message')
@login_required
def handle_message():
	current_app.logger.debug('get message envent test login required')

def get_cart_product_json_list(u):
	li = []
	for cp in u.cart_products.all():
		p = {}
		p['id'] = cp.product.id
		p['img_url'] = cp.product.image_url()
		p['name'] = cp.product.name
		p['url'] = url_for('main.product', id=cp.product.id)
		p['price'] = cp.product.price
		p['count'] = cp.count
		li.append(p)
	return li


@socketio.on("cart")
@login_required
def handle_cart(json_data):
	current_app.logger.debug("客户端的购物车事件")
	current_app.logger.debug(json_data)
	# action 1 添加产品到购物车
	# action 2 从购物车删除产品
	# action 3 查询购物车产品数量
	u = User.query.filter_by(id=json_data['user_id']).first()
	if u is None:
		current_app.logger.debug('错误, 无用户id')
		emit('error', data="user not found TODO:")
		return
	p = Product.query.filter_by(id=json_data.setdefault('product_id', 0)).first()

	action = json_data['action']
	count = json_data.setdefault('count', 1)

	json_data["cart_icon_count"] = u.cart_products.count() # 购物车产品数量
	json_data['cart_total_price'] = u.cart_total_price() # 购物车总价
	if action == 1:
		if p is None:
			current_app.logger.debug('错误, 无此产品')
			emit('error', data="TODO:")
			return
		current_app.logger.debug("添加到购物车")
		if u.add_to_cart(p, count) == 1:  # 添加第一个的情况
			json_data['products'] = get_cart_product_json_list(u)
			json_data['action'] = 4
			json_data["cart_icon_count"] = u.cart_products.count() # 购物车产品数量
			json_data['cart_total_price'] = u.cart_total_price() # 购物车总价
			emit('cart', json_data)
		else:
			json_data["cart_product_count"] = u.get_cart_product_count(p)
			json_data["cart_icon_count"] = u.cart_products.count() # 购物车产品数量
			json_data['cart_total_price'] = u.cart_total_price() # 购物车总价
			emit('cart', json_data)
		db.session.commit()
	elif action == 2:
		if p is None:
			current_app.logger.debug('错误, 无此产品')
			emit('error', data="TODO:")
			return
		current_app.logger.debug("从购物车删除")
		if u.reduce_from_cart(p, count):
			json_data["cart_product_count"] = u.get_cart_product_count(p)
			json_data["cart_icon_count"] = u.cart_products.count() # 购物车产品数量
			json_data['cart_total_price'] = u.cart_total_price() # 购物车总价
			emit('cart', json_data)
		else:
			json_data['products'] = get_cart_product_json_list(u)
			json_data['action'] = 4
			json_data["cart_icon_count"] = u.cart_products.count() # 购物车产品数量
			json_data['cart_total_price'] = u.cart_total_price() # 购物车总价
			emit('cart', json_data)
		db.session.commit()
	elif action == 3:
		current_app.logger.debug("查询购物车产品数量")
		emit("cart", json_data)
	elif action == 4:
		current_app.logger.debug("更新右侧购物车视图, 获取整个购物车列表")
		json_data['products'] = get_cart_product_json_list(u)
		json_data['action'] = 4
		emit('cart', json_data)
	else:
		current_app.logger.debug("购物车 错误")
		emit('error', data="TODO:")

@socketio.on("order")
@login_required
def handle_order(json_data):
	current_app.logger.debug("handling order event")
	current_app.logger.debug(json_data)
	o = Order.query.filter_by(id=json_data['order-id']).first()
	if o is None:
		emit("error", "无此订单")
	if json_data['action'] == 1:
		op = o.products.filter_by(product_id=json_data['product-id']).first()
		if op is None:
			emit("error", "订单中无此产品")
		op.price = json_data['price']
		db.session.commit()
	elif json_data['action'] == 2:
		o.money = json_data['delivery']
		db.session.commit()
	
	json_data['product-total-price'] = o.products_total_price
	json_data['total-price'] = o.products_total_price + o.money
	emit('order', json_data)


@socketio.on("overview")
@login_required
def handle_overview():
	json_data = {}
	current_date = datetime.datetime.now().date()
	day30 = datetime.timedelta(days=30)
	orders_this_month = current_user.orders_between_date(current_date-day30, current_date)
	purchases_this_month = current_user.purchases_between_date(current_date-day30, current_date)
	json_data['sale-this-month'] = sum([o.total_price for o in orders_this_month])
	json_data['spend-this-month'] = sum([o.total_price for o in purchases_this_month])
	json_data['ongoing-orders-count'] = current_user.ongoing_orders.count()
	json_data['ongoing-purchases-count'] = current_user.ongoing_purchases.count()
	emit('overview', json_data)

	

@socketio.on("chart")
@login_required
def handle_chart(json_data):
	current_app.logger.debug("handling chart event")
	orders_this_week = [current_user.orders_on_date(datetime.datetime.now().date() - datetime.timedelta(days=d)) for d in range(6,-1, -1)]
	orders_last_week = [current_user.orders_on_date(datetime.datetime.now().date() - datetime.timedelta(days=d)) for d in range(13,6, -1)]
	if json_data['action'] == 1:
		turnover_this_week = [sum([o.total_price for o in os]) for os in orders_this_week]
		turnover_last_week = [sum([o.total_price for o in os]) for os in orders_last_week]
		order_this_week = [len(os) for os in orders_this_week]
		json_data['turnover_this_week'] = turnover_this_week
		json_data['turnover_last_week'] = turnover_last_week
		json_data['order_this_week'] = order_this_week
		emit("chart", json_data)
	elif json_data['action'] == 2:
		pass
	else:
		emit("error", "绘图错误")

@socketio.on("setting")
@login_required
def handle_setting(json_data):
	current_app.logger.debug("handling setting event")
	current_app.logger.debug(str(json_data))
	if json_data['key'] == "factory-name":
		current_user.factory.name = json_data['value']
	elif json_data['key'] == "factory-address":
		current_user.factory.address = json_data['value']
	elif json_data['key'] == "factory-contact":
		current_user.factory.contact = json_data['value']
	elif json_data['key'] == "factory-phone":
		current_user.factory.phone = json_data['value']
	elif json_data['key'] == "user-name":
		current_user.user_info.name = json_data['value']
	elif json_data['key'] == "user-phone":
		current_user.user_info.phone = json_data['value']
	elif json_data['key'] == "user-email":
		current_user.user_info.email = json_data['value']
	elif json_data['key'] == "user-address":
		current_user.user_info.address = json_data['value']
	elif json_data['key'] == "order-auto-commit":
		configuration = current_user.user_info.configuration_json
		configuration["order-auto-commit"] = json_data['value'] == "true"
		current_user.user_info.configuration_json = configuration
	elif json_data['key'] == "email-update":
		configuration = current_user.user_info.configuration_json
		configuration["email-update"] = json_data['value'] == "true"
		current_user.user_info.configuration_json = configuration
	elif json_data['key'] == "update-on-new-order":
		configuration = current_user.user_info.configuration_json
		configuration["update-on-new-order"] = json_data['value'] == "on"
		current_user.user_info.configuration_json = configuration
	elif json_data['key'] == "update-on-order-status-change":
		configuration = current_user.user_info.configuration_json
		configuration["update-on-order-status-change"] = json_data['value'] == "on"
		current_user.user_info.configuration_json = configuration
	# update-on-order-status-change
	# 如果发生错误会把正确的信息返回
	db.session.commit()
	emit('setting', json_data)