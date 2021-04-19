from flask import Flask
from flask_login import LoginManager
import datetime

# Конфигурация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'N#pC@UzmS5kw%@$F'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

#  Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Счётчик текущего вопроса в квизе
current_question = 0
# True - если игрок отвечает на вопрос, False - если игрок хочет перейти к следующему вопросу
quiz_stage = True
# Счётчик правильных вопросов квиза
count_corr_answers = 0

# Импорт обработчиков
from views import *


def main():
    # Начальная инициализация БД
    db_session.global_init("db/data.db")
    # Регистрация методов API
    app.register_blueprint(quiz_api.blueprint)
    app.register_blueprint(question_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run()


if __name__ == '__main__':
    main()
