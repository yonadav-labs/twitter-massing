from flask import Blueprint, current_app
user_routes = Blueprint('user_routes', __name__, url_prefix='/user')

import time
import datetime

from .account import *
from .profile import *
from project import twitter_connection
from twitter import Twitter, OAuth, TwitterHTTPError


@user_routes.route('/findUsers', methods=['POST'])
def findUsers():
    result = {}
    json_data = request.json
    cursor = -1
    users = []
    loop_threshold = 26 # max 127.4k
    
    try:
        while cursor != 0 and loop_threshold > 0:
            start_time = datetime.datetime.now()
            results = twitter_connection.friends.ids(screen_name=json_data["screen_name"], cursor=cursor)
            cursor = results['next_cursor']
            loop_threshold = loop_threshold -1
            current_app.logger.info(str(len(results['ids'])))

            for n in range(0, len(results["ids"]), 100):
                ids = results["ids"][n:n + 100]
                subquery = twitter_connection.users.lookup(user_id=ids)
                for user in subquery:

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
                print len(users), '$#$#$#$#$#$#$#$#'

            # mechanism for avoiding rate limit for ids
            elapsed = (datetime.datetime.now() - start_time).seconds
            if elapsed < 61 and cursor:
                print cursor, 61-elapsed, '############'
                time.sleep(61-elapsed)

    except TwitterHTTPError as api_error:
        print api_error, '@@@@@@@@@@@@@@'
        #'rate limit exceeded'

    result['users'] = users
    return jsonify({'result': result})
