import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quizes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    questions = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    difficulty = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    game_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    current_question = 0

    def is_last_question(self):
        if len(self.questions.split("~")) <= self.current_question:
            return True
        return False

    def get_current_question_index(self):
        return self.current_question

    def get_next_question_index(self):
        self.current_question += 1
        return self.current_question
