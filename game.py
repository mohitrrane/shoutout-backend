from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from utils import json_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from game_class import *
from pymongo import MongoClient

client = MongoClient('mongodb://askquery:ABjScBh5rApoDMh4@cluster0-shard-00-00.ufe6g.mongodb.net:27017,cluster0-shard-00-01.ufe6g.mongodb.net:27017,\
    cluster0-shard-00-02.ufe6g.mongodb.net:27017/askquery?ssl=true&replicaSet=atlas-c9bqn1-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client.askquery

game = Blueprint('game', __name__)
game_api = Api(game)

class StartGame(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_type = request.json.get('game_type', None)
        n_questions = request.json.get('n_questions', None)

        if (not game_type) and (not n_questions):
            return json_response({'msg': 'Missing parameters in request.'}, 200)

        if game_type == 'mining_the_answers':
            resp = start_game(db, identity, n_questions)
            
            # Issuing Double verification token here

            return json_response(resp, 200)
        
        return json_response({'msg': 'Something went wrong'}, 200)

class JoinGame(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing game key in request.'}, 200)
       
        resp = join_game(db, identity, game_key)
                
        # Issuing Double Verification Token Here

        return json_response(resp, 200)

class EnterGame(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing game key in request.'}, 200)
        
        # Double Verification Here

        resp = enter_game(db, game_key)
        return json_response(resp, 200)

class GetAllStates(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing game key in request.'}, 200)
        
        # Double Verification Here
        
        resp = get_all_states(db, identity, game_key)
        return json_response(resp, 200)

class GetQuestion(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)
        qn_num = request.json.get('qn_num', None)

        if (not game_key) and (not qn_num):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = get_question(db, game_key, qn_num)
        return json_response(resp, 200)

class SubmitAnswer(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)
        qn_num = request.json.get('qn_num', None)
        answer = request.json.get('answer', None)
        
        if (not game_key) and (not qn_num):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        answer = {
            'qn_num': qn_num,
            'answer': answer
        }
        resp = submit_answer(db, identity, game_key, answer)
        return json_response(resp, 200)

class GetAnswers(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)
        qn_num = request.json.get('qn_num', None)

        if (not game_key) and (not qn_num):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = get_answers(db, game_key, qn_num)
        return json_response(resp, 200)

class SubmitSelection(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)
        qn_num = request.json.get('qn_num', None)
        answer = request.json.get('answer', None)

        if (not game_key) and (not qn_num):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        selection = {
            'qn_num': qn_num,
            'answer': answer
        }
        resp = submit_selection(db, identity, game_key, selection)
        return json_response(resp, 200)

class GetMidResult(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)
        qn_num = request.json.get('qn_num', None)

        if (not game_key) and (not qn_num):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = get_midresult(db, game_key, qn_num)
        return json_response(resp, 200)

class GetEndResult(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = get_endresult(db, game_key)
        return json_response(resp, 200)

class BeReady(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = be_ready(db, game_key, identity)
        return json_response(resp, 200)

class EndGame(Resource):
    @jwt_required
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 200) #400

        identity = get_jwt_identity()

        if not identity:
            return json_response({'msg': 'Token not valid.'}, 200)

        game_key = request.json.get('game_key', None)

        if (not game_key):
            return json_response({'msg': 'Missing parameters in request.'}, 200)
        
        # Double Verification Here

        resp = end_game(db, game_key)
        return json_response(resp, 200)

game_api.add_resource(StartGame, '/start_game')
game_api.add_resource(JoinGame, '/join_game')
game_api.add_resource(EnterGame, '/enter_game')
game_api.add_resource(GetAllStates, '/get_all_states')
game_api.add_resource(GetQuestion, '/get_question')
game_api.add_resource(SubmitAnswer, '/submit_answer')
game_api.add_resource(GetAnswers, '/get_answers')
game_api.add_resource(SubmitSelection, '/submit_selection')
game_api.add_resource(GetMidResult, '/get_midresult')
game_api.add_resource(GetEndResult, '/get_endresult')
game_api.add_resource(BeReady, '/be_ready')
game_api.add_resource(EndGame, '/end_game')