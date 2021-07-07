from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config['FLASK_APP'] = 'app' 
app.config['MONGO_URI'] = 'mongodb://askquery:sq83lTvQa0oHZCAI@cluster0-shard-00-00.ufe6g.mongodb.net:27017,cluster0-shard-00-01.ufe6g.mongodb.net:27017,cluster0-shard-00-02.ufe6g.mongodb.net:27017/askquery?ssl=true&replicaSet=atlas-c9bqn1-shard-0&authSource=admin&retryWrites=true&w=majority'
app.config['JWT_SECRET_KEY'] = 'drftgyhtghbjnkmghbnfytuygb'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/')
def index():
    mongo.db.user_details.insert_one({'name':'test'})
    return """
        rtgbhnjkml
        xdcfgvhbjnk
        dcfvgbhnjk
        xdcfvghbjk 
        fvgbhnjk
    """

if __name__ == '__main__':
    from user import user_api
    from game import game_api
    from question import question_api

    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(game_api.blueprint)
    app.register_blueprint(question_api.blueprint)
    app.run(debug=True)