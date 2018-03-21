from flask import Blueprint
admin_routes = Blueprint('admin_routes', __name__, url_prefix='/admin')

from .user import *
# from .deck import *
# from .profile import *
