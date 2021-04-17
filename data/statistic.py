import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Statistic(SqlAlchemyBase):
    __tablename__ = 'statistic'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    quiz = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("quizes.id"), nullable=False)
    scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    user_info = orm.relation('User')
    quiz_info = orm.relation('Quiz')
