from flask_login import UserMixin, AnonymousUserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
	

from . import db, login_manager

class OrderProduct(db.Model):
	"订单产品辅助表"
	__tablename__ = 'orders_products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)

	count = db.Column(db.Integer, default=0)
	price = db.Column(db.Integer, default=0)
	status = db.Column(db.Integer, default=0)
	# TODO: 待补充其他属性 orderProduct


class Order(db.Model):
	"订单"
	__tablename__ = 'orders'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	status = db.Column(db.Integer, default=0)  # 状态
	money = db.Column(db.Integer, nullable=False)
	deadline = db.Column(db.DateTime, nullable=False)
	#validation = 
	feedback_type = db.Column(db.Integer)
	feedback = db.Column(db.String(2000))

	store_id = db.Column(db.Integer, db.ForeignKey('store_infos.id')) # 物业<-订单
	factory_id = db.Column(db.Integer, db.ForeignKey('factory_infos.id')) # 工厂<-订单
	payment_id = db.Column(db.Integer, db.ForeignKey('payments.id')) # order-payment
	validation_id = db.Column(db.Integer, db.ForeignKey('validations.id'))
	products = db.relationship('OrderProduct', backref=db.backref('order', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

class Validation(db.Model):
	'支付方式'
	__tablename__ = 'validations'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	satus = db.Column(db.Integer, default=0) # 状态

	order = db.relationship('Order', backref=db.backref('validation'), uselist=False) # order-validation

class Payment(db.Model):
	'支付方式'
	__tablename__ = 'payments'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	method = db.Column(db.Integer, default=0, nullable=False)  # 支付方式
	status = db.Column(db.Integer, default=0)
	order = db.relationship('Order', backref=db.backref('payment'), uselist=False)  # order-payment

class Product(db.Model):
	'产品信息'
	__tablename__ = 'products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(1000))
	version = db.Column(db.String(20))
	description = db.Column(db.String(2000))
	comment = db.Column(db.Text)

	orders = db.relationship('OrderProduct', backref=db.backref('products', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	#factories = db.relationship()  # TODO: 与厂商多对多
	factory_id = db.Column(db.Integer, db.ForeignKey("factory_infos.id")) # factory<-product 

class UserInfo(db.Model):
	'用户信息'
	__tablename__ = 'user_infos'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	email = db.Column(db.String(64)) # 邮箱 
	confirmed = db.Column(db.Boolean, default=False)  # 邮箱认证标记
	name = db.Column(db.String(100)) # 真实姓名
	address = db.Column(db.String(1000))  # 地址
	phone = db.Column(db.String(20))

	credit = db.Column(db.Integer, default=60)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user-userinfo 一对一

	def __repr__(self):
		return "<UserInfo {} email:{}>".format(self.id, self.email)

class StoreInfo(db.Model):
	'相当于送货地址 物业 中间商 代理 销售'
	__tablename__ = 'store_infos'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(100), nullable=False) # 真实姓名
	address = db.Column(db.String(1000), nullable=False)  # 地址 
	contact = db.Column(db.String(100), nullable=False) # 联系人
	phone = db.Column(db.String(20), nullable=False)

	orders = db.relationship('Order', backref=db.backref('store')) # store<-order
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user< -storeinfo 一对多


class FactoryInfo(db.Model):
	'厂商信息 供应商'
	__tablename__ = 'factory_infos'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(100), nullable=False) # 真实姓名
	address = db.Column(db.String(1000), nullable=False)  # 地址
	contact = db.Column(db.String(100), nullable=False) # 联系人
	phone = db.Column(db.String(20), nullable=False) # 联系方式
	complaint_department = db.Column(db.String(100), nullable=False) # 投诉部门
	complaint_method = db.Column(db.String(1000), nullable=False)  # 投诉方式

	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user-factory 一对一
	products = db.relationship('Product', backref=db.backref('factory')) # factory<-product
	orders = db.relationship('Order', backref=db.backref('factory'), lazy='joined') # 工厂<-订单

class Permission:
	GUEST = 1 # 普通用户只能登陆，需要注册sotre或factory
	STORE_OWNER = 2 # 物业 存在门店的用户
	STORE_STAFF = 3
	FACTORY_OWNER = 4 # 厂商 存在工厂的用户
	FACTORY_STAFF = 5


users_roles = db.Table('tags',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

class Role(db.Model):
	__tablename__ = "roles"
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(64), unique=True, nullable=False) # 名称
	permissions = db.Column(db.Integer)

	users = db.relationship("User", secondary=users_roles, backref=db.backref('roles', lazy='dynamic'))  # 用户<->角色 多对多
	
	@staticmethod
	def init_roles():
		r1 = Role(name="guest", permissions=Permission.GUEST)
		db.session.add(r1)
		r2 = Role(name="store_owner", permissions=Permission.STORE_OWNER)
		db.session.add(r2)
		r3 = Role(name="store_staff", permissions=Permission.STORE_STAFF)
		db.session.add(r3)
		r4 = Role(name="factory_owner", permissions=Permission.FACTORY_OWNER)
		db.session.add(r4)
		r5 = Role(name="factory_staff", permissions=Permission.FACTORY_STAFF)
		db.session.add(r5)
		db.session.commit()

class User(db.Model, UserMixin):
	'用户 登陆信息'
	__tablename__ = 'users'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id

	# user_type = db.Column(db.Integer, default=1)  #默认为普通用户
	username = db.Column(db.String(64), unique=True)  # 用户名, 用于显示
	password_hash = db.Column(db.String(128))  # 密码

	master_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	subordinates = db.relationship("User", back_populates="master")
	master = db.relationship("User", back_populates="subordinates", remote_side=[id]) # 子账户多对一主账户

	user_info = db.relationship('UserInfo', backref=db.backref('user'), uselist=False) # user-userinfo 外键用户 一对一
	stores = db.relationship('StoreInfo', backref=db.backref('user')) # user<-storeinfo 外键用户 一对多
	factorys = db.relationship('FactoryInfo', backref=db.backref('user')) # user<-factoryinfo 外键用户 一对多

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if len(self.roles.all()):
			pass
		else:
			self.roles.append(Role.query.filter_by(name="guest").first())
			db.session.add(self)
			db.session.commit()
			

	def can(self, permissions):
		'用户权限认证'
		return (self.role.permissions & permissions)==permissions

	@property
	def passwrod(self):
		raise AttributeError('password is not a readable attribute')
	@passwrod.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

class AnonymousUser(AnonymousUserMixin):
	"匿名用户"
	def can(self, permissions):
		return False

login_manager.anonymous_user = AnonymousUser

@login_manager.unauthorized_handler
def unauthorized_callback():
	from flask import redirect, flash, url_for
	flash("请先登陆")
	return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
