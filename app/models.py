from flask_login import UserMixin, AnonymousUserMixin
import datetime

from . import db, login_manager

# 物业=线下门店=厂商客户
# 厂商=供应商

orders_products = db.Table('orders_products',
		db.Column('order_id', db.Integer, db.ForeignKey('orders.id')),
		db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
		db.Column('count', db.Integer, default=0, nullable=False),
		db.Column('price', db.Integer, default=0, nullable=False))


class Order(db.Model):
	"订单"
	__tablename__ = 'orders'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	
	money = db.Column(db.Integer, nullable=False)
	deadline = db.Column(db.DateTime, nullable=False)
	# payment =  # 外键?
	#validation = 
	feedback_type = db.Column(db.Integer)
	feedback = db.Column(db.String(2000))

	store_id = db.Column(db.Integer, db.ForeignKey('store_infos.id')) # 物业<-订单
	products = db.relationship('Product', backref=db.backref('orders', lazy='dynamic'), secondary=orders_products)
	# order<->product

class Product(db.Model):
	'产品信息'
	__tablename__ = 'products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(1000))
	version = db.Column(db.String(20))
	description = db.Column(db.String(2000))
	comment = db.Column(db.Text)

	# order<->product 此处不用写
	#factories = db.relationship()  # TODO: 与厂商多对多

class UserInfo(db.Model):
	'用户信息'
	__tablename__ = 'user_infos'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	email = db.Column(db.String(64), nullable=False) # 邮箱 
	confirmed = db.Column(db.Boolean, default=False)  # 邮箱认证标记
	name = db.Column(db.String(100), nullable=False) # 真实姓名
	address = db.Column(db.String(1000), nullable=False)  # TODO: continue
	credit = db.Column(db.Integer, default=60, nullable=False)
	phone = db.Column(db.String(20), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user-userinfo 一对一


class StoreInfo(db.Model):
	'物业 中间商 代理 销售'
	__tablename__ = 'store_infos'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(100), nullable=False) # 真实姓名
	address = db.Column(db.String(1000), nullable=False)  # 地址 
	contact = db.Column(db.String(100), nullable=False) # 联系人
	phone = db.Column(db.String(20), nullable=False)

	orders = db.relationship('Order', backref=db.backref('store')) # store<-order
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user-storeinfo 一对一


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


class User(UserMixin, db.Model):
	'用户 登陆信息'
	__tablename__ = 'users'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id

	user_type = db.Column(db.Integer, default=1)
	username = db.Column(db.String(64), unique=True)  # 用户名, 用于显示
	password_hash = db.Column(db.String(128))  # 密码

	user_info = db.relationship('UserInfo', backref=db.backref('user'), uselist=False) # user-userinfo 外键用户 一对一
	store_info = db.relationship('StoreInfo', backref=db.backref('user'), uselist=False) # user-storeinfo 外键用户 一对一
	factory_info = db.relationship('FactoryInfo', backref=db.backref('user'), uselist=False) # user-factoryinfo 外键用户 一对一