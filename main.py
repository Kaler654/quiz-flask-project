from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.quizes import Quiz
from data.statistic import Statistic
from data.questions import Question
from forms.user import RegisterForm
from forms.login_form import LoginForm
from forms.create_question import CreateQuestion
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)

# Счётчик текущего вопроса в квизе
current_question = 0
# True - если игрок отвечает на вопрос, False - если игрок хочет перейти к следующему вопросу
quiz_stage = True
# Словарь словарей для сбора выполненых вопросов и квизов
count_corr_answers = 0

user_info = {
    "quiz": {}
}


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def add_user_info(correct_answers, quiz):
    global user_info
    user_info["quiz"]["id"] = quiz.id
    user_info["quiz"]["correct_answers"] = correct_answers
    db_sess = db_session.create_session()
    statistic = Statistic(
        user=current_user.id,
        quiz=quiz.id,
        correct_answers=correct_answers,
    )
    db_sess.add(statistic)
    db_sess.commit()


def get_results(correct_answers, quiz):
    count_questions = len(quiz.questions.split("~"))
    percent = correct_answers / count_questions * 100
    return render_template("complete_quiz.html", corr_answers=correct_answers,
                           count_questions=count_questions, percent=percent)


@app.route('/quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def quiz(id):
    global current_question, quiz_stage, count_corr_answers
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == id).first()
    questions_id = list(map(int, quiz.questions.split("~")))
    try:
        current_question_id = questions_id[current_question]
        question = db_sess.query(Question).filter(Question.id == current_question_id).first()
        question_answers = question.answers.split("~")
    except IndexError:
        quiz_stage = True
        current_question = 0
        percent = round(count_corr_answers / len(questions_id) * 100, 1)
        return render_template("complete_quiz.html", corr_answers=count_corr_answers,
                               count_questions=len(questions_id), percent=percent)
    if request.method == 'GET':
        current_question = 0
        count_corr_answers = 0
        return render_template('quiz.html', number_of_question=current_question + 1,
                               count_of_questions=len(questions_id), question=question,
                               answers=question_answers, btn_text="Ответить", answer_index=0)
    elif request.method == 'POST':
        if quiz_stage:
            quiz_stage = False
            try:
                answer_index = question_answers.index(request.form["answer"])
            except ValueError:
                quiz_stage = True
                current_question = 0
                add_user_info(count_corr_answers, quiz)
                percent = round(count_corr_answers / len(questions_id) * 100, 1)
                return render_template("complete_quiz.html", corr_answers=count_corr_answers,
                                       count_questions=len(questions_id), percent=percent)
            correct_answer_index = question_answers.index(question.correct_answer)
            if request.form["answer"].strip() == question.correct_answer.strip():
                count_corr_answers += 1
            current_question += 1
            return render_template('quiz.html',
                                   number_of_question=current_question + 1,
                                   count_of_questions=len(questions_id), question=question,
                                   answers=question_answers, btn_text="Следующий вопрос",
                                   answer_index=answer_index + 1,
                                   corr_answer_index=correct_answer_index + 1)
        else:
            quiz_stage = True
            return render_template('quiz.html',
                                   number_of_question=current_question + 1,
                                   count_of_questions=len(questions_id), question=question,
                                   answers=question_answers, btn_text="Ответить", answer_index=0)


@app.route('/profile/<user>')
@login_required
def profile(user):
    return render_template("profile.html", user=current_user)


@app.route('/create_question_info', methods=['GET', 'POST'])
@login_required
def create_question_info():
    return render_template('create_question_info.html')


@app.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    form = CreateQuestion()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        last_quest_id = db_sess.query(Question)[-1].id
        file = request.files["file"]
        path = f"static/img/questions/question_{last_quest_id + 1}.jpg"
        file.save(path)
        question = Question(
            question=form.question.data,
            image="../" + path,
            answers=form.answers.data,
            correct_answer=form.correct_answer.data,
        )
        db_sess.add(question)
        db_sess.commit()
        return redirect(f"profile/{current_user.name}")
    return render_template('create_question.html', form=form)


def main():
    db_session.global_init("db/data.db")
    app.run()


if __name__ == '__main__':
    main()
