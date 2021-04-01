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
    # 邮箱配置
    SECRET_KEY = 'strongpassword'  # TODO: 设置一个密码

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