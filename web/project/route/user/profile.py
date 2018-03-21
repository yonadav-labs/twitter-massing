import csv

from flask import jsonify, request

from project import db
from project.models import Follow_Schedule, UnFollow_Schedule, Following, Pool
from project.others import allowed_file, restart_celery_beat
from . import user_routes


@user_routes.route('/getFollowSchedules', methods=['POST'])
def getFollowSchedules():
    result = {}
    json_data = request.json
    show_keys = ['id', 'account_id', 'start_date', 'start_time', 'end_time', 'max_follows']
    schedules = Follow_Schedule.query.filter_by(accountid=json_data['accountId']).all()
    result['status'] = 1
    result['schedules'] = [schedule.to_dict(show=show_keys) for schedule in schedules]
    return jsonify({'result': result})


@user_routes.route('/addFollowSchedule', methods=['POST'])
def addFollowSchedule():
    result = {}
    json_data = request.json
    schedule = Follow_Schedule.query.filter_by(accountid=json_data['accountId'], start_time=json_data['starttime'],
                                               end_time=json_data['endtime']).first()
    if (schedule):
        result['status'] = 0
        result['msg'] = 'Follow schedule is existed'
    else:
        try:
            schedule = Follow_Schedule(
                accountid=json_data['accountId'],
                start_time=json_data['starttime'],
                end_time=json_data['endtime'],
                max_follows=json_data['maxFollows']
            )
            db.session.add(schedule)
            db.session.commit()
            # restart_celery_beat()
            result['status'] = 1
            result['msg'] = 'Succefully added follow schedule.'
        except:
            result['status'] = -1
            result['msg'] = 'Occured error in db session.'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/delFollowSchedule', methods=['POST'])
def delFollowSchedule():
    result = {}
    json_data = request.json
    schedule = Follow_Schedule.query.filter_by(id=json_data['id']).first()
    if (schedule):
        try:
            db.session.delete(schedule)
            db.session.commit()
            # restart_celery_beat()
            result['status'] = 1
            result['msg'] = 'Succefully deleted Follow Schedule.'
        except:
            result['status'] = 0
            result['msg'] = 'Occured error in db session.'

    else:
        result['status'] = 0
        result['msg'] = 'Selected follow schedule is not existed'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/getUnFollowSchedules', methods=['POST'])
def getUnFollowSchedules():
    result = {}
    json_data = request.json
    show_keys = ['id', 'account_id', 'start_date', 'start_time', 'end_time', 'max_unfollows']
    schedules = UnFollow_Schedule.query.filter_by(accountid=json_data['accountId']).all()
    result['status'] = 1
    result['schedules'] = [schedule.to_dict(show=show_keys) for schedule in schedules]
    return jsonify({'result': result})


@user_routes.route('/addUnFollowSchedule', methods=['POST'])
def addUnFollowSchedule():
    result = {}
    json_data = request.json
    schedule = UnFollow_Schedule.query.filter_by(accountid=json_data['accountId'], start_time=json_data['starttime'],
                                                 end_time=json_data['endtime']).first()
    if (schedule):
        result['status'] = 0
        result['msg'] = 'Unfollow schedule is existed'
    else:
        try:
            schedule = UnFollow_Schedule(
                accountid=json_data['accountId'],
                start_time=json_data['starttime'],
                end_time=json_data['endtime'],
                max_unfollows=json_data['maxUnFollows'],
                option=json_data['option']
            )
            db.session.add(schedule)
            db.session.commit()
            # restart_celery_beat()
            result['status'] = 1
            result['msg'] = 'Succefully added unfollow schedule.'
        except:
            result['status'] = -1
            result['msg'] = 'Occured error in db session.'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/delUnFollowSchedule', methods=['POST'])
