from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class QuizForm(FlaskForm):
    """Форма создания квиза"""
    title = StringField('Название', validators=[DataRequired()])
    questions = StringField('id вопросов(через запятую)', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    difficulty = StringField('Сложность', validators=[DataRequired()])
    game_time = StringField('Время игры', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
