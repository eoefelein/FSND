import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # sample question to be used for test purposes
        self.new_question = {
            'question': 'How many National Parks are part of the U.S. National Park System?',
            'answer': 'There are 400 unique National Parks sites existing in the U.S. in 2020.',
            'difficulty': '9'
            'category': '1'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # tests that questions are paginated appropriately
    def test_pagination(self):
        # what are the two other ways of getting the response?
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code
        self.assertEqual(responses.status_code, 200)
        # check success message
        self.assertEqual(data['success'], True)

        # check that total_questions returns data
        self.assertTrue(data['total_questions'])
        # check that questions returns data
        self.assertTrue(len(data['questions']))
    
    # tests 404 response should information be requested beyond valid page range
    def test_response_to_request_beyond_valid_page(self):
        # send request with bad page data
        response = self.client().get('/questions?page=100')
        # load response
        data = json.loads(response.data)

        #check status_code
        self.assertEqual(response.status_code, 404)
        # check failure message
        self.assertEqual(data['success'], False)
        # check that message returned is explanatory
        self.assertEqual(data['message'], 'resource not found')

    # tests that questions deletion functionality works as expected
    def test_deletion(self):
        # create a new question to be deleted
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
        category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        # get the id of the question we just created
        question_id = question.id

        # in order to understand that a question is deleted correctly,
        # create two (2) variables, which capture the num of questions 
        # that exist before and after the deletion of a question
        num_questions_before = Question.query.all()
        # delete the question - corresponds to line 223 in __init__.py
        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)
        num_questions_after = Question.query.all()

        # use the question id, captured and stored in question_id variable,
        # to verify that question has been deleted
        # why would id need to equal 1? wouldn't we want to check the len here?
        question = Question.query.filter(Question.id == 1).one_or_none()

        # check status code
        self.assertEqual(response.status_code, 200)
        # check success message
        self.assertEqual(data['success'], True)
        # check that question_id matched id of question deleted
        self.assertEqual(data['deleted'], question_id)
        # check that difference between num_questions_before & num_questions_after is 1,
        # i.e., we have one less question
        self.asserEqual(len(num_questions_before) - len(num_questions_after) == 1)
        # check that question equals None after delete
        self.assertEqual(question, None)

    # tests that questions creation functionality works as expected
    def test_creation(self):
        # in order to understand that a question is created correctly,
        # create two (2) variables, which capture the num of questions 
        # that exist before and after the creation of a question
        num_questions_before = Question.query.all()
        # create new question - corresponds to line 223 in __init__.py
        response = self.client().post('/questions'. json=self.new_question)
        data = json.loads(response.data)
        num_questions_after = Question.query.all()

        # check that question has been created
        question = Question.query.filter_by(id=data['created']).one_or_none()

        # check status code
        self.assertEqual(response.status_code, 200)
        # check success message
        self.assertEqual(data['success'], True)
        # check that difference between num_questions_after and num_questions_before is 1,
        # i.e., we have one more question
        self.assertTrue(len(num_questions_after) - len(num_questions_before) == 1)
        # check that question does not equal None after creation
        self.assertIsNotNone(question)
    
    # tests 422 response should question creation fail
    def test_response_should_question_creation_fail(self):
        # in order to capture the num of questions before and after 
        # the creation of test question, create two (2) variables 
        # in which to store these values
        num_questions_before = Question.query.all()
        # create new question - corresponds to line 223 in __init__.py
        response = self.client().post('/questions'. json=self.new_question)
        data = json.loads(response.data)
        num_questions_after = Question.query.all()

        # check status code
        self.assertEqual(response.status_code, 422)
        #check success message
        self.assertEqual(data['success'], False)
        # check that num_questions_before & num_questions_after are equal
        self.assertTrue(len(num_questions_after) == len(num_questions_before))

    # tests that search question functionality works as expected
    def test_search(self):
        #send post request with search term
        response = self.client().post('/questions', json={'searchTerm': 'Organ'})
        # load response data
        data = json.loads(response.data)

        # check response status code
        self.assertEqual(response.status_code, 200)
        # check success message
        self.assertEqual(data['success'], True)
        # check that num of results is 1
        self.assertEqual(len(data['questions'], 1)

    # tests 404 response should question search fail
    def test_response_should_question_search_fail(self):
        # send post request with search term that will fail
        response = self.client().post('/questions', json={'searchTerm': '12345'})
        # load response data
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 404)
        # check failure message
        self.assertEqual(data['success'], False)
        # check that message returned is explanatory
        self.assertEqual(data['message'], 'resource not found')

    # tests get functionality of questions by category works as expected
    def test_get_questions_by_category(self):
        # send request with category id 5 for outdoors
        response = self.client().get('/categories/5/questions')
        # load response data
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        # check success message
        self.assertEqual(data['success']. True)
        # check that questions are returned, i.e. len of data['questions'] > 0
        self.assertNotEqual(len(data['questions']), 0)
        # check that category returned is outdoors
        self.assertEqual(data['current_category'], 'Outdoors')

    # tests 404 response should get functionality of questions by category fail
    def test_response_should_get_question_category_fail(self):
        # send request with invalid category id
        response = self.client().get('categories/250/questions')
        # load response data
        json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 404)
        # check failure message
        self.assertEqual(data['success'], False)
        # check that message returned is explanatory
        self.assertEqual(data['message'], 'resource not found')

    # test functionality of playing the quiz game itself
    def test_play_the_quiz_game(self):
        response = self.client().post('/quizzes', json={'previous_questions': [7,8], 
        'quiz_category': {'type': 'Outdoors', 'id': '1'}})
        # load response data
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 200)
        # check message
        self.assertEqual(data['success'], True)
        # check that a question is returned
        self.assertTrue(data['question'])
        # check that the question returned is in correct category
        self.assertEqual(data['question']['category'], 5)
        # check that question returned is not on previous question list
        self.assertNotEqual(data['question']['id'], 7)
        self.assertNotEqual(data['question']['id'], 8)

    # tests 404 response should quiz game not work as expected
    def test_play_the_quiz_game(self):
        # send post request without json data
        response = self.client().post('/quizzes', json={})
        # load response data
        data = json.loads(response.data)

        # check status code
        self.assertEqual(response.status_code, 404)
        # check message
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()