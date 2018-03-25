# project/models.py


import datetime
import json

from project import db, bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Base(db.Model):
    __abstract__ = True

    def to_dict(self, show=None, hide=None, path=None, show_all=None):
        """ Return a dictionary representation of this model.
        """

        if not show:
            show = []
        if not hide:
            hide = []
        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields
        default = []
        if hasattr(self, 'default_fields'):
            default = self.default_fields

        ret_data = {}

        if not path:
            path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                item = '%s%s' % (path, item)
                return item

            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is 'id' or check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    ret_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(item.to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        ))
                else:
                    if self.__mapper__.relationships[key].query_class is not None:
                        ret_data[key] = getattr(self, key).to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        )
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith('_'):
                continue
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                try:
                    ret_data[key] = json.loads(json.dumps(val))
                except:
                    pass

        return ret_data


class User(Base):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    account_limit = db.Column(db.Integer, nullable=False)

    def __init__(self, username, password, account_limit = 3 , admin=False, deck=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.account_limit = account_limit
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.username)


class Account(Base):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, ForeignKey(User.id), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    screenname = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    avatar_url = db.Column(db.String(1024), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    followings = db.Column(db.Integer, nullable=False)
    oauth_token = db.Column(db.String(255), nullable=False)
    oauth_secret = db.Column(db.String(255), nullable=False)
    follow_schedule_status = db.Column(db.Boolean, nullable=False, default=False)
    unfollow_schedule_status = db.Column(db.Boolean, nullable=False, default=False)
    unfollow_schedule_option = db.Column(db.Integer, nullable=False, default=0)
    user = relationship("User")

    def __init__(self, userid, fullname, screenname, description, avatar_url, followers, followings, oauth_token,
                 oauth_secret):
        self.userid = userid
        self.fullname = fullname
        self.screenname = screenname
        self.avatar_url = avatar_url
        self.description = description
        self.followers = followers
        self.followings = followings
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Account {0}>'.format(self.id)


#
# class List(Base):
#     __tablename__ = "lists"
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(255), nullable=False)
#     total_count = db.Column(db.Integer, nullable=False)
#
#     def __init__(self, name, total_count):
#         self.name = name
#         self.total_count = total_count
#
#     def get_id(self):
#         return self.id
#
#     def __repr__(self):
#         return '<List {0}>'.format(self.id)


class Pool(Base):
    __tablename__ = "pools"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accountid = db.Column(db.Integer, ForeignKey(Account.id), nullable=False)
    added_on = db.Column(db.DateTime)
    listname = db.Column(db.String(255), nullable=False)
    started_on = db.Column(db.DateTime)
    progress = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String(50), default="Uploading")
    last_followed = db.Column(db.String(255))
    complete_status = db.Column(db.Boolean, nullable=False, default=False)
    total_count = db.Column(db.Integer, nullable=False, default=0)
    account = relationship("Account")

    def __init__(self, accountid, listname, type='Uploading', last_followed=None, total_count=0, started_on=None):
        self.accountid = accountid
        self.added_on = datetime.datetime.now()
        self.listname = listname
        self.last_followed = last_followed
        self.total_count = total_count
        self.started_on = started_on
        self.type = type

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Pool {0}>'.format(self.id)


class Following(Base):
    __tablename__ = "followings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poolid = db.Column(db.Integer, ForeignKey(Pool.id), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    pool = relationship("Pool")
    status = db.Column(db.Integer, nullable=False, default=-1)

    def __init__(self, poolid, name, status=-1):
        self.poolid = poolid
        self.name = name
        self.status = status

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Following {0}>'.format(self.id)


class Follow_Schedule(Base):
    __tablename__ = "follow_schedule"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accountid = db.Column(db.Integer, ForeignKey(Account.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_follows = db.Column(db.Integer, nullable=False, default=0)
    account = relationship("Account")

    def __init__(self, accountid, start_time, end_time, max_follows):
        self.accountid = accountid
        self.start_time = start_time
        self.end_time = end_time
        self.max_follows = max_follows

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Follow_Schedule {0}>'.format(self.id)


class UnFollow_Schedule(Base):
    __tablename__ = "unfollow_schedule"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accountid = db.Column(db.Integer, ForeignKey(Account.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_unfollows = db.Column(db.Integer, nullable=False, default=0)
    option = db.Column(db.Boolean, nullable=False, default=False)
    account = relationship("Account")

    def __init__(self, accountid, start_time, end_time, max_unfollows, option):
        self.accountid = accountid
        self.start_time = start_time
        self.end_time = end_time
        self.max_unfollows = max_unfollows
        self.option = option

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<UnFollow_Schedule {0}>'.format(self.id)


class MissFollowing(Base):
    __tablename__ = "missfollowings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poolid = db.Column(db.Integer, ForeignKey(Pool.id), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    list = relationship("Pool")

    def __init__(self, listid, name):
        self.listid = listid
        self.name = name

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<MissFollowing {0}>'.format(self.id)
