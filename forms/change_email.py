from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class ChangeEmailForm(FlaskForm):
    """Форма изменения почты"""
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Сменить почту')
