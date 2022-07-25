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
        self.database_path = "postgresql://{}@{}/{}".format('niffy', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.newQuestion = {
            'question': 'What is the diameter of a basketball hoop in inches?',
            'answer': '18 inches',
            'difficulty': 4,
            'category': 6
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

    def test_get_categories(self):
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['categories']['1'])

    def test_delete_all_categories(self):
        res = self.client().delete('/api/v1.0/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)

   
    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertIn('categories', data)
        self.assertTrue(data['categories']['1'])
        self.assertIn('currentCategory', data)
        self.assertTrue(data['currentCategory'])

    def test_404_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_add_question(self):
        
        res = self.client().post('/questions', json=self.newQuestion)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_questions_in_category(self):
        res = self.client().get('/api/v1.0/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_404_questions_by_category_not_exists(self):
        res = self.client().get('/api/v1.0/categories/b/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/29')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions(self):
        res = self.client().post('/questions', json={"searchTerm": "question"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertTrue(data['totalQuestions'])
        self.assertIn('currentCategory', data)

    def test_404_search_question(self):
        new_search = {
            'searchTerm': 'zbvxhsjusy',
        }
        res = self.client().post('/questions', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)
        self.assertIn('totalQuestions', data)
        self.assertFalse(data['totalQuestions'])

    def test_get_random_quiz(self):
        response = self.client().post(
            "/quizzes",
            json={
                "previous_questions": [6, 9, 10],
                "quiz_category": {"id": "3", "type": "Geography"},
            },
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], "3")

    def test_422_get_quiz(self):
        res = self.client().post("/quizzes", json={"previous_questions": []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable entity")




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()