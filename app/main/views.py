from flask import render_template, session, redirect, url_for, request

from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    print(request)
    return 'successs'

