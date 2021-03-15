from flask import Flask
from flask_bootstrap import Bootstrap  # 前端模板
from flask_mail import Mail  # 邮件
from flask_moment import Moment  # 日期管理
from flask_sqlalchemy import SQLAlchemy  # 数据库
from flask_login import LoginManager  # 用于登陆管理
from flask_socketio import SocketIO  # websocket

from config import config_dict

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
# socketio = SocketIO()  # TODO: socketio配置

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'  # 用户请求了login_require的页面会被跳转到的页面


def create_app(config_name='default'):
    print('using config: ', config_name)
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    #socketio.init_app(app=app)

    # TODO: jinja2 环境变量设置
    
    # 将蓝图添加到app实例中
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
