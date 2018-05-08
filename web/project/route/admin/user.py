from flask import request, jsonify
from project import db, bcrypt
from project.models import User, Account

from . import admin_routes


@admin_routes.route('/addUser', methods=['POST'])
def addUser():
    result = {}
    json_data = request.json
    user = User(
        username=json_data['name'],
        password=json_data['password'],
        account_limit = json_data['limit']
    )
    try:
        db.session.add(user)
        db.session.commit()
        result['status'] = 1
        result['msg'] = 'Sucessfully registered.'
    except:
        result['msg'] = 'This user is already registered.'
        result['status'] = 0
    db.session.close()
    return jsonify({'result': result})


@admin_routes.route('/delUser', methods=['POST'])
def delUser():
    result = {}
    user_id = request.json['user_id']

    try:        
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        result['status'] = 1
        result['msg'] = 'Sucessfully deleted.'
    except Exception as e:
        print e
        result['status'] = 0
        result['msg'] = 'The user does not exist.'
    db.session.close()
    return jsonify({'result': result})


@admin_routes.route('/changePass', methods=['POST'])
def changePass():
    result = {}
    json_data = request.json
    user = User.query.filter_by(username='admin').first()
    if user and bcrypt.check_password_hash(
            user.password, json_data['oldpass']):
        newpass = bcrypt.generate_password_hash(json_data['newpass'])
        User.query.filter_by(username='admin').update({"password": newpass})
        db.session.commit()
        result['status'] = 1
        result['msg'] = 'Succefully changed password.'
    else:
        result['status'] = -1
        result['msg'] = 'Incorrect password.'
    return jsonify({'result': result})


@admin_routes.route('/listUsers', methods=['POST'])
def listUsers():
    result = {}
    users = User.query.filter_by(admin=False).all()
    ret_data = []
    for user in users:
        accounts = Account.query.filter_by(userid=user.id).all()
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['registered_on'] = user.registered_on
        user_data['account_limit'] = user.account_limit
        if (len(accounts) > 0):
            user_data['accounts'] = [account.to_dict(show=['id','userid','screenname','followings','followers','fullname','description', 'avatar_url']) for account in accounts]
        else:
            user_data['accounts'] = []
        ret_data.append(user_data)
    result['status'] = 1
    result['users'] = ret_data

    return jsonify({'result': result})
