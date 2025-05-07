from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ProjectForm(FlaskForm):
    name = StringField('项目名称', validators=[
        DataRequired(message='项目名称不能为空'),
        Length(max=100, message='项目名称不能超过100个字符')
    ])
    description = TextAreaField('项目描述', validators=[
        Length(max=500, message='项目描述不能超过500个字符')
    ])
    submit = SubmitField('保存更改')