def delUnFollowSchedule():
    result = {}
    json_data = request.json
    schedule = UnFollow_Schedule.query.filter_by(id=json_data['id']).first()
    if (schedule):
        try:
            db.session.delete(schedule)
            db.session.commit()
            # restart_celery_beat()
            result['status'] = 1
            result['msg'] = 'Succefully deleted Unfollow Schedule.'
        except:
            result['status'] = -1
            result['msg'] = 'Occured error in db session.'

    else:
        result['status'] = 0
        result['msg'] = 'Selected unfollow schedule is not existed'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/getLists', methods=['POST'])
def getLists():
    result = {}
    json_data = request.json
    show_keys = ['id', 'account_id', 'added_on', 'listname', 'started_on', 'progress', 'last_followed',
                 'complete_status', 'total_count']
    pools = Pool.query.filter_by(accountid=json_data['accountId']).all()
    result['status'] = 1
    result['lists'] = [pool.to_dict(show=show_keys) for pool in pools]
    return jsonify({'result': result})


@user_routes.route('/uploadCSVList', methods=['POST'])
def uploadCSVList():
    result = {}
    accountId = request.form['accountId']
    listname = request.form['listname']
    total_count = 0
    pool = Pool.query.filter_by(accountid=accountId, listname=listname).first()
    if (pool):
        result['status'] = 0
        result['msg'] = 'List name is existed'
        return jsonify({'result': result})
    if 'file' not in request.files:
        result['status'] = 0
        result['msg'] = 'No selected file'
        return jsonify({'result': result})
    file = request.files['file']  # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        result['status'] = 0
        result['msg'] = 'No selected file'
        return jsonify({'result': result})
    if file and allowed_file(file.filename):
        pool = Pool(
            accountid=accountId,
            listname=listname
        )
        db.session.add(pool)
        db.session.commit()
        listreader = csv.reader(file, delimiter=' ', quotechar='|')
        for row in listreader:
            if (row[0][0] != '@'):
                continue
            total_count = total_count + 1
            follow = Following(
                poolid=pool.id,
                name=row[0]
            )
            db.session.add(follow)
        Pool.query.filter_by(id=pool.id).update({'total_count': total_count})
        db.session.commit()
        restart_celery_beat()
        result['status'] = 1
        result['msg'] = 'File uploaded successfully'
    else:
        result['status'] = 0
        result['msg'] = 'Something went wrong.'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/uploadList', methods=['POST'])
def uploadList():
    print '###############'
    result = {}
    json_data = request.json
    accountId = json_data['accountId']
    listname = json_data['listname']
    listusers = json_data['listusers']

    pool = Pool.query.filter_by(accountid=accountId, listname=listname).first()
    if (pool):
        result['status'] = 0
        result['msg'] = 'List name is existed'
        return jsonify({'result': result})

    if len(listusers) < 1:
        result['status'] = 0
        result['msg'] = 'No selected users'
        return jsonify({'result': result})

    pool = Pool(
        accountid=accountId,
        listname=listname
    )
    db.session.add(pool)
    db.session.commit()

    for user in listusers:
        follow = Following(
            poolid=pool.id,
            name=user['screen_name']
        )
        db.session.add(follow)
    total_count = len(listusers)
    Pool.query.filter_by(id=pool.id).update({'total_count': total_count})
    db.session.commit()
    # restart_celery_beat()
    result['status'] = 1
    result['msg'] = 'Users uploaded successfully'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/delList', methods=['POST'])
def delList():
    result = {}
    json_data = request.json
    pool = Pool.query.filter_by(id=json_data['id']).first()
    if (pool):
        try:
            followings = Following.query.filter_by(poolid=pool.id).all()
            for following in followings:
                db.session.delete(following)
            db.session.commit()
            db.session.delete(pool)
            db.session.commit()
            result['status'] = 1
            result['msg'] = 'Succefully deleted List.'
            restart_celery_beat()
        except:
            result['status'] = 0
            result['msg'] = 'Occured error in db session.'
    else:
        result['status'] = 0
        result['msg'] = 'Selected list is not existed'
    db.session.close()
    return jsonify({'result': result})
