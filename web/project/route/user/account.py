from flask import jsonify, request, redirect, url_for, session, flash

from project import twitter, twitter_connection, db
from project.models import Account, Pool, Following, Follow_Schedule, UnFollow_Schedule
from project.others import restart_celery_beat
from . import user_routes


@user_routes.route('/getAccountsByUserId', methods=['POST'])  # param : userid
def getAccountsByUserId():
    json_data = request.json
    accounts = Account.query.filter_by(userid=json_data['userid']).all()
    return jsonify({'result': [account.to_dict(
        show=['id', 'userid', 'screenname', 'followings', 'followers', 'fullname', 'description', 'avatar_url',
              'follow_schedule_status', 'unfollow_schedule_status','unfollow_schedule_option']) for
        account in accounts]})


@user_routes.route('/getAccountById', methods=['POST'])  # param : userid
def getAccountById():
    json_data = request.json
    account = Account.query.filter_by(id=json_data['id']).first()
    return jsonify({'result': account.to_dict(
        show=['id', 'userid', 'screenname', 'followings', 'followers', 'fullname', 'description', 'avatar_url',
              'follow_schedule_status', 'unfollow_schedule_status','unfollow_schedule_option'])})


@user_routes.route('/changeFollowScheduleStatus', methods=['POST'])  # param : userid
def changeFollowScheduleStatus():
    result = {}
    json_data = request.json
    account = Account.query.filter_by(id=json_data['accountId']).first()
    if(account):
        Account.query.filter_by(id=json_data['accountId']).update({'follow_schedule_status':json_data['follow_schedule_status']})
        db.session.commit()
        restart_celery_beat()
        result['status'] = 1
        result['msg'] = 'Successfully change Follow Schedule status.'
    else:
        result['status'] = 0
        result['msg'] = 'Occured error in change Follow Schedule status.'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/changeUnFollowScheduleStatus', methods=['POST'])  # param : userid
def changeUnFollowScheduleStatus():
    result = {}
    json_data = request.json
    account = Account.query.filter_by(id=json_data['accountId']).first()
    if(account):
        Account.query.filter_by(id=json_data['accountId']) \
                     .update({
                        'unfollow_schedule_status':json_data['unfollow_schedule_status'],
                        'unfollow_schedule_option':json_data['unfollow_schedule_option']})
        db.session.commit()
        restart_celery_beat()
        result['status'] = 1
        result['msg'] = 'Successfully change UnFollow Schedule status.'
    else:
        result['status'] = 0
        result['msg'] = 'Occured error in change UnFollow Schedule status.'
    db.session.close()
    return jsonify({'result': result})


@twitter.tokengetter
def get_twitter_token():
    pass
    # if 'twitter_oauth' in session:
    #     resp = session['twitter_oauth']
    #     return resp['oauth_token'], resp['oauth_token_secret']


@user_routes.route('/addAccount')
def add_account():
    userid = request.args['userid']
    callback_url = url_for('user_routes.oauthorized', userid=userid, next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@user_routes.route('/delAccount', methods=['POST'])
def delAccount():
    result = {}
    json_data = request.json
    try:
        account = Account.query.filter_by(id=json_data['accountId']).first()
        pools = Pool.query.filter_by(accountid=account.id).all()
        for pool in pools:
            followings = Following.query.filter_by(poolid=pool.id)
            for following in followings:
                db.session.delete(following)
            db.session.delete(pool)
        follow_schedules = Follow_Schedule.query.filter_by(accountid=account.id).all()
        for follow_schedule in follow_schedules:
            db.session.delete(follow_schedule)
        unfollow_schedules = UnFollow_Schedule.query.filter_by(accountid=account.id).all()
        for unfollow_schedule in unfollow_schedules:
            db.session.delete(unfollow_schedule)
        db.session.delete(account)
        db.session.commit()
        result['status'] = 1
        result['msg'] = 'Succefully deleted Account.'
    except:
        result['status'] = -1
        result['msg'] = 'Occured error in delete Account.'
    db.session.close()
    return jsonify({'result': result})


@user_routes.route('/twitter/oauthorized')
@twitter.authorized_handler
def oauthorized(resp):
    userid = request.args['userid']
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
        oauth_token = resp['oauth_token']
        oauth_secret = resp['oauth_token_secret']
        screen_name = resp['screen_name']
        user = twitter_connection.users.lookup(screen_name=screen_name)[0]

        if (user):
            fullname = user['name']
            description = user['description']
            avatar_url = user['profile_image_url_https']
            followers = user['followers_count']
            followings = user['friends_count']
            account = Account.query.filter_by(userid=userid, screenname=screen_name).first()
            if (account == None):
                account = Account(
                    userid=userid,
                    fullname=fullname,
                    screenname=screen_name,
                    description=description,
                    avatar_url=avatar_url,
                    followers=followers,
                    followings=followings,
                    oauth_token=oauth_token,
                    oauth_secret=oauth_secret
                )
                db.session.add(account)
                db.session.commit()
                db.session.close()
    return redirect(url_for('routes.index'))
