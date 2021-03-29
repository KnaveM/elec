from flask import render_template, session, redirect, url_for, request

from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
	"主页 显示不同的厂商" # TODO: main page
	return render_template('index.html')

@main.route('/test')
def test():
	return render_template('base3.html')

@main.route('/carts')
def carts():
	"TODO: 临时使用的购物车, 用于测试功能"
	