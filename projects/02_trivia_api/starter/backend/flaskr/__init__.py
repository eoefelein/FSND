import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    @TODO: Set up CORS.
    Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # additional parameter, resources, is passed - obj within which
    # keys are URI for given resource (here '/api')
    # and values map to specified origins that have access to that resource
    cors = CORS(
        app,
        resources={r"/api*": {"origins": "*"}}
    )  # resource-specific usage

    @app.after_request
    def after_request(response):
        # CORS Headers
        # allowing for content-type authorization
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        # specifying response headers so as to allow for different methods
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS"
        )
        return response

    # when request is passed in as a param here,
    # we can use args associated with request to get the page num
    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        # so start & end correspond to ids of each book returned to the page
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [q.format() for q in selection]
        current_qs = questions[start:end]
        return current_qs

    # helper function to get categories
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        categories = [c.format() for c in categories]
        categories = {k: v for d in categories for k, v in d.items()}
        return categories

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/")
    def home():
        return jsonify({"success": True})

    # for specific routes & endpoints for which we want to allow CORS,
    # we can use @cross_origin, prior to the handling of that route,
    # in order to enable CORS specifically for that endpoint
    @app.route("/categories")
    # @cross_origin()  # route-specific usage
    def get_those_categories():
        categories = get_categories()
        return jsonify(
            {
                "success": True,
                "categories": categories,
                "current_category": None,
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
    ten questions per page
    and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    # starting with the get request is a nice way to get acccess to the DB,
    # and start to see things working.
    # following endpoint rules, we set up endpoints based on collections,
    # in this case, collections of questions
    @app.route("/questions")
    def get_questions():
        # use the Question, imported from models.py, to get all Question objs
        # and format with the method defined
        ordered_questions = Question.query.order_by(Question.id).all()
        questions = paginate_questions(request, ordered_questions)
        if len(questions) == 0:
            abort(404)
        all_cat = list(map(Category.format, Category.query.all()))
        output = {
            "success": True,
            "questions": questions,
            "total_questions": len(ordered_questions),
            "current_category": None,
            "categories": all_cat,
        }
        return jsonify(output)

    """
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  """

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        body = request.get_json()
        try:
            # first thing TODO is to make sure question exists...
            # if question doesn't exist:
            question = Question.query.filter_by(id == id).one_or_none()
            # one_or none() sqlalchemy method returns:
            # 1) at most one result or 2) raises an exception,
            # so if multiple objects are returned,
            # raises sqlalchemy.orm.exc.MultipleResultsFound

            if question is None:  # if question doesn't exist
                abort(
                    404
                )  # indicates the question doesn't exist & can't be deleted

            # otherwise, delete the question:
            question.delete()
            # find selection of ordered questions...
            selection = Question.query.order_by(Question.id).all()
            # ... & paginate based on our current location within the selection
            current_question = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question.id,
                    # current_questions on pg we're on currently
                    "questions": current_question,
                    "total_questions": len(
                        Question.query.all()
                    ),  # total questions kept paginated/updated
                }
            )
        except unprocessable:
            abort(422)
            # should issue arise in deleting the question, abort

    """
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  """

    """
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  """

    @app.route("/questions", methods=["POST"])
    def post_question():
        # load the request body
        body = request.get_json()

        # get search_term from user
        if body.get("searchTerm"):
            search_term = body.get("searchTerm")

            # query the database using the search term,
            # use ilike for pattern matching with Postgres SQL
            selection = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()

            if len(selection) == 0:
                abort(404)

            paginated = paginate_questions(request, selection)

            # return results
            return jsonify(
                {
                    "success": True,
                    "questions": paginated,
                    "total_questions": len(Question.query.all()),
                }
            )
        else:
            # should the question not exist, create it!
            # # load data from body and store to variables
            new_question = body.get("question")
            new_answer = body.get("answer")
            new_category = body.get("category")
            new_difficulty = body.get("difficulty")
            # ensure all data fields are populated
            # could also use ??? - or are db's set up separately?
            # db.session.add(todo_list)
            # db.session.commit()
            # body['id'] = todo_list.id
            # body['name'] = todo_list.name
            if (
                (new_question is None)
                or (new_answer is None)
                or (new_difficulty is None)
                or (new_category is None)
            ):
                abort(422)
            try:
                # create and insert new question
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category,
                )

                # insert question
                question.insert()

                # get all questions and paginate
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                # paginate the results
                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "question_created": question.question,
                        "questions": current_questions,
                        "questions": paginated,
                        "total_questions": len(Question.query.all()),
                    }
                )
            except unprocessable:
                abort(422)
                # abort unprocessable if exception

    """
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  """

    @app.route("/categories/<int:id>/questions")
    def get_questions_by_category(id):
        category = Question.query.filter_by(id == id).one_or_none()

        # abort 404 if category is not found
        if category is None:
            abort(404)

        # get the matching questions
        selection = Question.query.filter_by(category == category.id).all()

        # paginate the selection...
        # why would you need to paginate if using one_or_none method
        paginated = paginate_questions(request, selection)

        # return the results
        return jsonify(
            {
                "success": True,
                "questions": paginated,
                # is type being pulled from paginate helper function?
                "category": category.type,
                "total_questions": len(Question.query.all()),
            }
        )

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

    @app.route("/quizzes", methods=["POST"])
    def play_the_quiz_game():
        category = Question.query.filter_by(id == id).one_or_none()

        if category is None:
            abort(404)

        selection = Question.query.filter_by(category == category.id)

        # get the previous questions - this is defined on the front-end
        previous_questions = body.get("previous_questions")
        # get the category - this is defined on the front-end
        category = body.get("quiz_category")

        if (category is None) or (previous_questions is None):
            abort(404)

        # if ALL is selected, load all questions, otherwise...
        if category["id"] == 0:
            questions = Question.query.all()
        # load questions for only the category specified
        else:
            questions = Question
            .query
            .filter_by(category == category["id"])
            .all()

        # get total num of questions
        total = len(questions)

        # picks a random question
        def generate_random_question():
            return questions[random.randrange(0, len(questions))]

        # get random question
        question = generate_random_question()

        # check to see if question has already been used
        def check_if_used(question):
            used = False
            for question in previous_questions:
                if question == question.id:
                    used = True
            return used

        # continue generating questions until:
        # used question condition = False
        while check_if_used(question):
            question = generate_random_question()

            # if unable to find unused question,
            # return no question
            if len(previous_questions) == total:
                return jsonify({
                    "success": True,
                    "message": "Sorry, all questions have been used!"
                    })

        # else, return the question
        return jsonify({"success": True, "question": question.format()})

    """
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  """

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                "success": True,
                "error": 400,
                "message": "Bad request"
                }),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "Resource not found"
                }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": True,
                "error": 422,
                "message": "Request is unprocessable"
                }),
            422,
        )

    @app.errorhandler(500)
    def bad_response(error):
        return (
            jsonify({
                "success": True,
                "error": 500,
                "message": "Bad response"
                }),
            500,
        )

    return app


'\n'