from flask.globals import current_app
from flask.helpers import url_for
from flask_login import UserMixin, AnonymousUserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json


from . import db, login_manager

class OrderProduct(db.Model):
	"订单产品辅助表"
	__tablename__ = 'orders_products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)

	count = db.Column(db.Integer, default=0)
	price = db.Column(db.Integer, default=0) # 定制价格
	status = db.Column(db.Integer, default=0)  # 处理退款等
	# TODO: 待补充其他属性 orderProduct

	@property
	def product(self):
		return Product.query.filter_by(id=self.product_id).first()

class OrderStatus:
	"订单的状态"
	CREATED = 0 # 初始化
	WAIT_PAYMENT = 1 # 等待买家付款
	PENDING = 2 # 处理中, 等待买家收货
	WAIT_COMMENT = 3 # 买家已确认收货
	COMMENTED = 4 # 买家已评论, 全部流程已结束

	@staticmethod
	def to_str(status):
		if status==OrderStatus.CREATED:
			return "初始化"
		elif status==OrderStatus.WAIT_PAYMENT:
			return "等待支付"
		elif status==OrderStatus.PENDING:
			return "正在处理"
		elif status==OrderStatus.WAIT_COMMENT:
			return "等待评论"
		elif status==OrderStatus.COMMENTED:
			return "已评论"
		else:
			return "错误"

