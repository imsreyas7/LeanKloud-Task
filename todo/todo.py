from flask import Flask, render_template
from flask import Blueprint, request
from flask.templating import render_template
from flask_restplus import Api, Resource, fields
import mysql.connector
import datetime
from functools import wraps

#Database Used: MySQL
#Due By, Overdue and Finished options added
#Authorization for WRITE added

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Sre#123",
  database="sonoo"
)

authorizations =  {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'WRITE-API-KEY'
    }
}


api_main = Flask(__name__)
api = Api(api_main, version='3.0', title='LeanKloud TodoMVC API',
    description='A simple TodoMVC API as part of LeanKloud Task',
    authorizations= authorizations
)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'WRITE-API-KEY' in request.headers:
            if request.headers['WRITE-API-KEY'] == 'WRITEAPIKEY':
                token = request.headers['WRITE-API-KEY']
            else:
                return {'message': 'Wrong token. Authorization rejected.'}, 401
        else:
            return {'message': 'Not Authorized. Enter Write token'}, 401
        return f(*args, **kwargs)
    return decorated
                

ns = api.namespace('todos', description='TODO app operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'dueby': fields.Date(required=True, description='The task due date'),
    'status': fields.String(required=True, description='The status of the task')
})



class TodoDAO(object):
    def __init__(self):
        self.counter = 0
    
    def addTask(self, task, dueby, status):
        self.counter += 1
        cur = mydb.cursor()
        query = 'insert into todos values (%s, %s, %s, %s)'
        val =  (self.counter, task, dueby, status)
        cur.execute(query, val)
        mydb.commit()
    


    def get(self, id):
        cur = mydb.cursor()
        query = 'select * from todos where id = %s'
        val = (id,)
        cur.execute(query, val)
        res = cur.fetchall()
        if len(res) == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))
        else:
            return {'id': res[0][0], 'task':res[0][1], 'dueby':res[0][2].strftime('%Y-%m-%d'), 'status':res[0][3]}

    def delete(self, id):
        cur = mydb.cursor()
        query = 'delete from todos where id = %s'
        val = (id,)
        cur.execute(query, val)
        mydb.commit()
        if cur.rowcount == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))
    
    def getAll(self):
        cur = mydb.cursor()
        query = 'select * from todos'
        cur.execute(query)
        res = cur.fetchall()
        if len(res) == 0:
            api.abort(404, "No Todo exists".format(id))
        else:
            res = [{'id': res[i][0], 'task':res[i][1], 'dueby':res[i][2].strftime('%Y-%m-%d'), 'status': res[i][3]} for i in range(len(res))]
            return res
    
    def findDue(self, due_by):
        cur = mydb.cursor()
        query = 'select * from todos where dueby = %s and status != %s'
        val = (due_by, "Finished")
        cur.execute(query, val)
        res = cur.fetchall()
        if len(res) == 0:
            api.abort(404, "No overdue")
        else:
            res = [{'id': res[i][0], 'task':res[i][1], 'dueby':res[i][2].strftime('%Y-%m-%d'), 'status': res[i][3]} for i in range(len(res))]
            return res
    
    def overDue(self):
        curdate = datetime.datetime.now().strftime('%Y-%m-%d')
        cur = mydb.cursor()
        query = 'select * from todos where dueby < %s and status != %s'
        val = (curdate, "Finished")
        cur.execute(query, val)
        res = cur.fetchall()
        if len(res) == 0:
            api.abort(404, "No overdue")
        else:
            res = [{'id': res[i][0], 'task':res[i][1], 'dueby':res[i][2].strftime('%Y-%m-%d'), 'status': res[i][3]} for i in range(len(res))]
            return res
    
    def finishedTasks(self):
        cur = mydb.cursor()
        query = 'select * from todos where status = %s'
        val = ("Finished",)
        cur.execute(query, val)
        res = cur.fetchall()
        if len(res) == 0:
            api.abort(404, "No Todo exists")
        else:
            res = [{'id': res[i][0], 'task':res[i][1], 'dueby':res[i][2].strftime('%Y-%m-%d'), 'status': res[i][3]} for i in range(len(res))]
            return res
    
    def updateStatus(self, id, status):
        cur = mydb.cursor()
        query = 'update todos set status = %s where id = %s'
        val = (status, id)
        cur.execute(query, val)
        mydb.commit()
        if cur.rowcount == 0:
            api.abort(404, "Todo {} doesn't exist".format(id))


DAO = TodoDAO()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        todos = DAO.getAll()
        return todos

    @ns.doc('create_todo', security='apikey')
    @token_required
    @ns.response(204, 'Todo added')
    @ns.param('task', 'The task to be done')
    @ns.param('status', 'Status of the task (Not Started, In Process, Finished)',enum=["Not Started", "In Process", "Finished"])
    @ns.param('due_by', "The task's due date")
    def post(self):
        '''Add a new task'''
        task = request.values.get('task')
        status = request.values.get('status')
        due_by = request.values.get('due_by')
        DAO.addTask(task, due_by, status)
        return '', 204


@ns.route('/todo')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch a given task'''
        id = int(request.values.get('id'))
        return DAO.get(id)

    @ns.doc('delete_todo', security='apikey')
    @ns.response(204, 'Todo deleted')
    @token_required
    def delete(self):
        '''Delete a task given its identifier'''
        id = int(request.values.get('id'))
        DAO.delete(id)
        return '', 204

@ns.route('/due')
@ns.response(404, 'Todo not found')
@ns.param('due_by', 'The due date')
class Due(Resource):
    @ns.doc('todo_due')
    @ns.marshal_list_with(todo)
    def get(self):
        '''Find a todo with given due date'''
        due_by = request.values.get('due_by')
        return DAO.findDue(due_by)

@ns.route('/status')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The id of the task')
@ns.param('status', 'Status to be updated', enum=["Not Started", "In Process", "Finished"])
class UpdateTask(Resource):
    @ns.doc('status_update', security='apikey')
    @ns.response('204', 'Todo updated')
    @token_required
    def post(self):
        id = int(request.values.get('id'))
        status = request.values.get('status')
        DAO.updateStatus(id, status)
        return '', 204

@ns.route('/overdue')
@ns.response(404, 'Todo not found')
class OverDue(Resource):
    @ns.doc('todo_overdue')
    @ns.marshal_list_with(todo)
    def get(self):
        '''Find all todos which are overdue from current date'''
        return DAO.overDue()

@ns.route('/finished')
@ns.response(404, 'Todo not found')
class Finished(Resource):
    @ns.doc('finished_todo')
    @ns.marshal_list_with(todo)
    def get(self):
        '''Find all todos which are finished'''
        return DAO.finishedTasks()




if __name__ == "__main__":
    api_main.run(debug=True)
