from flask import Blueprint, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from pymongo import MongoClient

from app import mongo, bcrypt
from utils import json_response
import datetime

client = MongoClient('mongodb://askquery:ABjScBh5rApoDMh4@cluster0-shard-00-00.ufe6g.mongodb.net:27017,cluster0-shard-00-01.ufe6g.mongodb.net:27017,\
cluster0-shard-00-02.ufe6g.mongodb.net:27017/askquery?ssl=true&replicaSet=atlas-c9bqn1-shard-0&authSource=admin&retryWrites=true&w=majority')

db = client.askquery

question = Blueprint('question', __name__)
question_api = Api(question)

def post_question(db, question, answer):
    db.questions.insert_one({
        'question': question,
        'answer': answer
    })
    return {'msg': 'Question Posted' }

def get_question(db):
    questions = [
        {
            'question': question['question'],
            'answer': question['answer']
        } for question in db.questions.find({})
    ]
    return questions

class Question(Resource):
    def get(self):
        resp = get_question(db)
        return json_response(resp, 200)

    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        question = request.json.get('question', None)
        answer = request.json.get('answer', None)

        if (not question) and (not answer):
            return json_response({'msg': 'Missing parameters in request.'}, 200)

        resp = post_question(db, question, answer)
        return json_response(resp, 200)

question_api.add_resource(Question, '/question')