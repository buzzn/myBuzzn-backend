from functools import wraps
from flask import redirect
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.group import Group
from models.user import User
from util.database import db


def login_required(fn):
    """ Wraps a function and injects a login check before each call. Redirects
    to the login page if the current user is not logged in.
    :param fn: the function to wrap.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        target_user = User.query.filter_by(id=user_id).first()
        if target_user is None:
            return redirect('/admin/login', code=403)
        return fn(*args, **kwargs)
    return wrapper


def get_parameters():
    """ Get user and group parameters for the current logged-in user. """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return None, None
    group = db.session.query(Group).filter_by(id=user.group_id).first()
    if group is None:
        return None, None
    return user, group
