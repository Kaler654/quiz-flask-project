from flask import Flask, render_template, redirect, request
from data import db_session
from data.users import User
from data.quizes import Quiz
from data.questions import Question
from forms.user import RegisterForm
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)

current_question = 0


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


@app.route('/quiz/<int:id>', methods=['GET', 'POST'])
def quiz(id):
    global current_question
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == id).first()
    questions_id = list(map(int, quiz.questions.split("~")))
    if request.method == 'GET':
        current_question_id = questions_id[current_question]
        question = db_sess.query(Question).filter(Question.id == current_question_id).first()
        question_answers = question.answers.split("~")
        return render_template('quiz.html', number_of_question=current_question + 1,
                               count_of_questions=len(questions_id), question=question,
                               answers=question_answers)
    elif request.method == 'POST':
        current_question += 1
        if current_question >= len(questions_id):
            current_question = 0
            return "Тест закончен"
        else:
            current_question_id = questions_id[current_question]
            question = db_sess.query(Question).filter(
                Question.id == current_question_id).first()
            question_answers = question.answers.split("~")
            if request.form["answer"].strip() == question.correct_answer.strip():
                print("nice")
            return render_template('quiz.html',
                                   number_of_question=current_question + 1,
                                   count_of_questions=len(questions_id), question=question,
                                   answers=question_answers)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/data.db")
    app.run()


if __name__ == '__main__':
    main()
