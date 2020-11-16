# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints:
GET '/'
GET '/questions'
DELETE '/questions/<int:id>'
POST '/questions', methods=["POST"]
GET '/categories/<int:id>/questions'
GET '/quizzes', methods=["POST"]

GET '/'
 - Home Route, Landing Page
Sample: curl http://127.0.0.1:5000/
{
    "success": true
}

GET '/categories'
 - gets a list of categories
Returns: a list of categories
Sample Response:
{
    "categories": {
        "id": 6,
        "type": "Sports"
    },
    "current_category": null,
    "success": true
}

GET '/questions'
 - gets questions
Returns: 
 - a pagined list of questions
 - number of total questions
 - the current category
 - categories
Sample Response:
{
    "categories": [
        {
            "id": 1,
            "type": "Science"
        },...],
    "current_category": null,
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        }...
    ]
}

DELETE '/questions/<int:id>'
 - Deletes a question by id using url params
Returns: the id of deleted question upon success
Sample Response:
{
    "deleted": 4, 
    "success": true
}

POST '/questions', methods=["POST"]
 - Creates an endpoint to:
1) POST a new question
2) POST endpoint to get questions based on a search term
Returns:
 - the question and answer text
 - category
 - difficulty score
 - any questions for which the search term is a substring of the question
Sample Response:
{
      "created": 54, 
      "question_created": "In which U.S. National Park can you find El Capitan?", 
      "questions": [
          {
              "answer": "George Washington Carver", 
              "category": 4, 
              "difficulty": 2, 
              "id": 12, 
              "question": "Who invented Peanut Butter?"
          },...

GET '/categories/<int:id>/questions'
- get questions based on category
Returns: a question based on a category
Sample Response:
{
    "current_category": 5,
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 6,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        }
    ],
    "success": true,
    "total_questions": 2
}

GET '/quizzes', methods=["POST"]
 - get questions to play the quiz
Returns: a random questions within the given category, that is not one of the previous questions.
Sample Response:
{
    "question": {
        "answer": "Scarab", 
        "category": 4, 
        "difficulty": 4, 
        "id": 23, 
        "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    },
    "success": true
  }

Error Handling:
The API returns Error messages in the following format:
{
    "success": False,
    "error": 404,
    "message": "Resource not found"
}
The API will return four (4) types of errors:
    400 – bad request
    404 – resource not found
    422 – unprocessable
    500 - bad response

```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```