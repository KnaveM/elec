import os

class Config:
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 邮箱配置
    SECRET_KEY = 'password'  # TODO: 设置一个密码
    ANTI_MAIL_SUBJECT_PREFIX = '[]'
    # ANTI_MAIL_SENDER = 'Anti Admin <admin@anti.com>'
    ANTI_MAIL_SENDER = "Admin<@qq.com>"  # TODO: 信息中的sender和发件者设置为不同的地址
    ANTI_ADMIN = "Admin"  # os.environ.get('ANTI_ADMIN')

    @staticmethod
    def init_app(app):
        pass
   

class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/elec'
    DEBUG = True
    # 邮箱配置
    ANTI_ADMIN = ''
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''  # os.environ.get('MAIL_USERNAME')  # 获取系统中的环境变量
    MAIL_PASSWORD = ''  # os.environ.get('MAIL_PASSWORD')
    # 数据库配置
    


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/anti'


class ProductionConfig(Config):
    AI_PATH = ""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/anti'


config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}