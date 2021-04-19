import flask
from flask import jsonify
from . import db_session
from .quizes import Quiz

blueprint = flask.Blueprint(
    'quiz_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/quizzes')
def get_quizzes():
    """Получение всех квизов"""
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).all()
    return jsonify(
        {
            'quizzes':
                [item.to_dict(only=('id', 'title'))
                 for item in quizzes]
        }
    )


@blueprint.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
def get_one_quiz(quiz_id):
    """Получение информации об определенном квизе"""
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'quiz': quiz.to_dict(only=(
                'id', 'title', 'questions', 'description', 'difficulty', 'game_time',
                'created_date'))
        }
    )
