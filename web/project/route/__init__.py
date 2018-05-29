from flask import Blueprint
from flask import request, jsonify, session

from project import app, bcrypt
from project.models import User

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    return app.send_static_file('index.html')

@routes.route('/info')
def info():
    return app.send_static_file('info.html')

@routes.route('/login', methods=['POST'])
def login():
    json_data = request.json
    user = User.query.filter_by(username=json_data['name']).first()
    if user and bcrypt.check_password_hash(
            user.password, json_data['password']):
        session['logged_in'] = True
        sesuser = {'name': user.username, 'id': user.id, 'admin': user.admin, 'account_limit' : user.account_limit}
        session['user'] = sesuser
        status = True
        data = {'status': status, 'user': sesuser};
    else:
        status = False
        data = {'status': status};
    return jsonify({'result': data})


@routes.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({'result': 'success'})


@routes.route('/status')
def status():
    if session.get('logged_in') and session.get('user'):
        if session['logged_in'] and session['user']:
            status = True
            user = session['user']
            data = {'status': status, 'user': user};
    else:
        status = False
        data = {'status': status};
    return jsonify({'result': data})
