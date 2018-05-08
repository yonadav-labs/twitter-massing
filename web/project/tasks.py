import os
import time
import tweepy
import random
import datetime

from datetime import timedelta
from celery.schedules import crontab
from celery.signals import task_prerun, task_postrun

from project import app, db, celery
from project.models import User, Account, Pool, Following
from twitter import Twitter, OAuth, TwitterHTTPError
from sqlalchemy import func
from subprocess import call

@celery.task()
def celery_restart_beat():
    curfilePath = os.path.abspath(__file__)
    curDir = os.path.abspath(
        # this will return current directory in which python file resides.
        os.path.join(curfilePath, os.pardir))  
    parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
    script_path = parentDir + "/run_restart_celery_beat.sh"
    call(["bash",script_path])

@celery.task()
def follow_task(accountId, max_follows, detail):
    account = Account.query.filter_by(id=accountId).first()
    if (account):
        pool = Pool.query.filter_by(accountid=accountId, complete_status=False) \
                         .order_by(Pool.id.asc()).first()
        if(pool):
            twitter_connection = Twitter(auth=OAuth(account.oauth_token,
                                                    account.oauth_secret,
                                                    app.config["CONSUMER_KEY"],
                                                    app.config["CONSUMER_SECRET"]))
            followings = Following.query.filter_by(poolid=pool.id, status=-1) \
                                        .order_by(Following.id.asc()) \
                                        .limit(max_follows).all()
            
            last_followed = auto_follow(twitter_connection=twitter_connection, followings=followings, detail=detail)
            follows = db.session.query(func.count(Following.id)).filter(Following.status == 1, Following.poolid == pool.id).scalar()
            Pool.query.filter_by(id=pool.id).update({'progress': follows})
            db.session.commit()

            if last_followed == "meet follow limit":
                Account.query.filter_by(id=accountId).update({'follow_schedule_status': False})
                db.session.commit()
                celery_restart_beat.delay()
            elif last_followed:
                Pool.query.filter_by(id=pool.id).update({'last_followed': last_followed })
                db.session.commit()

            if (pool.started_on == None):
                now_time = datetime.datetime.now()
                Pool.query.filter_by(id=pool.id).update({'started_on': now_time})
                db.session.commit()

            followings = db.session.query(func.count(Following.id)).filter(Following.poolid == pool.id, Following.status == -1).scalar()
            if (followings < 1):
                Pool.query.filter_by(id=pool.id).update({'complete_status': True})
                db.session.commit()
                print 'following task is done.'
                celery_restart_beat.delay()
        else:
            print 'there are no following task.'
    db.session.close()

def auto_follow(twitter_connection, followings, detail):
    print '============== START ============ ( {} )'.format(detail)
    last_followed = None
    for following in followings:
        try:
            twitter_connection.friendships.create(screen_name=following.name, follow=False)
            Following.query.filter_by(id=following.id).update({'status': 1})
            last_followed = following.name
        except TwitterHTTPError as api_error:
            print '##########', api_error, '########## FOLLOW', detail
            # quit on rate limit errors
            if "unable to follow more people at this time" in str(api_error).lower():
                print("You are unable to follow more people at this time. "
                      "Wait a while before running the bot again or gain "
                      "more followers.")
                return "meet follow limit"
            # don't print "already requested to follow" errors - they're frequent
            if "already requested to follow" in str(api_error).lower() or 'user must be age screened to perform this action' in str(api_error).lower():
                Following.query.filter_by(id=following.id).update({'status': 1})
                last_followed = following.name
                print 'already followed user %s' % following.name
            elif "cannot find specified user" in str(api_error).lower() or "blocked from following this account" in str(api_error).lower():
                Following.query.filter_by(id=following.id).update({'status': 0})
                print 'Cannot find user or blocked from following this account %s' % following.name
            else:
                print api_error
    db.session.commit()
    print '--------------  END  -------------- ( {} )'.format(detail)
    return last_followed


@celery.task()
def unfollow_task(accountId, max_unfollows, detail):
    account = Account.query.filter_by(id=accountId).first()
    if (account):
        twitter_connection = Twitter(auth=OAuth(account.oauth_token,
                                                account.oauth_secret,
                                                app.config["CONSUMER_KEY"],
                                                app.config["CONSUMER_SECRET"]))
        unfollows = auto_unfollow(twitter_connection=twitter_connection, max_unfollows=max_unfollows, detail=detail)


def auto_unfollow(twitter_connection, max_unfollows, detail):
    print '============== START ============ ( {} )'.format(detail)
    try:
        following = twitter_connection.friends.ids()["ids"]
    except TwitterHTTPError as api_error:
        print '##########', api_error, '########## UNFOLLOW', detail
        following = []

    for user_id in following:
        try:
            twitter_connection.users.lookup(user_id=user_id)
            twitter_connection.friendships.destroy(user_id=user_id)
            break
        except TwitterHTTPError as api_error:
            print '##########', api_error, '########## UNFOLLOW'
    print '------------- END ------------- ( {} )'.format(detail)
    return 'unfollows'


@celery.task()
def like_tweets(accountId, detail):
    print '============== START ============ ( {} )'.format(detail)
    account = Account.query.filter_by(id=accountId).first()
    twitter_connection = Twitter(auth=OAuth(account.oauth_token,
                                            account.oauth_secret,
                                            app.config["CONSUMER_KEY"],
                                            app.config["CONSUMER_SECRET"]))

    auth = tweepy.OAuthHandler(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
    auth.set_access_token(account.oauth_token, account.oauth_secret)
    api = tweepy.API(auth)

    num_accounts = random.randint(5, 8)
    followers = twitter_connection.followers.ids(screen_name=account.screenname)
    accounts = random.sample(followers['ids'], num_accounts)
    num_tweets = int(25/len(accounts))
    tweets = []

    for account in accounts:
        try:
            tweets_ = api.user_timeline(id=account, count=num_tweets)
            tweets = tweets + [ii.id for ii in tweets_]
        except Exception as e:
            pass

    for tweet in random.sample(tweets, random.randint(2, 10)):
        try:
            api.create_favorite(tweet)
        except Exception as e:
            pass

    print '------------- END ------------- ( {} )'.format(detail)
    return 'unfollows'


@celery.on_after_configure.connect
def configure_workers(sender, **kwargs):
    celery.control.purge()
    users = User.query.filter_by(admin=False).all()
    for user in users:
        accounts = Account.query.filter_by(userid=user.id).all()
        for account in accounts:
            pool = Pool.query.filter_by(accountid=account.id, complete_status=False).order_by(Pool.id.asc()).first()
            if (account.follow_schedule_status and pool):
                name = 'Follow task for {} ({}) on {}'.format(account.fullname, account.id, pool.listname)
                print name
                sender.add_periodic_task(
                            88.0,
                            follow_task.s(accountId=account.id, max_follows=1, detail=name), name=name
                        )

            if (account.unfollow_schedule_status):
                name = 'Unfollow task for {} ({})'.format(account.fullname, account.id)
                print name
                ss = sender.add_periodic_task(
                    89.0,
                    unfollow_task.s(accountId=account.id, max_unfollows=1, detail=name),
                    name=name
                )

            if (account.activity):
                name = 'Activity task for {} ({})'.format(account.fullname, account.id)
                print name
                ss = sender.add_periodic_task(
                    300,
                    # 24 * 60 * 60,
                    like_tweets.s(accountId=account.id, detail=name),
                    name=name
                )
