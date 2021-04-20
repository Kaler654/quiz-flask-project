# Quizzes
💻
[Site](http://flask-quizz-project.herokuapp.com)

## Contacts
* email kaler654@mail.ru
* telegram [@kaler654](https://telegram.im/@kaler654)


## About
This project was created for people to spend time in the best way possible.
You can register on the site, complete quizzes, see the rating of all users and suggest your questions for future quizzes

#### Supported languages
+ Russian


## Home page
![gif](http://g.recordit.co/BhnUCi9x8D.gif)


## Using
`pip install -r requirements.txt`

## API

## `get_quizzes` /api/quizzes
Returns information (id, title) about all quizzes

## `get_one_quiz` /api/quizzes/<int:quiz_id>
Returns information (id, title, questions, description, difficulty, game_time, created_date) about the required quiz

## `get_questions` /api/questions
Returns information (id, question) about all questions

## `get_one_question` /api/questions/<int:quiz_id>
Returns information (id, question, answers, correct_answer, moderation, author) about the required questions
