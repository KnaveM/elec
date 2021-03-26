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
	status = db.Column(db.Integer, default=0)  # 处理退款等
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

	payment_number = db.Column(db.String(20)) # 支付单号
		
	# validation_id = db.Column(db.Integer, db.ForeignKey('validations.id')) # TODO: 验收方式

	# MARK: 外键一对多
	store_id = db.Column(db.Integer, db.ForeignKey('store_infos.id')) # 物业<-订单 相当于地址
	payment_id = db.Column(db.Integer, db.ForeignKey('payments.id')) # order->payment 支付方式

	# MARK: 外键多对多
	products = db.relationship('OrderProduct', backref=db.backref('order', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def __init__(self, buyer_store, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.store_id = buyer_store.id
		db.session.add(self)
		db.session.flush()

class Validation(db.Model):
	'验收方式' # TODO: 验收方式
	__tablename__ = 'validations'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	satus = db.Column(db.Integer, default=0) # 状态

	# order = db.relationship('Order', backref=db.backref('validation'), uselist=False) # order-validation

class Payment(db.Model):
	'支付方式'
	__tablename__ = 'payments'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(20), default=0, nullable=False)  # 支付方式
	# status = db.Column(db.Integer, default=0)

	# MARK: 外键一对多
	orders = db.relationship('Order', backref=db.backref('payment'), uselist=False)  # order-payment

class Product(db.Model):
	'产品信息'
	__tablename__ = 'products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(1000))
	version = db.Column(db.String(20))
	description = db.Column(db.String(2000))
	comment = db.Column(db.Text)

	# MARK: 外键一对多
	factory_id = db.Column(db.Integer, db.ForeignKey("factory_infos.id")) # factory<-product 

	# MARK: 外键多对多
	orders = db.relationship('OrderProduct', backref=db.backref('products', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def __init__(self, factory, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		factory.add_product(self)
		db.session.add(self)
		db.session.flush()


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
	roles = db.relationship('Role', backref=db.backref('store'), lazy='joined')
	# user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # user< -storeinfo 一对多

	def __init__(self, user, *args, **kwargs) -> None:
		"新建物业store"
		super().__init__(*args, **kwargs)
		db.session.add(self)
		db.session.flush()
		r1 = Role(name='store_owner', permissions=Permission.STORE_OWNER, store_id=self.id)
		r2 = Role(name='store_staff', permissions=Permission.STORE_STAFF, store_id=self.id)
		db.session.add(r1)
		db.session.add(r2)
		db.session.flush()
		
		user.roles.append(r1)
		db.session.add(user)
		db.session.flush()

factorys_payments = db.Table('factorys_payments',
    db.Column('factory_id', db.Integer, db.ForeignKey('factory_infos.id')),
    db.Column('payment_id', db.Integer, db.ForeignKey('payments.id'))
)

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

	# MARK: 外键一对多
	roles = db.relationship("Role", backref=db.backref("factory"), lazy="joined")
	products = db.relationship('Product', backref=db.backref('factory')) # factory<-product
	# MARK: 外键多对多
	payments = db.relationship("Payment", secondary=factorys_payments, backref=db.backref('factorys', lazy='dynamic'))  # 用户<->角色 多对多

	def __init__(self, user, *args, **kwargs) -> None:
		"新建工厂factory"
		super().__init__(*args, **kwargs)
		db.session.add(self)
		db.session.flush()
		r1 = Role(name='factory_owner', permissions=Permission.FACTORY_OWNER, factory_id=self.id)
		r2 = Role(name='factory_order_manager', permissions=Permission.FACTORY_ORDER_MANAGER, factory_id=self.id)
		r3 = Role(name='factory_product_manager', permissions=Permission.FACTORY_PRODUCT_MANAGER, factory_id=self.id)
		db.session.add(r1)
		db.session.add(r2)
		db.session.add(r3)
		db.session.flush()
		
		user.roles.append(r1)
		db.session.add(user)
		db.session.flush()

	def add_product(self, product):
		self.products.append(product)
class Permission:
	STORE_OWNER = 0b1 # 物业 存在门店的用户
	STORE_STAFF = 0b10
	FACTORY_OWNER = 0b100 # 厂商 存在工厂的用户
	FACTORY_PRODUCT_MANAGER = 0b1000
	FACTORY_ORDER_MANAGER = 0b10000


users_roles = db.Table('users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class Role(db.Model):
	__tablename__ = "roles"
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(64), nullable=False) # 名称
	permissions = db.Column(db.Integer)

	# MARK: 外键一对一

	# MARK: 外键一对多
	store_id = db.Column(db.Integer, db.ForeignKey("store_infos.id")) # store <- role 一对多
	factory_id = db.Column(db.Integer, db.ForeignKey("factory_infos.id"))  # factory <- role 一对多

	# MARK: 外键多对多
	# MARK: 用户
	users = db.relationship("User", secondary=users_roles, backref=db.backref('roles', lazy='dynamic'))  # 用户<->角色 多对多

	def can(self, permissions):
		"判断权限"
		return (self.permissions & permissions) == permissions

	def do(self, method, permissions, *args, **kwargs):
		"检测权限后执行"
		if self.can(permissions):
			return method(*args, **kwargs)
		from .errors import NeedAuthorizedError
		raise NeedAuthorizedError("无权限")
	
	# MARK: 账户管理
	def add_subordinate(self, username, password):
		"master_account主账户, username用户名, password密码"
		new_user = User(username=username, password=password, master_id=self.id)
		db.session.add(new_user)
		db.session.commit()

	def edit_subordinate(self, sub, old_role, new_role):
		pass # TODO: edit subor

	# MARK: 产品管理
	def search_product_list(self):
		pass

	def add_product(self):
		pass

	def edit_product(self):
		pass

	def delete_product(self):
		pass

	# MARK: 订单管理
	def analysis(self):
		pass

	def create_order(self):
		pass

	def edit_order(self):
		pass

	def order_add_product(self):
		pass

class User(db.Model, UserMixin):
	'用户 登陆信息'
	__tablename__ = 'users'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id

	username = db.Column(db.String(64), unique=True)  # 用户名, 用于显示
	password_hash = db.Column(db.String(128))  # 密码

	# MARK: 外键一对一
	# MARK: 用户信息 一对一
	user_info = db.relationship('UserInfo', backref=db.backref('user'), uselist=False) # user-userinfo 外键用户 一对一

	# MARK: 外键一对多
	# MARK: 子账户主从关系 
	master_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	master = db.relationship("User", back_populates="subordinates", remote_side=[id]) # 子账户多对一主账户
	subordinates = db.relationship("User", back_populates="master")

	# MARK: 外键多对多
	# roles

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	

	def can(self, role:Role):
		'用户权限认证'
		return role in self.roles # 如果有这个角色
		

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
	def can(self, role):
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
