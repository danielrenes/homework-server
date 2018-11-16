from functools import wraps

from flask import Blueprint, g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from homework_server import db
from homework_server.models import User

auth_api = Blueprint('auth_api', __name__)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)

@basic_auth.error_handler
def basic_auth_error():
    return '', 401

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return '', 401

@auth_api.route('/token', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})

@auth_api.route('/token', methods=['GET'])
@token_auth.login_required
def check_token():
    return '', 200

@auth_api.route('/token', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204

def check_user(user_type):
    assert issubclass(user_type, User)
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if type(g.current_user) != user_type:
                return '', 403
            return func(*args, **kwargs)
        return inner
    return outer