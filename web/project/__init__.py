# project/__init__.py

from __future__ import print_function

import logging

import flask_oauth
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from twitter import Twitter, OAuth

from config import BaseConfig
from factory import create_celery_app

# config
drivermap = {}

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
logging.basicConfig(filename='error.log')

oauth = flask_oauth.OAuth()

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['CONSUMER_KEY'],
    consumer_secret=app.config['CONSUMER_SECRET']
)

twitter_connection = Twitter(auth=OAuth(
    app.config["OAUTH_TOKEN"],
    app.config["OAUTH_SECRET"],
    app.config["CONSUMER_KEY"],
    app.config["CONSUMER_SECRET"])
)

celery = create_celery_app(app,db)


from others import *
from route import *
from route.admin import *
from route.user import *


def configure_blueprints(blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def init_app():
    """Create a Flask app."""

    blueprints = [
        routes,
        admin_routes,
        user_routes
    ]
    configure_blueprints(blueprints)
    return app


init_app()



if __name__ == "__main__":
    app.run()
