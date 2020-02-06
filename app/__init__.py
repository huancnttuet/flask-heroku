# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restplus import Api, Resource, fields

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/flask_test'
    db.init_app(app)
    migrate = Migrate(app, db)
    from app import models
    with app.app_context():
        db.create_all()

    api = Api(app, version='1.0', title='TodoMVC API',
              description='A simple TodoMVC API',
              )

    ns = api.namespace('todos', description='TODO operations')

    todo = api.model('Todo', {
        'id': fields.Integer(readonly=True, description='The task unique identifier'),
        'task': fields.String(required=True, description='The task details')
    })

    from .models import Task

    class TodoDAO(object):
        def __init__(self):
            self.counter = 0
            self.todos = []

        def get(self, id):
            for todo in self.todos:
                if todo['id'] == id:
                    return todo
            api.abort(404, "Todo {} doesn't exist".format(id))

        def create(self, data):
            todo = data
            todo['id'] = self.counter = self.counter + 1
            self.todos.append(todo)
            print(data['task'])
            with app.app_context():
                newTask = Task(task=data['task'])
                db.session.add(newTask)
                db.session.commit()
            return todo

        def update(self, id, data):
            todo = self.get(id)
            todo.update(data)
            return todo

        def delete(self, id):
            todo = self.get(id)
            self.todos.remove(todo)

    DAO = TodoDAO()
    DAO.create({'task': 'Build an API'})
    DAO.create({'task': '?????'})
    DAO.create({'task': 'profit!'})

    @ns.route('/')
    class TodoList(Resource):
        '''Shows a list of all todos, and lets you POST to add new tasks'''
        @ns.doc('list_todos')
        @ns.marshal_list_with(todo)
        def get(self):
            '''List all tasks'''
            return DAO.todos

        @ns.doc('create_todo')
        @ns.expect(todo)
        @ns.marshal_with(todo, code=201)
        def post(self):
            '''Create a new task'''
            return DAO.create(api.payload), 201

    @ns.route('/<int:id>')
    @ns.response(404, 'Todo not found')
    @ns.param('id', 'The task identifier')
    class Todo(Resource):
        '''Show a single todo item and lets you delete them'''
        @ns.doc('get_todo')
        @ns.marshal_with(todo)
        def get(self, id):
            '''Fetch a given resource'''
            return DAO.get(id)

        @ns.doc('delete_todo')
        @ns.response(204, 'Todo deleted')
        def delete(self, id):
            '''Delete a task given its identifier'''
            DAO.delete(id)
            return '', 204

        @ns.expect(todo)
        @ns.marshal_with(todo)
        def put(self, id):
            '''Update a task given its identifier'''
            return DAO.update(id, api.payload)

# temporary route
    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    return app
