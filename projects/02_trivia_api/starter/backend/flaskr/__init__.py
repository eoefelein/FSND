import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# when request is passed in as a param here,
# we can use args associated with request to get the page num
def paginate_books(request, selection):
    page = request.args.get("page", 1, type=int)
    # so start and end correspond to the ids of each ind book being returned to the page
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
    cors = CORS(app, resources={r"/api*": {origin: "*"}})  # resource-specific usage
    # additional parameter, resources, is passed - obj within which
    # keys are URI for given resource (here '/api')
    # and values map to specified origins that have access to that resource

    """
  @TODO: Use the after_request decorator to set Access-Control-Allow
  """
    # Flask decorator, which serves to add headers to the response
    # this method will take the response as a parameter, make some edits to it and return it

    @app.after_request(response)
    def after_request(response):
        # CORS Headers
        # allowing for content-type authorization
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        # specifying response headers so as to allow for different methods
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, OPTIONS"
        )
        return response

    """
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  """

    # for specific routes and endpoints for which we'd want to allow cross-origin resource sharing,
    # we can implement the @cross_origin decorator, prior to the handling of that route,
    # in order to enable CORS specifically for that endpoint
    @app.route("/categories")
    @cross_origin()  # route-specific usage
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # abort 404 if no categories found
        if (len(categories_dict) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'categories': categories_dict
        })

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
    # starting with the get request is a nice way to get acccess to the DB,
    # and start to see things working
    # following endpoint rules, we want to set up endpoints based on collections,
    # in this case, collections of questions
    @app.route("/questions")
    def get_questions():
        # use the Question, imported from models.py, to get all Question objs
        # and format with the method defined
        questions = Questions.query.all()
        formatted_questions = [question.format() for question in questions]
        # JSON response body obj returned to the user, all questions can be returned here
        return jsonify({"success": True, "questions": formatted_questions})

    # # my attempt and the on I ask the question for with Udacity's Mentor Help
    # @app.route("/questions")
    # def get_questions():
    #     # load the request body
    #     body = request.get_json()
    #     # if search_term exists...
    #     if body.get("search_term"):
    #         # get search_term from user
    #         search_term = body.get("search_term")
    #         # query the database using the search term
    #     selection = Question.query.filter(
    #         Question.question.ilike(f"%{search_term}%")
    #     ).all()
    #     # if len(selection)==0), then the question with the "searchTerm" doesn't exist in the db
    #     # and so a 404(not found) error is raised. How would you address this depends on the proj.
    #     # For this project, we want to show that the question was not found
    #     # and add that question to the db
    #     if len(selection) == 0:
    #         abort(404)
    #     paginated = request.args.get("paginated")
    #     question = Question(question=question)
    #     if exists:
    #         return question.jsonify({"success": True, "question": question})

    """
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        body = request.get_json()
        try:
            # first thing to do is to make sure that question exists...if question doesn't exist
            question = Question.query.filter_by(id == id).one_or_none()
            # one_or none() sqlalchemy method returns at most one result or raises an exception,
            # so if multiple objects are returned, raises sqlalchemy.orm.exc.MultipleResultsFound

            if question is None:  # if question doesn't exist
                abort(
                    404
                )  # which indicates that the question doesn't exist and cannot be deleted

            # otherwise, delete the question:
            question.delete()
            # find selection of ordered questions...
            selection = Question.query.order_by(Question.id).all()
            # ... and paginate based on our current location within that selection
            current_question = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question.id,
                    "questions": current_question,  # current_questions on the page we're currently on
                    "total_questions": len(
                        Question.query.all()
                    ),  # total questions front-end can keep pageined/updated
                }
            )
        except:
            # should issue arise in deleting the question, abort
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

            # query the database using the search term, use ilike for pattern matching with Postgres SQL
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
            except:
                # abort unpreocessable if exception
                abort(422)

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

        # paginate the selection - why would you need to paginate if using one_or_none method
        paginated = paginate_questions(request, selection)

        # return the results
        return jsonify(
            {
                "success": True,
                "questions": paginated,
                "category": category.type,  # is type being pulled from paginate helper function?
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
            questions = Question.query.filter_by(category == category["id"]).all()

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

        # continue generating questions until question makes used condition is False
        while check_if_used(question):
            question = generate_random_question()

            # if unable to find unused question, return no question
            if len(previous_questions) == total:
                return jsonify(
                    {"success": True, "message": "Sorry, all questions have been used!"}
                )

        # else, return the question
        return jsonify({"success": True, "question": question.format()})

    """
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": True, "error": 422, "message": "Request is unprocessable"}
            ),
            422,
        )

    return app
