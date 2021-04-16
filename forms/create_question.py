from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateQuestion(FlaskForm):
    question = StringField('Вопрос', validators=[DataRequired()])
    answers = StringField('Варианты ответа(через запятую)', validators=[DataRequired()])
    correct_answer = StringField('Правильный вариант ответа', validators=[DataRequired()])
    submit = SubmitField('Создать вопрос')
