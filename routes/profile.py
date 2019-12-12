
import json
from flask import Blueprint, request
from flask_api import status
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.user import User
from util.error import UNKNOWN_USER
from util.database import db

Profile = Blueprint('Profile', __name__)


@Profile.route('/profile', methods=['GET'])
@jwt_required
def profile():
    """Gets all the profile data.
    """
    user_id = get_jwt_identity()
    target_user = User.query.filter_by(id=user_id).first()

    if target_user is None:
        return UNKNOWN_USER

    return json.dumps({k:v for k, v in target_user.__dict__.items() if k in (
        'name', 'mail', 'flat_size', 'inhabitants', 'group_id')}), status.HTTP_200_OK


@Profile.route('/profile', methods=['PUT'])
@jwt_required
def put_profile():
    """Changes the profile to the given values.
    :param int flatSize: The user's new flat size.
    :param str inhabitants: The flat's new inhabitants of the user.
    :param int name: The user's new name.
    """
    user_id = get_jwt_identity()
    target_user = User.query.filter_by(id=user_id).first()

    if target_user is None:
        return UNKNOWN_USER

    j = request.get_json(force=True)
    target_user.flat_size = float(j['flatSize'])
    target_user.inhabitants = int(j['inhabitants'])
    target_user.name = j['name']

    db.session.commit()

    return '', status.HTTP_200_OK
