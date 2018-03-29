import os
import time
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
def follow_task(accountId, max_follows):
    account = Account.query.filter_by(id=accountId).first()
    if (account):
        pool = Pool.query.filter_by(accountid=accountId, complete_status=False).order_by(Pool.id.asc()).first()
        if(pool):
            twitter_connection = Twitter(auth=OAuth(account.oauth_token,
                                                    account.oauth_secret,
                                                    app.config["CONSUMER_KEY"],
                                                    app.config["CONSUMER_SECRET"]))
            followings = Following.query.filter_by(poolid=pool.id, status=-1).order_by(Following.id.asc()).limit(max_follows).all()
            print('start follow task')
            last_followed = auto_follow(twitter_connection=twitter_connection, followings=followings)
            follows = db.session.query(func.count(Following.id)).filter(Following.status == 1, Following.poolid == pool.id).scalar()
            Pool.query.filter_by(id=pool.id).update({'progress': follows})
            db.session.commit()
            if(last_followed != None):
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


@celery.task()
def celery_restart_beat():
    curfilePath = os.path.abspath(__file__)
    curDir = os.path.abspath(
        os.path.join(curfilePath, os.pardir))  # this will return current directory in which python file resides.
    parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
    script_path = parentDir + "/run_restart_celery_beat.sh"
    call(["bash",script_path])



def auto_follow(twitter_connection, followings):
    last_followed = None
    for following in followings:
        try:
            twitter_connection.friendships.create(screen_name=following.name, follow=False)
            Following.query.filter_by(id=following.id).update({'status': 1})
            last_followed = following.name
        except TwitterHTTPError as api_error:
            print '@@@@', api_error, '@@@@@@@@@@@@@@'
            # quit on rate limit errors
            if "unable to follow more people at this time" in str(api_error).lower():
                print("You are unable to follow more people at this time. "
                      "Wait a while before running the bot again or gain "
                      "more followers.")
                return last_followed
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
    return last_followed


def subset(s,k):
    r = set()
    i = 0
    for v in s:
        if(i == k):
            return r
        r.add(v)
        i = i + 1
    return r


@celery.task()
def unfollow_task(accountId, max_unfollows, option):
    account = Account.query.filter_by(id=accountId).first()
    if (account):
        twitter_connection = Twitter(auth=OAuth(account.oauth_token,
                                                account.oauth_secret,
                                                app.config["CONSUMER_KEY"],
                                                app.config["CONSUMER_SECRET"]))
        print('start unfollow task')
        unfollows = auto_unfollow(twitter_connection=twitter_connection, max_unfollows=max_unfollows, option=option)
        # print (unfollows)


def auto_unfollow(twitter_connection, max_unfollows, option):
    # unfollows = 0
    following = set(twitter_connection.friends.ids()["ids"])
    # followers = set(twitter_connection.followers.ids()["ids"])

    # if(max_unfollows == -1):
    #     max_unfollows = len(following)

    # if(option):
    #     not_following_back = following
    # else:
    #     not_following_back = following - followers

    # if(len(not_following_back) > max_unfollows):
    #     not_following_back = subset(not_following_back,max_unfollows)

    # print len(not_following_back)

    user_id = following[0]
    # for user_id in not_following_back:
    try:
        twitter_connection.friendships.destroy(user_id=user_id)
        # unfollows = unfollows + 1
    except TwitterHTTPError as api_error:
        print api_error, '############### unfollow '
    return unfollows


@celery.on_after_configure.connect
def configure_workers(sender, **kwargs):
    celery.control.purge()
    users = User.query.filter_by(admin=False).all()
    for user in users:
        accounts = Account.query.filter_by(userid=user.id).all()
        for account in accounts:
            pool = Pool.query.filter_by(accountid=account.id, complete_status=False).order_by(Pool.id.asc()).first()
            if (account.follow_schedule_status and pool):
                name = 'follow_task per %s minutes' % app.config['TASK_PERIOD_TIME']
                print name
                sender.add_periodic_task(
                            61.0,
                            follow_task.s(accountId=account.id, max_follows=1), name=name
                        )

            if (account.unfollow_schedule_status):
                name = 'unfollow_task per %s minutes at week of day  %s ' % (
                        app.config['TASK_PERIOD_TIME'], app.config['UNFOLLOWING_PERIOD_WEEK'])
                print name
                sender.add_periodic_task(
                    85.0,
                    unfollow_task.s(accountId=account.id, max_unfollows=1, option=account.unfollow_schedule_option),
                    name=name
                )
