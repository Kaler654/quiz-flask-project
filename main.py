from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.quizes import Quiz
from data.statistic import Statistic
from data.questions import Question
from forms.user import RegisterForm
from forms.login_form import LoginForm
from forms.create_question import CreateQuestion
from forms.change_password import ChangePasswordForm
from forms.change_email import ChangeEmailForm
from forms.edit_user import EditUserForm
from forms.quiz_form import QuizForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'N#pC@UzmS5kw%@$F'
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

        all_users = db_sess.query(User.name).all()
        if not all([form.name.data != user_name[0] for user_name in all_users]):
            return render_template('register.html', form=form,
                                   message="Пользователь с таким именем уже есть")

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            status="Пользователь",
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
    db_sess = db_session.create_session()
    user_passed_quizzes = db_sess.query(Statistic).filter(Statistic.user == current_user.id,
                                                          Statistic.quiz == quiz.id).all()
    if len(user_passed_quizzes) == 0:
        statistic = Statistic(
            user=current_user.id,
            quiz=quiz.id,
            scores=correct_answers,
        )
        db_sess.add(statistic)
    else:
        curr_statistic = user_passed_quizzes[0]
        if correct_answers > curr_statistic.scores:
            curr_statistic.scores = correct_answers
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
        add_user_info(count_corr_answers, quiz)
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
        request.form = request.form  # Обновляет данные получаемые с формы
        if quiz_stage:
            quiz_stage = False
            try:
                answer_index = question_answers.index(request.form["answer"])
            except ValueError as e:
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
            author=current_user.id
        )
        db_sess.add(question)
        db_sess.commit()
        return redirect(f"profile/{current_user.name}")
    return render_template('create_question.html', form=form, title="Создание вопроса")


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('change_password.html', form=form, message="Пароли не совпадают")
        if len(form.password.data) < 8:
            return render_template('change_password.html', form=form,
                                   message="Пароль должен быть не меньше 8 символов")
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect(f"profile/{current_user.name}")
    return render_template('change_password.html', form=form)


@app.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        user.email = form.email.data
        db_sess.commit()
        return redirect(f"profile/{current_user.name}")
    return render_template('change_email.html', form=form)


@app.route('/my_questions')
@login_required
def my_questions():
    db_sess = db_session.create_session()
    user_questions = db_sess.query(Question).filter(Question.author == current_user.id).all()
    return render_template("my_questions.html", questions=user_questions)


