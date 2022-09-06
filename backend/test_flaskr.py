from gettext import find
import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.path = 'postgresql://postgres:ogazboiz@localhost:5432/trivia'
        self.new_question = {
            'question': 'New question',
            'answer': 'New answer',
            'difficulty': 1,
            'category': '1'
        }
        setup_db(self.path, self.app)
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
    [done]
    """

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])
    
    def test_get_paginated_books(self):
        res = self.client.get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        

    def test_404_requesting_beyond_available_page(self):
        response = self.client.get("/questions?page=100000")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_select_category(self):
        response = self.client.get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
    def test_select_category_error(self):
        response = self.client.get('/categories/category/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')


    def test_search_question(self):
        find = {'searchTerm': 'a'}
        response = self.client.post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_400_search_question_searchterm_empty(self):
        find = {'searchTerm': ''}
        response = self.client.post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')
    
    def test_book_search_without_results(self):
        find = {'searchTerm': 'm4jrimfkrjnfr'}
        response = self.client.post('/questions/search', json=find)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions']==0, True)
        self.assertIsNotNone((data['questions']))
    
    def test_delete_question(self):
        
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        question_id = question.id
        previous_question = Question.query.all()

        response = self.client.delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)
        next_question = Question.query.all()
        question = Question.query.filter(Question.id == 1).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(len(previous_question) - len(next_question) == 1)
        self.assertEqual(question, None)

    def test_play_quiz_game(self):
        response = self.client.post('/quizzes', json={
            "quiz_category": {
                "type": "Science",
                "id": "1"
            },
            "previous_questions": []
        }) 
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']['category']))

    def test_play_quiz_fails(self):
        response = self.client.post('/quizzes') 

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

        
if __name__ == "__main__":
    unittest.main()