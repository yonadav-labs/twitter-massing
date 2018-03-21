import os
from project import app
from project.models import User, Account, Follow_Schedule, UnFollow_Schedule
from project.tasks import celery, follow_task, unfollow_task,celery_restart_beat
from subprocess import call

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def restart_celery_beat():
    celery_restart_beat.delay()

# @app.before_first_request
def configure_workers():
    users = User.query.filter_by(admin=False).all()
    for user in users:
        accounts = Account.query.filter_by(userid=user.id).all()
        for account in accounts:
            if (account.follow_schedule_status):
                following_schedule = Follow_Schedule.query.filter_by(accountid=account.id).order_by(Follow_Schedule.start_time.asc()).all()
                if(following_schedule):
                    for schedule in following_schedule:
                        expires = (schedule.end_time - schedule.start_time).total_seconds()
                        month = schedule.start_time.month
                        day = schedule.start_time.day
                        hour = schedule.start_time.hour
                        minute = schedule.start_time.minute
                        max_follows = schedule.max_follows
                        name = 'follow_%s-%s' %(month,day)
                        print ('add_follow_periodic_task %s' % name)
                        follow_task(account.id,max_follows=max_follows)
                else:
                    expires = 14400
                    name = 'default_follow_task'
                    print ('add_follow_periodic_task %s' % name)
                    follow_task(account.id, max_follows=max_follows)

            if (account.unfollow_schedule_status):
                unfollowing_schedule = UnFollow_Schedule.query.filter_by(accountid=account.id).all()
                if (unfollowing_schedule):
                    for schedule in unfollowing_schedule:
                        expires = (schedule.end_time - schedule.start_time).total_seconds()
                        month = schedule.start_time.month
                        day = schedule.start_time.day
                        hour = schedule.start_time.hour
                        minute = schedule.start_time.minute
                        max_unfollows = schedule.max_unfollows
                        option = schedule.option
                        name = 'unfollow_%s-%s' % (month, day)
                        print ('add_unfollow_periodic_task %s' % name)
                        unfollow_task(accountId=account.id, max_unfollows=max_unfollows, option=option)