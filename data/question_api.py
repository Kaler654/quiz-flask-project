import flask
from flask import jsonify
from . import db_session
from .questions import Question

# Создание схемы
blueprint = flask.Blueprint(
    'question_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/questions')
def get_questions():
    """Получение всех вопросов для квизов"""
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    return jsonify(
        {
            'questions':
                [item.to_dict(only=('id', 'question'))
                 for item in questions]
        }
    )


@blueprint.route('/api/questions/<int:question_id>', methods=['GET'])
def get_one_question(question_id):
    """Получение информации об определенном вопросе"""
    db_sess = db_session.create_session()
    question = db_sess.query(Question).get(question_id)
    if not question:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'question': question.to_dict(only=(
                'id', 'question', 'answers', 'correct_answer', 'moderation', 'author'))
        }
    )
