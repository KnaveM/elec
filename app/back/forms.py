from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SubmitField, BooleanField, SelectField, FileField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.fields.core import IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError

from ..models import User


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
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的产品名")])
	img1 = FileField("主图1", validators=[FileRequired()])
	img2 = FileField("主图2", validators=[FileRequired()])
	img3 = FileField("主图3", validators=[FileRequired()])
	img4 = FileField("主图4", validators=[FileRequired()])
	img5 = FileField("主图5", validators=[FileRequired()])
	subtitle = StringField("子标题:", validators=[Required()])
	price = IntegerField("单价:", validators=[Required()])
	# description = StringField("详情描述:", validators=[Required()])
	specification = StringField("参数:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	# comment = StringField("备注:", validators=[Required()])
	factory = SelectField("工厂:")
	submit = SubmitField("保存")

	def __init__(self, choices, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.factory.choices = choices


