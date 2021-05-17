import os
import sys
from datetime import timedelta
import socket

class Config:
    DEBUG = False
    PREFERRED_URL_SCHEME = "http"
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SECRET_KEY = 'strongpassword'  # TODO: 设置一个密码

    # 邮箱配置
    # MAIL_DEBUG = False
    # MAIL_USE_SSL = True
    # MAIL_USE_TSL = False
    # MAIL_SERVER = "smtp.qq.com"
    # MAIL_PORT = 465
    # MAIL_USERNAME = os.getenv("MAIL_USERNAME") or "ERROR_USERNAME"
    # MAIL_PASSWORD = os.getenv("MAIL_PASSWORD") or "ERROR_PASSWORD"
    # # 垃圾flask-mail 别用
    # # 用qq邮箱需要修改flask-mail中的源文件内容
    # MAIL_DEFAULT_SENDER = ('大商电器', os.getenv('MAIL_USERNAME'))



    @staticmethod
    def init_app(app):
        pass
   

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@{}/elec'.format(socket.gethostbyname(socket.gethostname()))  
    DEBUG = True
    

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/elev'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/elev'


config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}