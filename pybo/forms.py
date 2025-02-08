from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired("제목은 채워!")])
    content = TextAreaField('내용', validators=[DataRequired("내용을 채워!")])

class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired("내용을 채워!")])