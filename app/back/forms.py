from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SubmitField, BooleanField, SelectField, FileField, TextAreaField, TextField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.fields.core import IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
import json

from ..models import User


class StoreInfoForm(FlaskForm):
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的姓名")])
	address = StringField("地址:", render_kw={'readonly': False}, validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	contact = StringField("联系人:", validators=[Required()])
	phone = StringField("电话:", validators=[Required()])
	submit = SubmitField("保存", render_kw={"class": "btn app-btn-secondary"})  # submit的class无效

	def __init__(self, address_readonly=False, view_only=False, **kwargs):
		super().__init__(**kwargs)
		if address_readonly:
			self.address.render_kw = {'readonly': True}
		if view_only:
			self.name.render_kw = {'readonly': True}
			self.address.render_kw = {'readonly': True}
			self.contact.render_kw = {'readonly': True}
			self.phone.render_kw = {'readonly': True}
			self.submit.render_kw = {"style": "display: none;"}

		

class FactoryInfoForm(FlaskForm):
	name = StringField("名称:", validators=[Required(), Length(2,64, "请输入正确的姓名")])
	address = StringField("地址:", validators=[Required(), Length(-1, 1000, "地址最多不超过1000字符")])
	contact = StringField("联系人:", validators=[Required()])
	phone = StringField("电话:", validators=[Required()])
	complaint_department = StringField("投诉部门", validators=[Required()])
	complaint_method = StringField("投诉方式", validators=[Required()])
	submit = SubmitField("保存")

class ProductForm(FlaskForm):
	name = TextAreaField("标题:", validators=[Required(), Length(10,64, "请输入正确的产品名, 字符数限制为[10, 64]")], render_kw={"autoheight": True})
	subtitle = TextAreaField("子标题:", validators=[Required("请输入产品的副标题")])
	img1 = FileField("主图1")  # TODO: file allowed
	img2 = FileField("主图2")
	img3 = FileField("主图3")
	img4 = FileField("主图4")
	img5 = FileField("主图5")
	
	price = IntegerField("参考单价:", validators=[Required("请输入产品的单价")])
	# description = StringField("详情描述:", validators=[Required()])
	specification = TextAreaField("参数:", validators=[Required(), Length(-1, 5000, "详情最多不超过1000字符")])
	# comment = StringField("备注:", validators=[Required()])
	# factory = SelectField("工厂:")
	submit = SubmitField("保存")

	def __init__(self, product=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# self.factory.choices = choices

		if  product:
			# 不能在此修改data中的内容, 为啥呢???
			# self.name.data = product.name
			# self.subtitle.data = product.subtitle
			# self.price.data = product.price
			# self.specification.data = json.dumps(product.specification_json)
			self.img1.url = product.image_url(1)
			self.img2.url = product.image_url(2)
			self.img3.url = product.image_url(3)
			self.img4.url = product.image_url(4)
			self.img5.url = product.image_url(5)
		else:
			self.img1.validators = [FileRequired("请上传主图")]
			self.img2.validators = [FileRequired("请上传主图")]
			self.img3.validators = [FileRequired("请上传主图")]
			self.img4.validators = [FileRequired("请上传主图")]
			self.img5.validators = [FileRequired("请上传主图")]

