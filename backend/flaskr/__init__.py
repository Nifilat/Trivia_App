import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={r"*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    @app.route("/")
    def hello_world():
        return jsonify({"message": "Wecome to trivia APP"})


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/v1.0/categories')
    def all_categories():
        categories = Category.query.order_by(Category.id, Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories}
            }
        )





    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(
            Category.id).with_entities(Category.id, Category.type).all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': dict(categories),
            'current_category': dict(categories)[5]
        })

 

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """


    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404, "Question not found")

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    'total_questions': len(selection),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if body is None:
            abort(400)

        """
        @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
        """

    
        if 'searchTerm' in body:
            search_term = body.get('searchTerm', '').strip()
            questions = Question.query.filter(
                Question.question.ilike('%' + search_term + '%')).all()

            questions = [question.format() for question in questions]

            return jsonify({
                'questions': questions,
                'totalQuestions': len(questions),
                'currentCategory': questions[0]['category'] if len(questions) else ""
            })

        elif 'question' in body and 'answer' in body and 'difficulty' in body and 'category' in body:
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            try:
                new_question = Question(
                    question=question, answer=answer, difficulty=difficulty, category=category)
                new_question.insert()

            except:
                abort(422)

            return jsonify({
                "question": new_question.format(),
            })
        else:
            abort(400)

        
        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/api/v1.0/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        
        category = Category.query.get(category_id)
        if category:
            # retrive all questions in a category
            questionsInCurrentCategory = Question.query.filter_by(category=category_id).all()
            currentQuestions = paginate_questions(request, questionsInCurrentCategory)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questionsInCurrentCategory),
                'current_category': category.type
            })
        # if category not found
        else:
            abort(404)

       

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        category_id = None
        category = None

        try:
            if body is None or 'quiz_category' not in body or 'previous_questions' not in body:
                abort(400)

            previous_questions = body['previous_questions'] if type(
                body['previous_questions']) is list else []

            if bool(body['quiz_category']):
                category_id = body['quiz_category']['id']
                category = Category.query.get(category_id)

            if category is not None:
                quize = Question.query.filter(Question.category == category_id).filter(Question.id.notin_(
                    previous_questions)).order_by(func.random()).first()
            elif category is None and len(previous_questions) < 5:
                quize = Question.query.filter(Question.id.notin_(
                    previous_questions)).order_by(func.random()).first()
            else:
                quize = None

            if quize is not None:
                quize = quize.format()

            return jsonify({
                'question': quize
            })

        except:
            print(sys.exc_info())
            abort(500)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": 'Bad Request',
                    
                }
            ), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": 'Not found',
                    
                }
            ), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": 'Unprocessable entity',
                    
                }
            ), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
        "success": False, 
        "error": 405,
        "message": "The method is not allowed for the requested URL"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server Error"}
            ),
            500,
        )

    @app.errorhandler(503)
    def service_unavailable(error):
        return (
            jsonify({"success": False, "message": "Service Unavailable", "error": 503}),
            503,
        )

    return app

