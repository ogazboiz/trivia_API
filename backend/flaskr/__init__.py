import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [rowes.format() for rowes in selection]
        current_questions = questions[start:end]

        return current_questions
PATH ='postgresql://postgres:ogazboiz@localhost:5432/trivia'

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  # setup_db(app=app, path=PATH)
  setup_db(PATH,app)
  
  '''

  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''


  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  [done]
  '''
  @app.route('/categories')
  def get_categories():
    category_query = Category.query.all()
    categories = {}
    
    for category in category_query:
        categories[category.id] = category.type

    return jsonify({ 
      "success": True,
      "categories": categories
    })



  '''
  @TODO: :
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
     
 
 

        
        # return current_questions
  @app.route('/questions')
#   def get_questions():
#     selection = Question.query.all()
#     questions = {}
     
#     for question in selection:
#       all =question.question,question.category,question.difficulty,question.answer
#       questions[question.id] = all

#     return jsonify({
#       "success": True,
#       "questions": questions
#     })
  def get_questions():
    selection = Question.query.all()
    current_question = paginate_questions(request, selection)
    all_question = Category.query.all()
    category = {question.id:question.type for question in all_question} # only this worked
    if len(current_question) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_question,
      'total_questions': len(selection),
      'categories':category,
      'current_category':None # i have no idea what you mean about that ?
    })


     

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.filter(
          Question.id == id).\
          one_or_none()

      if question is None:
        abort(404)
      
      else:
        question.delete()
        return jsonify({
          "success" : True,
          "deleted": id
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=['POST'])
  def post_question():
    body = request.get_json()
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)

    try:
      new_question =Question(question=question, answer=answer, category=category, difficulty=difficulty)
        
      new_question.insert()
      return jsonify({
        'success' :True
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_values = body.get('searchTerm')

    if search_values:
      selections = Question.query.filter(Question.question.ilike('%' + search_values + '%')).all()
    #   questions = paginate_questions(request, selections)
      formatted_questions = [question.format() for question in selections]

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(selections),
      })
    else:
      abort(400)

  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    # category = Category.query.get(id)
    # if category is None:
    #   abort(404)
    
    # selections = Question.query.filter_by(category=id).all()
    # questions = paginate_questions(request, selections)
    # formatted_questions = [question.format() for question in questions]

    # return jsonify({
    #   'success': True,
    #   'questions': formatted_questions,
    #   'total_questions': len(selections),
    #   'current_category': id
    # })
    try:
      selection = Question.query.filter(Question.category == str(id)).all()
      cats = [question.format() for question in selection]
      
      return jsonify({
        'success': True,
        'questions':cats,
        'total_questions': len(selection),
        'current_category':id
      })
    except:
      abort(404)


 
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
    body = request.get_json()
    previous_question = body['previous_questions']
    category_id = body['quiz_category']['id']
    if (not 'quiz_category' in body and not 'previous_questions' in body):
        abort(422)  
    questions = None

    if category_id:
      questions = Question.query.order_by(Question.id).all()
    else:
      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    question = None
    if len(questions) == 0:
      abort(404)
    else:
      index = len(previous_question)
      if index < len(questions):
        question = questions[index].format()
    return jsonify({
      "question" : question
    })

  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"}), 404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"}), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"}), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"}), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Sever Error"}), 500


  return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug = True)