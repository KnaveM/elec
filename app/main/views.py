from app.models import Product
from flask import render_template, session, redirect, url_for, request, current_app
from flask_login import login_required

from . import main
from .. import socketio

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
	return render_template('search.html')

@main.route('/product')
def product():
	return render_template('product.html')

# for testing socketio

@socketio.on('connect')
def test_connect():
	current_app.logger.debug('server is connected, this is a debug message')

@socketio.on('message')
def handle_message(data):
	current_app.logger.debug('get message envent')