import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    correct_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)


