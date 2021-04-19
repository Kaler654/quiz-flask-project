from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateQuestion(FlaskForm):
    """Форма создания вопроса"""
    question = StringField('Вопрос', validators=[DataRequired()])
    answers = StringField('Варианты ответа(через ~)', validators=[DataRequired()])
    correct_answer = StringField('Правильный вариант ответа', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
