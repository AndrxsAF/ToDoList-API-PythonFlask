"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/todo', methods=['GET'])
def show_todos():
    todos = Todo.query.all()
    return jsonify(list(map(lambda tasks: tasks.serialize(), todos))), 200
    
@app.route('/todo/add', methods=['POST'])
def add_todos():
    body = request.get_json()
    new_todo = Todo(task=body["task"], status=False)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.serialize()), 200

@app.route('/todo/<id>', methods=['GET', 'DELETE'])
def delete_todos(id):
    todo = Todo.query.get(id)
    if todo:
        if request.method == "GET":
            return jsonify(todo.serialize())
        elif request.method == "DELETE":
            db.session.delete(todo)
            db.session.commit()
            return jsonify('Tarea eliminada con exito.')
    else:
        return jsonify('No existe esa función')

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
