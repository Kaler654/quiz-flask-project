from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditUserForm(FlaskForm):
    """Форма изменения пользователя"""
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    status = StringField('Статус', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
