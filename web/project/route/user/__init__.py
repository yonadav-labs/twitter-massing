from flask import Blueprint, current_app
user_routes = Blueprint('user_routes', __name__, url_prefix='/user')

import time
import datetime

from .account import *
from .profile import *

from project import twitter_connection
from project import db
from project.models import Following, Pool

from twitter import Twitter, OAuth, TwitterHTTPError
from flask import session

@user_routes.route('/stopFetching', methods=['POST'])
def stopFetching():
    # print session, '########### 2'
    session['fetching'] = False
    # print session, '########### 3'
    return jsonify({'result': 'success'})

@user_routes.route('/getFetchList', methods=['POST'])
def getFetchList():
    plid = request.json.get('id')
    fetch_list = Pool.query.get(plid)
    filters = fetch_list.last_followed.split(',')
    result = {
        'screen_name': fetch_list.listname,
        'followings_count': filters[0],
        'followers_count': filters[1],
        'likes_count': filters[2],
        'tweets_count': filters[3]
    }
    result['users'] = [{ 'screen_name': ii.name } for ii in Following.query.filter_by(poolid=plid).all()]
    return jsonify({'result': result})

@user_routes.route('/findUsers', methods=['POST'])
def findUsers():
    result = {}
    json_data = request.json

    cursor = -1
    users = []
    loop_threshold = 26 # max 127.4k
    # set fetching flag
    fetching = True
    # print session, '########### 0'
    session['fetching'] = fetching
    # print session, '########### 1'
    last_followed = '{},{},{},{}'.format(json_data['followings_count'], 
                                         json_data['followers_count'], 
                                         json_data['likes_count'], 
                                         json_data['tweets_count'])

    try:
        target = twitter_connection.users.lookup(screen_name=json_data["screen_name"])
        pool = Pool(accountid=json_data['accountId'], 
                    listname=json_data["screen_name"],
                    last_followed=last_followed,
                    started_on=datetime.datetime.now(),
                    type='Fetching',
                    total_count=min(target[0]['friends_count'], 125000))
        db.session.add(pool)
        db.session.commit()

        while cursor != 0 and loop_threshold > 0 and fetching:
            start_time = datetime.datetime.now()
            results = twitter_connection.friends.ids(screen_name=json_data["screen_name"], cursor=cursor)
            cursor = results['next_cursor']
            loop_threshold = loop_threshold -1
            current_app.logger.info(str(len(results['ids'])))

            for n in range(0, len(results["ids"]), 100):
                # check status of fetching
                fetching = session.get('fetching')
                # print session, '@@@@@@@@@@@@@@@@@'
                if not fetching:
                    break

                ids = results["ids"][n:n + 100]
                subquery = twitter_connection.users.lookup(user_id=ids)
                for user in subquery:
                    # check threshold
                    if len(users) == 125000:
                        break

                    followings = user['friends_count']
                    followers = user['followers_count']
                    likes = user['favourites_count']
                    tweets = user['statuses_count']

                    if (followings >= int(json_data['followings_count']) and
                                followers >= int(json_data['followers_count']) and
                                likes >= int(json_data['likes_count']) and
                                tweets >= int(json_data['tweets_count'])):
                        tmpuser = {}
                        tmpuser['id'] = user['id']
                        tmpuser['name'] = user['name']
                        tmpuser['screen_name'] = user['screen_name']
                        tmpuser['location'] = user['location']

                        users.append(tmpuser)
                        # store in db
                        follow = Following(poolid=pool.id, name=user['screen_name'], status=-2)
                        db.session.add(follow)

                Pool.query.filter_by(id=pool.id).update({'progress': len(users)})
                db.session.commit()
                print len(users), '$#$#$#$#$#$#$#$#'

            # mechanism for avoiding rate limit for ids
            elapsed = (datetime.datetime.now() - start_time).seconds
            if elapsed < 61 and cursor:
                time.sleep(61-elapsed)

    except TwitterHTTPError as api_error:
        print api_error, '@@@@@@@@@@@@@@'
        #'rate limit exceeded'

    Pool.query.filter_by(id=pool.id).update({'complete_status': True})
    db.session.commit()
    # reset fetching flag
    # session['fetching'] = False    
    result['users'] = users
    return jsonify({'result': result})
