from flask import render_template, session, redirect, url_for, request

from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
	"主页 显示不同的厂商" # TODO: main page
	return render_template('index.html')
