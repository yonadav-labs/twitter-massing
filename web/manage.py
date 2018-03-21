# manage.py
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from project import app, db
from project.models import User
from project.config import BaseConfig

app.config.from_object(BaseConfig)
migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)

#
@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()
#
# @manager.command
# def drop_db():
#     """Drops the db tables."""
#     db.drop_all()
#
#
@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(
        User(username='admin',
             password='admin',
             admin=True,
             account_limit=3))
    db.session.commit()
#
# @manager.command
# def create_data():
#     """Creates sample data."""
#     pass


if __name__ == '__main__':
    manager.run()
