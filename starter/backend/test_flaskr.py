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

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.get_category = {
            'type':'personal'
            
        }
        self.new_question = {
            'id':15,
            'question':'what is trivia',
            'answer':"i don't know",
            'category':'unknow question',
            'difficulty':2
        }


    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_category(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['categories']),5)
        self.assertIsInstance(data['categories'],list)
    
    def test_get_question(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # Questions
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)

        # Total questions
        self.assertEqual(data['total_questions'], 10)

        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 5)
        self.assertIsInstance(data['categories'], dict)

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_create_question(self):
        """
        CREATE question
        """
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 15)

    def test_delete_question(self):
        
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)

    def test_404_send_not_valid_id_for_delete_question(self):
          
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_search_questions(self):
        """
        Search questions with results
        """
        res = self.client().post(
            '/search',
            json={'searchTerm': 'how are you'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], None)






    def test_get_questions_by_category(self):
        """
        Get questions by category
        """
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)


    def test_404_send_category_without_questions(self):
         
        res = self.client().get('/categories/15/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    def test_quizzes_without_category_and_without_previous_questions(self):
        
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '0',
                'type': 'All'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], dict)

    def test_quizzes_with_category_and_without_previous_questions(self):
        """
        Test quizzes without previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def test_quizzes_with_category_and_with_some_previous_questions(self):
        """
        Test quizzes with some previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14],
            'quiz_category': {
                'id': '2',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def test_quizzes_with_category_and_with_all_the_previous_questions(self):
        """
        Test quizzes with all the previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14, 15],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()