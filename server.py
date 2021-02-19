# Run with "python server.py"
import jwt
import bottle

from bottle import run, route,template, request, auth_basic, response
from peewee import *
from marshmallow import Schema, fields, ValidationError

# Start your code here, good luck (: ...

db = SqliteDatabase('notas.db')

class User(Model):
    user_id = PrimaryKeyField()
    username = CharField()
    password = CharField()

    class Meta:
        database = db # This model uses the "notas.db" database.

class Grade(Model):
    grade_id = PrimaryKeyField()
    user = ForeignKeyField(User, to_field="user_id")
    name = CharField()
    description = CharField()

    class Meta:
        database = db # This model uses the "notas.db" database.


class GradeSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()

    class Meta:
        strict = True

class UserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    class Meta:
        strict = True

def initialize_db():
    db.connect()
    db.create_tables([User,Grade], safe = True)
    db.close()

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

@route('/register',method='POST')
def register():
    initialize_db()
    username = request.forms.get('username')
    password = request.forms.get('password')
    try:
        result = UserSchema().load({"username":username,"password":password})
        user = User(username=username,password=password)
        user.save()
        return {
            "ok":"se registro correctamente"
        }
    except ValidationError as err:
        return err.messages


def is_authenticated_user(username, password):
    user = User.get(User.username == 'luis', User.password == 'admin123')
    if user:
        return True
    else:
        return False

    
@route('/login',method=['OPTIONS','POST'])
@enable_cors
def do_login():
    response.headers['Content-type'] = 'application/json'
    username = request.forms.get('username')
    password = request.forms.get('password')
    user = User.get(User.username == username, User.password == password)
    key = "secret"
    if user:
        encoded = jwt.encode({"user": user.username, "password": user.password,"ok":True}, key, algorithm="HS256")
        return encoded
    else:
        encoded = jwt.encode({"ok":False}, key, algorithm="HS256")
        return encoded
    



@route('/add',method=['OPTIONS','POST'])
#@enable_cors
def create():
    initialize_db()
    response.headers['Content-type'] = 'application/json'
    name = request.forms.get('name')
    description = request.forms.get('description')
    username = request.forms.get('username')
    password = request.forms.get('password')
    user = User.get(User.username==username,User.password==password)
    try:
        result = GradeSchema().load({"name":name,"description":description})
        grade = Grade.create(user=user.user_id,name=name,description=description)
        return {
            'ok':True
        }
    except ValidationError as err:
        return err.messages
    
@route('/list',method=['OPTIONS','GET'])
@enable_cors
#@auth_basic(is_authenticated_user)
def listar():
    initialize_db()
    response.headers['Content-type'] = 'application/json'
    data = []
    for grade in Grade.select():
        data.append(grade)
    schema = GradeSchema(many=True)
    result = schema.dump(data)
    if is_authenticated_user('luis','admin123'):
        return {'response': result.data}
    else:
        return {'response':'no estas autenticado'}

run(host='localhost', port=8000, reloader= True, debug=True)