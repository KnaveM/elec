from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError

from ..models import User

class LoginForm(FlaskForm):
	username = StringField("用户名:", validators=[Required()])
	password = PasswordField("密码:", validators=[Required()])
	remember_me = BooleanField('记住我')
	submit = SubmitField("登陆")

class RegistrationForm(FlaskForm):
	username = StringField('用户名:', validators=[Required(), Length(4, 20, "用户名长度范围为[4, 20]，只能包含字母数字下划线，必须以字母开头"), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, "用户名只能为字母、数字或下划线")])
	password = PasswordField('密码:', validators=[Required(), Length(8, 20, message="密码长度范围为[8, 20]，只能包含字母数字下划线"), EqualTo('password2', message="两次输入的密码必须相同"), Regexp('^[A-Za-z0-9_]*$', message="密码只能包含字母数字下划线")])
	password2 = PasswordField("确认密码:", validators=[Required()])

	email = StringField("邮箱:", validators=[Required(), Length(1,64), Email()])
	name = StringField("姓名:", validators=[Required(), Length(2,64, "请输入正确的姓名，以身份证为准")])
	address = StringField("地址:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	phone = StringField("电话:", validators=[Required()])
	submit = SubmitField("注册")

	# TODO: validate email and usernmae
	def validate_email(self, field):
		# if User.query.filter_by()
		pass

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError("用户名已注册，请使用另一个")

class EditUserInfoForm(FlaskForm):
	email = StringField("邮箱:", validators=[Required(), Length(1,64), Email()])
	name = StringField("姓名:", validators=[Required(), Length(2,64, "请输入正确的姓名，以身份证为准")])
	address = StringField("地址:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	phone = StringField("电话:", validators=[Required()])
	submit = SubmitField("保存")


class StoreInfoForm(FlaskForm):
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的姓名")])
	address = StringField("地址:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	contact = StringField("联系人:", validators=[Required()])
	phone = StringField("电话:", validators=[Required()])
	submit = SubmitField("保存")

class FactoryInfoForm(FlaskForm):
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的姓名")])
	address = StringField("地址:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	contact = StringField("联系人:", validators=[Required()])
	phone = StringField("电话:", validators=[Required()])
	complaint_department = StringField("投诉部门", validators=[Required()])
	complaint_method = StringField("投诉方式", validators=[Required()])
	submit = SubmitField("保存")

class ProductForm(FlaskForm):
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的姓名")])
	version = StringField("版本:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	description = StringField("描述:", validators=[Required()])
	comment = StringField("备注:", validators=[Required()])
	factory = SelectField("工厂:")
	submit = SubmitField("保存")

	def __init__(self, choices, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.factory.choices = choices