@app.route('/rating')
@login_required
@login_required
def rating():
    table = {}
    db_sess = db_session.create_session()
    all_stat = db_sess.query(Statistic).all()
    for stat in all_stat:
        table[stat.user_info.name] = {}
        table[stat.user_info.name]["quizes"] = []
        table[stat.user_info.name]["scores"] = []
    for stat in all_stat:
        table[stat.user_info.name]["quizes"].append(stat.quiz)
        table[stat.user_info.name]["scores"].append(stat.scores)
    users = []
    for key in table:
        user_info = (key, len(table[key]["quizes"]), sum(table[key]["scores"]),
                     sum(table[key]["scores"]) // len(table[key]["scores"]))
        users.append(user_info)
    users = sorted(users, key=lambda x: (x[1], x[2], x[3]), reverse=True)
    return render_template("rating.html", users=users)


@app.route('/admin_panel')
@login_required
def admin():
    if current_user.id == 1 or current_user.status == "Администратор":
        return render_template("admin.html")
    abort(404)


@app.route('/all_users')
def all_users():
    if current_user.id == 1 or current_user.status == "Администратор":
        users_info = []
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        for user in users:
            users_info.append(
                (
                user.id, user.name, user.email, user.status, user.created_date.strftime("%d.%m.%Y")))
        return render_template("users.html", users=users_info, current_user=current_user)
    abort(404)


@app.route('/user_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        if id != 1:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == id).first()
            if user:
                db_sess.delete(user)
                db_sess.commit()
                return redirect('/all_users')
            else:
                abort(404)
    abort(404)


@app.route('/user_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        if id != 1:
            form = EditUserForm()
            if request.method == "GET":
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == id).first()
                if user:
                    form.name.data = user.name
                    form.email.data = user.email
                    form.status.data = user.status
                else:
                    abort(404)
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == id).first()
                if user:
                    user.name = form.name.data
                    user.email = form.email.data
                    user.status = form.status.data
                    db_sess.commit()
                    return redirect('/all_users')
                else:
                    abort(404)
            return render_template('edit_user.html', form=form, current_user=current_user)
    abort(404)


@app.route('/moderation')
@login_required
def moderation():
    if current_user.id == 1 or current_user.status == "Администратор":
        questions_info = []
        db_sess = db_session.create_session()
        questions = db_sess.query(Question).filter(Question.moderation == 0)
        for question in questions:
            questions_info.append((question.id, question.question, question.image.replace("..", ""),
                                   question.answers, question.correct_answer))
        return render_template("moderation.html", questions=questions_info)
    abort(404)


@app.route('/question_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def question_delete(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id == id).first()
        if question:
            os.remove(question.image.replace("../", ""))
            db_sess.delete(question)
            db_sess.commit()
            return redirect('/admin_panel')
    abort(404)


@app.route('/question_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def question_edit(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        form = CreateQuestion()
        if request.method == "GET":
            db_sess = db_session.create_session()
            question = db_sess.query(Question).filter(Question.id == id).first()
            if question:
                form.question.data = question.question
                form.answers.data = question.answers
                form.correct_answer.data = question.correct_answer
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            question = db_sess.query(Question).filter(Question.id == id).first()
            file = request.files["file"]
            path = f"static/img/questions/question_{question.id}.jpg"
            if file.filename != "":
                file.save(path)
            if question:
                question.question = form.question.data
                question.image = "../" + path
                question.answers = form.answers.data
                question.correct_answer = form.correct_answer.data
                db_sess.commit()
                return redirect('/all_questions')
            else:
                abort(404)
        return render_template('create_question.html', form=form, title="Изменение вопроса")
    abort(404)


@app.route('/question_approve/<int:id>', methods=['GET', 'POST'])
@login_required
def question_approve(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id == id).first()
        if question:
            question.moderation = 1
            db_sess.commit()
            return redirect('/moderation')
    abort(404)


@app.route('/all_quizzes')
def all_quizzes():
    if current_user.id == 1 or current_user.status == "Администратор":
        quizzes_info = []
        db_sess = db_session.create_session()
        quizzes = db_sess.query(Quiz).all()
        for quiz in quizzes:
            quizzes_info.append((quiz.id, quiz.title, quiz.questions.replace("~", ","),
                                 quiz.description, quiz.difficulty, quiz.game_time,
                                 quiz.created_date.strftime("%d.%m.%Y")))
        return render_template("all_quizzes.html", quizes=quizzes_info)
    abort(404)


@app.route('/quiz_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def quiz_delete(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        db_sess = db_session.create_session()
        quiz = db_sess.query(Quiz).filter(Quiz.id == id).first()
        if quiz:
            db_sess.delete(quiz)
            db_sess.commit()
            return redirect('/all_quizzes')
    abort(404)


@app.route('/quiz_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def quiz_edit(id):
    if current_user.id == 1 or current_user.status == "Администратор":
        form = QuizForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            quiz = db_sess.query(Quiz).filter(Quiz.id == id).first()
            if quiz:
                form.title.data = quiz.title
                form.questions.data = quiz.questions.replace("~", ",")
                form.description.data = quiz.description
                form.difficulty.data = quiz.difficulty
                form.game_time.data = quiz.game_time
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            quiz = db_sess.query(Quiz).filter(Quiz.id == id).first()
            if quiz:
                quiz.title = form.title.data
                quiz.questions = form.questions.data.replace(",", "~")
                quiz.description = form.description.data
                quiz.difficulty = form.difficulty.data
                quiz.game_time = form.game_time.data
                db_sess.commit()
                return redirect('/all_quizzes')
            else:
                abort(404)
        return render_template('edit_quiz.html', form=form, title="Изменение квиза")
    abort(404)


@app.route('/all_questions')
def all_questions():
    if current_user.id == 1 or current_user.status == "Администратор":
        questions_info = []
        db_sess = db_session.create_session()
        questions = db_sess.query(Question).all()
        for question in questions:
            questions_info.append((question.id, question.question, question.image.replace("..", ""),
                                   question.answers, question.correct_answer,
                                   question.moderation, question.author_info.name))
        return render_template("all_questions.html", questions=questions_info)
    abort(404)


@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = Quiz(
            title=form.title.data,
            questions=form.questions.data.replace(",", "~"),
            description=form.description.data,
            difficulty=form.difficulty.data,
            game_time=form.game_time.data
        )
        db_sess.add(quiz)
        db_sess.commit()
        return redirect("/admin_panel")
    return render_template('edit_quiz.html', form=form, title="Создание квиза")


@app.route('/quizzes')
def quizzes():
    quizzes_info = []
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).all()
    for quiz in quizzes:
        quizzes_info.append((quiz.id, quiz.title, quiz.description, quiz.difficulty,
                             len(quiz.questions.split("~")), quiz.game_time,
                             quiz.created_date.strftime("%d.%m.%Y")))
    return render_template('quizzes.html', quizzes=quizzes_info, title="Все квизы",
                           description="Полный набор наших квизов")


@app.route("/movie")
def movie():
    quizzes_info = []
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).filter(Quiz.title.like("%Кино%"))
    for quiz in quizzes:
        quizzes_info.append((quiz.id, quiz.title, quiz.description, quiz.difficulty,
                             len(quiz.questions.split("~")), quiz.game_time,
                             quiz.created_date.strftime("%d.%m.%Y")))
    return render_template('quizzes.html', quizzes=quizzes_info, title="Кино",
                           description="Подборка викторин с вопросами про кино")


@app.route("/thematic")
def thematic():
    quizzes_info = []
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).filter(Quiz.title.like("%Тематическая%"))
    for quiz in quizzes:
        quizzes_info.append((quiz.id, quiz.title, quiz.description, quiz.difficulty,
                             len(quiz.questions.split("~")), quiz.game_time,
                             quiz.created_date.strftime("%d.%m.%Y")))
    return render_template('quizzes.html', quizzes=quizzes_info, title="Тематические",
                           description="Викторины с вопросами на различные темы")


@app.route("/logic")
def logic():
    quizzes_info = []
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).filter(Quiz.title.like("%Логика%"))
    for quiz in quizzes:
        quizzes_info.append((quiz.id, quiz.title, quiz.description, quiz.difficulty,
                             len(quiz.questions.split("~")), quiz.game_time,
                             quiz.created_date.strftime("%d.%m.%Y")))
    return render_template('quizzes.html', quizzes=quizzes_info, title="Логика",
                           description="Викторины с вопросами на логику")


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html")


@app.errorhandler(401)
def not_found(error):
    return redirect("/login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/data.db")
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