class Order(db.Model):
	"订单"
	__tablename__ = 'orders'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	status = db.Column(db.Integer, default=0)  # 状态
	money = db.Column(db.Integer)  #运费?
	deadline = db.Column(db.DateTime)
	create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	#validation = 
	feedback_type = db.Column(db.Integer)
	feedback = db.Column(db.String(2000))

	payment_number = db.Column(db.String(20)) # 支付单号
		
	# validation_id = db.Column(db.Integer, db.ForeignKey('validations.id')) # TODO: 验收方式

	# buyer_agent 买家代理账户
	# saler_agent 卖家代理账户

	# MARK: 外键一对多
	store_id = db.Column(db.Integer, db.ForeignKey('store_infos.id')) # 物业<-订单 相当于地址
	payment_id = db.Column(db.Integer, db.ForeignKey('payments.id')) # order->payment 支付方式

	# MARK: 外键多对多
	products = db.relationship('OrderProduct', backref=db.backref('order', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def __init__(self, buyer_store, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.store_id = buyer_store.id
		db.session.add(self)
		# db.session.flush() # 不需要获得id

	def add_product(self, product, count=1):
		op = self.products.filter_by(product_id=product.id).first()
		if op:
			op.count += count
		else:
			op = OrderProduct(order_id=self.id, product_id=product.id, count=count)
			op.price = product.price
			self.products.append(op)
		db.session.add(self)
		return op
			

	def reduce_product(self, product, count):
		"TODO: 订单不需要删除吧?"
		op = self.products.filter_by(product_id=product.id).first()
		if op:
			op.count -= count
			if op.count == 0:
				self.products.remove(op)
				return None
		else:
			return None
		db.session.add(self)
		return op

	@property
	def products_total_price(self):
		return sum([op.count*op.price for op in self.products.all()])

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


class Cart(db.Model):
	"用户购物车辅助表 备货单"
	__tablename__ = 'carts'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)

	count = db.Column(db.Integer, default=1, nullable=False)

	# 外键
	store_id = db.Column(db.Integer, db.ForeignKey("store_infos.id")) # 目的地

	@staticmethod
	def _delete_product(product):
		ps = Cart.query.filter_by(product_id=product.id).all()
		[db.session.delete(p) for p in ps]

class Product(db.Model):
	'产品信息'
	__tablename__ = 'products'
	__table_args__ = {'mysql_collate': 'utf8_general_ci'}

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id
	name = db.Column(db.String(1000)) #标题
	price = db.Column(db.Integer) # 单价
	# 图片必须要有五张 直接以id-1/2/3/4/5来管理即可
	subtitle = db.Column(db.String(2000)) # 副标题
	specification = db.Column(db.String(2000))  # json str 产品参数
	description = db.Column(db.String(2000)) # TODO: 不使用
	comment = db.Column(db.Text)

	# MARK: 外键一对多
	factory_id = db.Column(db.Integer, db.ForeignKey("factory_infos.id")) # factory<-product
	cart = db.relationship("Cart", backref=db.backref('product', uselist=False))

	# MARK: 外键多对多
	orders = db.relationship('OrderProduct', backref=db.backref('products', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def __init__(self, factory, *args, **kwargs) -> None:
		"通过工厂生成, 默认flush生成产品id"
		super().__init__(*args, **kwargs)
		factory.add_product(self)
		db.session.add(self)
		db.session.flush()

	@property
	def specification_json(self):
		try:
			js = json.loads(self.specification)
			return js
		except Exception as e:
			current_app.logger.error("解析product.specification错误: %s", e)
			return {}

	@specification_json.setter
	def specification_json(self, s_js):
		self.specification = json.dumps(s_js)

	def image_url(self, no=1):
		return url_for('static', filename="assets/db/images/p"+str(self.id)+"_"+str(no))

	def delete(self):
		# 先删除外键
		Cart._delete_product(self)
		db.session.delete(self)

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

	def __init__(self, user, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		user.user_info = self
		db.session.add(self)

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

	@property
	def owner(self):
		return [r.users[0] for r in self.roles if r.permissions==Permission.STORE_OWNER][0]

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
	cart_products = db.relationship('Cart', backref=db.backref('user', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan') # 购物车中的产品

	def __init__(self, *args, **kwargs):
		super().__init__(*args, username=kwargs['username'], password=kwargs['password'])
		db.session.add(self)
		userinfo = UserInfo(self, email=kwargs["email"], name=kwargs["name"], address=kwargs["address"], phone=kwargs["phone"])
		db.session.add(userinfo)
	
	@property
	def stores(self):
		"一个账号可以有多个门店"
		return [r.store for r in self.roles.filter_by(permissions=Permission.STORE_OWNER).all()]


	@property
	def factory(self):
		"每个账户只能创建一个工厂"
		fr = self.roles.filter_by(permissions=Permission.FACTORY_OWNER).first()
		return fr.factory if fr is not None else None

	# DROPPED 
	@property
	def factorys(self):
		"待删除"
		return [r.factory for r in self.roles.filter_by(permissions=Permission.FACTORY_OWNER).all()]

	@property
	def products(self):
		if self.factorys:
			return Product.query.filter_by(factory_id=self.factorys[0].id).all()
		return []

	@property
	def purchases(self):
		os = []
		for store in self.stores:
			os.extend(store.orders)
		return os
	
	@property
	def orders(self):
		if self.factorys.__len__():
			return list(set(op.order for op in OrderProduct.query.filter(OrderProduct.product_id.in_(Product.query.with_entities(Product.id).filter_by(factory_id=self.factorys[0].id), )).all()))
		else:
			return []

	def gravatar(self, size=100, default='identicon', rating='g'):
		"网站被墙了不能使用了"
		import hashlib
		hash = hashlib.md5(self.username.encode()).hexdigest()
		return 'http://www.gravatar.com/avatar/{}?s={}&d={}&r={}'.format(hash, size, default, rating)

	# MARK: 购物车

	def cart_total_price(self):
		return sum([cp.count * cp.product.price for cp in self.cart_products])
			

	def get_cart_product_count(self, p):
		"查看指定产品在购物车中的数量"
		c = Cart.query.filter_by(user_id=self.id, product_id=p.id).first()
		if c is None:
			return 0
		else:
			return c.count

	def add_to_cart(self, p, count=1):
		c = Cart.query.filter_by(user_id=self.id, product_id=p.id).first()
		if c is None:
			c = Cart(user_id=self.id, product_id=p.id, count=count)
			self.cart_products.append(c)
		else:
			c.count += count
			db.session.add(c)
		db.session.add(self)

	def reduce_from_cart(self, p, count=1):
		c = Cart.query.filter_by(user_id=self.id, product_id=p.id).first()
		if c is None:
			return -1
		else:
			c.count -= count
			if c.count <= 0:
				self.cart_products.remove(c)
			db.session.add(c)
			db.session.add(self)

	def create_orders(self, store):
		"store为配送地址, 购物车根据产品所在的工厂进行分类, 同一个工厂的产品放在一张订单中, 返回订单列表, 生成的订单是初始化的订单"

		os = {}
		# o = Order(store)
		for c in self.cart_products:
			try:
				o = os[c.product.factory_id]
			except KeyError:
				os[c.product.factory_id] = Order(store)
				o = os[c.product.factory_id]
			o.add_product(c.product, c.count)
			self.reduce_from_cart(c.product, c.count)
		for tuple_o in os.items():
			db.session.add(tuple_o[1])
		return list(os.items())

	def commit_order(self, order):
		"提交订单, 设置订单状态为1未付款"
		# TODO: check
		if order.status == OrderStatus.CREATED:
			order.status = OrderStatus.WAIT_PAYMENT
		db.session.add(order)

	# MARK: 下属管理
	def add_subordinate(self, new_user):
		# check 权限
		if self.master_id is not None:
			return -1
		new_user.master_id = self.id
		db.session.add(new_user)
		return 0
	
	def delete_subordinate(self, sub):
		# check TODO: 删除要怎么写
		if sub not in self.subordinates:
			return -1
		db.session.delete(sub.user_info) # 先删除外键
		self.subordinates.remove(sub)
		db.session.add(self)

	def update_subordinate_role(self, sub, role):
		# TODO: 修改自账户权限
		pass

	# MARK: 用户登陆
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
