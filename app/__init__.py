from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment  # 日期管理
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

from config import config_dict

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
socketio = SocketIO()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'  # 用户请求了login_require的页面会被跳转到的页面


def create_app(config_name='default'):
    print(config_name)
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)  # ?这是啥
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app=app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)  # 将蓝图添加到app实例中
    
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # from .game import game as game_blueprint
    # app.register_blueprint(game_blueprint, url_prefix='/game')
    
    # from .match import match as match_blueprint
    # app.register_blueprint(match_blueprint, url_prefix='/match')
    
    return app
