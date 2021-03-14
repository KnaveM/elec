from flask_login import UserMixin, AnonymousUserMixin

from . import db, login_manager

class Role(db.Model):
    "用户角色"
    __tablename__ = 'roles'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # 设置编码utf8
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False,
                        index=True)  # 是否为默认角色, 默认为User
    permissions = db.Column(db.Integer)  # 权限
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "<Role %r>" % self.name

# 用户
class User(UserMixin, db.Model):
    '用户'
    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True)  # id
    email = db.Column(db.String(64), unique=True,
                      index=True)  # 邮箱, 作为身份凭证, 用于登陆
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 身份
    password_hash = db.Column(db.String(128))  # 密码
    confirmed = db.Column(db.Boolean, default=False)  # 邮箱认证标记

    username = db.Column(db.String(64), unique=True)  # 用户名, 用于显示

