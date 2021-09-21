from itertools import count
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
  
  def paginated(request,query):
        page=request.args.get('page',1,type=int)
        start=(page-1)*QUESTIONS_PER_PAGE
        end=start * QUESTIONS_PER_PAGE
        outcome=[qus.format() for qus in query]
        outcome[start:end]
        return outcome

  def question_shuffler(count):
        shuffle=random.sample(count,2)
        first_random_question=shuffle[0]
        second_random_question=shuffle[1]
        shuffle_list=[first_random_question,second_random_question]
        return shuffle_list

      
        
              
              
       

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  



  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_category():
    query=Category.query.all()
    category=[cat.format() for cat in query]
    return jsonify({
        'success':True,
        'categories':category
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def get_questions():
    query=Question.query.order_by(Question.id).all()
    cat=Category.query.all()
    categories=[ obj.format() for obj in cat ]
    

    return jsonify({
        'success':True,
        'question':paginated(request,query),
        'categories':categories,
        'number of total questions':len(paginated(request,query))
        

    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
  @app.route('/questions/<int:qus_id>',methods=['DELETE'])
  def del_question(qus_id):
      query=Question.query.get(qus_id)
      if query == None:
          abort(404)
      else:
          query.delete()
      return jsonify({
          'success':True,
          'question':query.format()

      })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():
      body=request.get_json()

      try:
          question_body=body.get('question',None)
          answer_body=body.get('answer',None)
          category_body=body.get('category',None)
          difficulty_body=body.get('difficulty',None)
          question=Question(question=question_body,answer=answer_body,category=category_body,difficulty=difficulty_body)
          question.insert()

          query=Question.query.order_by(Question.id).all()
          question_submition=paginated(request,query)


      except:
          abort(422)
      return jsonify({
          'success':True,
          'question_submition':question_submition

      })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions',methods=['POST'])
  def get_search():
      try:
          search=request.args.get('search')
          query=Question.query.filter(Question.question.contains('%'+search+'%'))
      except:
          abort(402)
      return jsonify({
          'success':True,
          'search question':paginated(request,query)
      })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions',methods=['GET'])
  def category_qus(cat_id):
    query=Question.query.get(id=cat_id)
    query_cat=query.category
    questions=Question.query.filter_by(Category=query_cat)
    query_question=[qus.format() for qus in questions]

    return jsonify({
        'success':True,
        'questions':query_question

    })

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

  @app.route('/quizzes',methods=['POST'])
  def quizs():
        
      count=[]
      body=request.get_json()
      try:
        query_cat=request.args.get('category')
        answer_body=body.get('answer',None)
        category_body=body.get('category',None)
        difficulty_body=body.get('difficulty',None)
        id_body=body.get('id',None)
        question_body=body.get('question',None)
        previous_qus_parameters=Question(answer=answer_body,category=category_body
        ,difficulty=difficulty_body,id=id_body,question=question_body)
        previous_qus_parameters.insert()
        cat_query=Question.query.filter_by(category=query_cat)
        cat_list=[cat.id for cat in cat_query]
        count.append(cat_list)
        random_qus_id=question_shuffler(count)
        first_random_question=random_qus_id[0]
        second_random_question=random_qus_id[1]

        query_random=Question.query.get(id=first_random_question)
        if id_body == first_random_question:
              random_question=Question.query.get(id=second_random_question)
        elif id_body != query_random:
              random_question=Question.query.get(id=first_random_question)
      except:
        abort(404)
      return jsonify({
        'category':query_cat,
        'previous_question':previous_qus_parameters,
        'new generated_question':random_question
        
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
          "message": "Not found"
          }), 404


  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "unprocessable"
      }),422



  return app
 


















    