import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Statistic(SqlAlchemyBase):
    __tablename__ = 'statistic'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    quiz = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("quizes.id"), nullable=False)
    correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    passage_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
