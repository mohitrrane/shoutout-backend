from flask import Blueprint, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from pymongo import ReturnDocument

from app import mongo, bcrypt
from utils import json_response
import datetime

user = Blueprint('user', __name__)
user_api = Api(user)

class Register(Resource):
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 400)

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        name = request.json.get('name', None)
        email = request.json.get('email', None)

        if not username:
            return json_response({'msg': "Missing username parameter"}, 400)
        if not password:
            return json_response({'msg': "Missing password parameter"}, 400)
        if not name:
            return json_response({'msg': "Missing first_name parameter"}, 400)

        user = mongo.db.users.find_one({'username': username})

        if user:
            return json_response({"msg": "User already exists"}, 200) # 401
        
        mongo.db.users.insert_one({
            'username': username, 
            'password': generate_password_hash(password),
            'name': name,
            'email': email,
            'created_at': datetime.datetime.utcnow()
        })

        access_token = create_access_token(identity=username)
        return json_response({'access_token': access_token}, 200)

class Login(Resource):
    def post(self):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 400)

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return json_response({'msg': "Missing username parameter"}, 400)
        if not password:
            return json_response({'msg': "Missing password parameter"}, 400)

        user = mongo.db.users.find_one({'username': username})

        if not user:
            return json_response({"msg": "User Not Found"}, 401)
        
        if not check_password_hash(user['password'], password):
            return json_response({"msg": "Wrong password"}, 401)

        access_token = create_access_token(identity=username)
        return json_response({'access_token': access_token}, 200)


class Profile(Resource):
    @jwt_required
    def post(self, username):
        user = mongo.db.users.find_one({'username': username})
        if not user:
            return json_response({"msg": "User Not Found"}, 401)
        identity = get_jwt_identity()

        if (identity is None) or (identity != username):
            profile = {
                'username': user['username'], 
                'name': user['name']
            }
            return json_response(profile, 200)
        profile = {
            'username': user['username'],
            'name': user['name'],
            'email': user['email']
        }
        return json_response(profile, 200)

    @jwt_required
    def put(self, username):
        if not request.is_json:
            return json_response({'msg': 'Missing JSON in request.'}, 400)
        
        user = mongo.db.users.find_one({'username': username})

        if not user:
            return json_response({"msg": "User Not Found"}, 401)

        identity = get_jwt_identity()
        print(identity)
        if (identity is None) or (identity != username):
            return json_response({"msg": "Access not allowed"}, 403)

       
        name = request.json.get('name', None)
        
        if not name or name == '':
            return json_response({'msg': "No updatable parameters found"}, 403)

        updated_document = mongo.db.users\
                            .find_one_and_update(
                                {'username': username}, 
                                {'$set': {"name": name}}, 
                                return_document=ReturnDocument.AFTER
                            )
        profile = {
            'username': updated_document['username'],
            'name': updated_document['name'],
            'email': updated_document['email']
        }
        return json_response({"msg": "Profile Updated successfully", "Updated Document": profile}, 404)
        

user_api.add_resource(Login, '/login')
user_api.add_resource(Register, '/register')
user_api.add_resource(Profile, '/profile/<string:username>')