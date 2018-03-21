from flask import Blueprint, current_app
user_routes = Blueprint('user_routes', __name__, url_prefix='/user')

from .account import *
from .profile import *
from project import twitter_connection


@user_routes.route('/findUsers', methods=['POST'])
def findUsers():
    result = {}
    json_data = request.json
    results = twitter_connection.friends.ids(screen_name=json_data["screen_name"])
    users = []
    count = 0

    current_app.logger.info(str(len(results['ids'])))

    for n in range(0, len(results["ids"]), 100):
        ids = results["ids"][n:n + 100]
        subquery = twitter_connection.users.lookup(user_id=ids)
        for user in subquery:

            followings = user['friends_count']
            followers = user['followers_count']
            likes = user['favourites_count']
            tweets = user['statuses_count']

            if (followings > int(json_data['followings_count']) and
                        followers > int(json_data['followers_count']) and
                        likes > int(json_data['likes_count']) and
                        tweets > int(json_data['tweets_count'])):
                tmpuser = {}
                tmpuser['id'] = user['id']
                tmpuser['name'] = user['name']
                tmpuser['screen_name'] = user['screen_name']
                tmpuser['location'] = user['location']

                users.append(tmpuser)

    result['users'] = users
    return jsonify({'result': result})
