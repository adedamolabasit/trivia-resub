from itertools import count
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORY_ALL=0

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  def paginated(request,query):
    all=[]
    page=request.args.get('page',1,type=int)
    pg=page -1
    start=int(pg *QUESTIONS_PER_PAGE)
    end=int(start * QUESTIONS_PER_PAGE)
    outcome=[qus.format() for qus in query]
    return outcome
    

  def question_shuffler(count):
        shuffle=random.sample(count,2)
        first_random_question=shuffle[0]
        second_random_question=shuffle[1]
        shuffle_list=[first_random_question,second_random_question]
        return shuffle_list

  def get_ids_from_questions(questions, previous_ids):

        questions_formatted = [q.format() for q in questions]
        current_ids = [q.get('id') for q in questions_formatted]

        ids = list(set(current_ids).difference(previous_ids))

        return ids
        
              
              
       

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
    try:

        query=Category.query.order_by(Category.id).all()
        
        return jsonify({
            'success':True,
            'categories':{
                category.id: category.type for category in query
            }
        })
    except Exception:
        abort(422)

        
    

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

    try:
            query=Question.query.order_by(Question.id).all()
            cat=Category.query.order_by(Category.id).all()
            categories={
                category.id:category.type for category in cat
            }
            

            return jsonify({
                'success':True,
                'questions':paginated(request,query),
                'categories':categories,
                'total_questions':len(paginated(request,query)),
                'current_category':None

            })
    except Exception as err:
        if '404' in err:
            abort(404)
        else:
            abort(422)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
  @app.route('/questions/<int:qus_id>',methods=['DELETE'])
  def del_question(qus_id):
    try:
        query=Question.query.get(qus_id)
        if query is None:
            abort(404)
        else:
            query.delete()
        return jsonify({
            'success':True,
            'question':query.format()

        })
    
    except Exception as err:
        if '404' in str(err):
            abort(404)
        else:
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
  @app.route('/questions',methods=['POST'])
  def create_question():

        
   

    try:
        body=request.get_json()
        
        question=body.get('question',None)
        answer=body.get('answer',None)
        category=body.get('category',None)
        difficulty=body.get('difficulty',None)
        question=Question(question=question,answer=answer,category=category,difficulty=difficulty)
        question.insert()

        query=Question.query.order_by(Question.id).all()
        
        return jsonify({
        'success':True,
        'created':query.id

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
  @app.route('/search',methods=['POST'])
  def get_search():
      
      try:
          body=request.get_json()
          search=body.get('searchTerm',None)
          query=Question.query.order_by(Question.id).filter(Question.question.ilike('%'+search+'%'))
          query_format=[question.format() for question in query]
          return jsonify({
          'success':True,
          'questions':query_format,
          'total_questions':len(paginated(request,query)),
          'current_category':None
      }) 
      except:
          abort(422)
     
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>',methods=['GET'])
  def category_qus(cat_id):
      query=Question.query.get(cat_id)
      if query is None:
                abort(404)

      try:
       
        query_cat=query.category
        questions=Question.query.order_by(Question.id).filter(Question.category==query_cat).all()


        query_question=[qus.format() for qus in questions]
        total_question=len(query_question)
        if total_question == 0:
            abort(404)
        return jsonify({
            'success':True,
            'questions':query_question,
            'total_questions':total_question,
            'current_category':cat_id
        })
      except Exception as err:
        if '404' in err:
            abort(404)
        else:
            abort(422)

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
  def retrieve_quizzes():
    
        try:
            # Get raw data
            questions = None
            body = request.get_json()
            quiz_category = body.get('quiz_category', None)
            previous_ids = body.get('previous_questions', None)
            category_id = quiz_category.get('id')

            # Check category
            if category_id == CATEGORY_ALL:
                # Get all the questions
                questions = Question.query.all()
            else:
                # Get the questions by the requested category
                questions = Question.query \
                    .filter(Question.category == category_id) \
                    .all()

            # Get the list of ids
            ids = get_ids_from_questions(questions, previous_ids)

            if len(ids) == 0:
                # If the list is empty return no question
                return jsonify({
                    'success': True,
                    'question': None
                })
            else:
                # Choice a random id
                random_id = random.choice(ids)

                # Get the question
                question = Question.query.get(random_id)

                return jsonify({
                    'success': True,
                    'question': question.format()
                })

        except Exception:
            abort(422)



 

        
        
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

  @app.errorhandler(500)
  def internal_server_error(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

  return app
 


















    